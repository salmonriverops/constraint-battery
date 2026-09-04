"""Airtable export adapter.

Reads a directory of per-table CSV or JSON files exported from Airtable and
produces rows for the six landing tables. The column map lives in
airtable_map.json so that a change in the export does not need a code change.

This adapter loads operational transaction records only. See extract/README.md
for the denylist and for how the override log is handled.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from . import base
from .denylist import is_answer_key_field

SOURCE_SYSTEM = "airtable"

MAP_PATH = Path(__file__).with_name("airtable_map.json")

# An acknowledgement entry looks like "<label> :: <who> :: <YYYY-MM-DD>".
ACK_ENTRY = re.compile(r"^(?P<label>.*?)\s*::\s*(?P<who>.*?)\s*::\s*(?P<when>\S+)\s*$")


def _rid(row, prefix=""):
    """The stable landing id for a source row."""
    ident = row.get("id") or row.get("Record ID") or row.get("record_id")
    return f"{prefix}{ident}" if ident else None


def _cells(row):
    """Airtable JSON exports nest values under cellValuesByFieldId or fields."""
    for key in ("fields", "cellValuesByFieldId"):
        if isinstance(row.get(key), dict):
            merged = dict(row[key])
            merged["id"] = row.get("id")
            return merged
    return row


def _label_key(label: str) -> str:
    """Normalise an override label so the same rule collapses to one key.

    Record ids embedded in a machine key are stripped, so that
    'dbl-recAAA-mv_recBBB-mv_recCCC' and 'dbl-recDDD-mv_recEEE-mv_recFFF'
    collapse to the same class.
    """
    text = label.strip().lower()
    text = re.sub(r"(mv_|op_)?rec[a-z0-9]{14}", "", text, flags=re.I)
    text = re.sub(r"\d+", "#", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return text.strip() or "unlabelled"


class Adapter:
    def __init__(self, export_dir: Path, extracted_at, reveal_labels=False, profile=None):
        self.dir = Path(export_dir)
        self.extracted_at = extracted_at
        self.reveal_labels = reveal_labels
        self.profile = profile or {}
        self.skipped = []
        self.map = json.loads(MAP_PATH.read_text(encoding="utf-8"))
        self.missing_columns = []   # (source table, column) pairs the export did not carry
        self.label_map = {}         # opaque id -> raw label, written outside git
        self.notes = []

    # -- helpers ---------------------------------------------------------

    def _skip(self, table):
        """True when the active profile does not read this source table at all."""
        if table in (self.profile.get("skip_source_tables") or []):
            if table not in self.skipped:
                self.skipped.append(table)
            return True
        return False

    def _load(self, table):
        rows = [_cells(r) for r in base.read_table(self.dir, table)]
        return rows

    def _get(self, rows, row, table, column):
        """Read a column, recording it once if the export does not carry it."""
        if column is None:
            return None
        if rows and column not in rows[0]:
            entry = (table, column)
            if entry not in self.missing_columns:
                self.missing_columns.append(entry)
            return None
        return row.get(column)

    # -- landing tables --------------------------------------------------

    def work(self):
        out = []
        for spec in self.map["work"]:
            if self._skip(spec["table"]):
                continue
            rows = self._load(spec["table"])
            for row in rows:
                wid = _rid(row, spec.get("id_prefix", ""))
                if not wid:
                    continue
                start = base.parse_ts(self._get(rows, row, spec["table"], spec.get("start_ts")))
                end = base.parse_ts(self._get(rows, row, spec["table"], spec.get("end_ts")))
                if start is None and spec.get("fallback_date"):
                    start = base.parse_ts(self._get(rows, row, spec["table"], spec["fallback_date"]))
                if "work_type_link" in spec:
                    ids = base.links(self._get(rows, row, spec["table"], spec["work_type_link"]))
                    # The linked record id, not its label. The rules table it points at
                    # is denylisted, so only the opaque key crosses the boundary.
                    work_type = ids[0] if ids else None
                else:
                    work_type = base.scalar(self._get(rows, row, spec["table"], spec.get("work_type")))
                if "location_link" in spec:
                    ids = base.links(self._get(rows, row, spec["table"], spec["location_link"]))
                    location = f"lc_{ids[0]}" if ids else None
                else:
                    location = base.scalar(self._get(rows, row, spec["table"], spec.get("location_id")))
                out.append({
                    "work_id": wid,
                    "work_type": work_type,
                    "start_ts": start,
                    "end_ts": end,
                    "location_id": location,
                    "status": base.scalar(self._get(rows, row, spec["table"], spec.get("status"))),
                    "customer_count": base.parse_int(
                        self._get(rows, row, spec["table"], spec.get("customer_count"))),
                    "source_id": row.get("id"),
                })
        return out

    def resources(self):
        out = []
        for spec in self.map["resources"]:
            if self._skip(spec["table"]):
                continue
            rows = self._load(spec["table"])
            for row in rows:
                rid = _rid(row, spec.get("id_prefix", ""))
                if not rid:
                    continue
                kind = spec.get("kind")
                if self.profile.get("collapse_resource_kind"):
                    # A vehicle list exists anywhere. A maintained type taxonomy on top
                    # of it does not, so fall back to the spec's literal kind.
                    kind = kind or spec.get("kind_fallback")
                elif spec.get("kind_column"):
                    kind = base.scalar(
                        self._get(rows, row, spec["table"], spec["kind_column"])) or kind
                out.append({
                    "resource_id": rid,
                    "kind": kind,
                    "name": base.scalar(self._get(rows, row, spec["table"], spec.get("name"))),
                    "home_location_id": base.scalar(
                        self._get(rows, row, spec["table"], spec.get("home_location_id"))),
                    "active_from": None,
                    "active_to": None,
                    "source_id": row.get("id"),
                })
        return out

    def assignments(self, work_index):
        """Explode linked-record columns into one assignment row per resource.

        role is the source column name. It is a free string and no probe branches on it.
        """
        out = []
        for spec in self.map["assignments"]:
            if self._skip(spec["table"]):
                continue
            rows = self._load(spec["table"])
            for row in rows:
                work_ids = []
                if spec.get("work_prefix"):
                    wid = _rid(row, spec["work_prefix"])
                    if wid:
                        work_ids = [wid]
                for column, prefix in (spec.get("work_link") or {}).items():
                    for linked in base.links(self._get(rows, row, spec["table"], column)):
                        work_ids.append(f"{prefix}{linked}")
                for work_id in work_ids:
                    window = work_index.get(work_id, (None, None))
                    for column, prefix in spec["roles"].items():
                        for linked in base.links(self._get(rows, row, spec["table"], column)):
                            resource_id = f"{prefix}{linked}"
                            out.append({
                                "assignment_id": base.opaque_id(
                                    work_id, resource_id, column, prefix="as_"),
                                "resource_id": resource_id,
                                "work_id": work_id,
                                "role": column,
                                "start_ts": window[0],
                                "end_ts": window[1],
                                "source_id": row.get("id"),
                            })
        # One resource can reach the same work through several source tables.
        # Collapse to the first occurrence so assignment_id stays a primary key.
        seen, unique = set(), []
        for row in sorted(out, key=lambda r: (r["assignment_id"], r["role"])):
            if row["assignment_id"] in seen:
                continue
            seen.add(row["assignment_id"])
            unique.append(row)
        return unique

    def locations(self):
        out = []
        for spec in self.map["locations"]:
            if self._skip(spec["table"]):
                continue
            rows = self._load(spec["table"])
            for row in rows:
                lid = _rid(row, spec.get("id_prefix", ""))
                if lid:
                    out.append({
                        "location_id": lid,
                        "name": base.scalar(self._get(rows, row, spec["table"], spec.get("name"))),
                    })
        return out

    def location_travel(self):
        out = []
        for spec in self.map["location_travel"]:
            if self._skip(spec["table"]):
                continue
            rows = self._load(spec["table"])
            for row in rows:
                froms = base.links(self._get(rows, row, spec["table"], spec["from_link"]))
                tos = base.links(self._get(rows, row, spec["table"], spec["to_link"]))
                minutes = base.parse_int(self._get(rows, row, spec["table"], spec.get("minutes")))
                samples = base.parse_int(self._get(rows, row, spec["table"], spec.get("sample_count")))
                if not froms or not tos or minutes is None:
                    continue
                out.append({
                    "from_id": f"{spec['id_prefix']}{froms[0]}",
                    "to_id": f"{spec['id_prefix']}{tos[0]}",
                    "minutes": minutes,
                    "is_estimate": not samples,
                })
        return out

    def changes(self):
        """The override log.

        Each acknowledgement entry is one human saying "this flag is wrong or handled".
        That is a change from flagged to acknowledged, so it lands in changes with
        old_value 'flagged' and new_value 'acknowledged'.

        The label is replaced by an opaque id unless reveal_labels is set, because the
        label is the conflict checker's own rule name and therefore answer-key content.
        The id-to-label map is written outside git so it can be read after matching.
        """
        out = []
        for spec in self.map["changes"]:
            table = spec["table"]
            if self._skip(table):
                continue
            rows = self._load(table)
            column = spec["ack_column"]
            if rows and column not in rows[0]:
                self.missing_columns.append((table, column))
                continue
            if not self.reveal_labels and not is_answer_key_field(column):
                self.notes.append(
                    f"{table}.{column} is mapped as an override log but is not in "
                    f"ANSWER_KEY_FIELDS. Check whether it should be."
                )
            for row in rows:
                raw = row.get(column)
                if not raw:
                    continue
                for line in str(raw).split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    match = ACK_ENTRY.match(line)
                    if match:
                        label, who, when = (match.group("label"),
                                            match.group("who"), match.group("when"))
                    else:
                        label, who, when = line, None, None
                    key = _label_key(label)
                    field = key if self.reveal_labels else base.opaque_id(key, prefix="ovr_")
                    self.label_map.setdefault(field, key)
                    out.append({
                        "change_id": base.opaque_id(
                            _rid(row, spec.get("entity_prefix", "")), field, who, when,
                            prefix="ch_"),
                        "entity_table": "work",
                        "entity_id": _rid(row, spec.get("entity_prefix", "")),
                        "field": field,
                        "old_value": "flagged",
                        "new_value": "acknowledged",
                        "changed_at": base.parse_ts(when),
                        "changed_by": who,
                        "source_id": row.get("id"),
                    })
        seen, unique = set(), []
        for row in sorted(out, key=lambda r: r["change_id"]):
            if row["change_id"] in seen:
                continue
            seen.add(row["change_id"])
            unique.append(row)
        return unique


def build(export_dir: Path, cfg: dict):
    adapter = Adapter(export_dir, cfg["extracted_at"], cfg.get("reveal_labels", False),
                      profile=cfg.get("profile"))
    dropped = set((cfg.get("profile") or {}).get("drop_tables") or [])
    work_rows = adapter.work()
    work_index = {r["work_id"]: (r["start_ts"], r["end_ts"]) for r in work_rows}

    # A dropped table is not built at all, so no work is wasted and no side effect of
    # building it, such as the override label map, is produced.
    builders = {
        "work": lambda: work_rows,
        "resources": adapter.resources,
        "assignments": lambda: adapter.assignments(work_index),
        "locations": adapter.locations,
        "location_travel": adapter.location_travel,
        "changes": adapter.changes,
    }
    tables = {name: ([] if name in dropped else build_one())
              for name, build_one in builders.items()}
    for name, rows in tables.items():
        if name not in ("locations", "location_travel"):
            base.stamp(rows, SOURCE_SYSTEM, cfg["extracted_at"])
    return tables, adapter
