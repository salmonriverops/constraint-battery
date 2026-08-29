"""Adapter helpers shared by every source adapter.

An adapter is a module in this package that exposes:

    SOURCE_SYSTEM : str
    def build(export_dir: Path, cfg: dict) -> dict[str, list[dict]]

and returns rows keyed by landing table name. Adapters never write to the
database and never read anything under key/.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import datetime, date
from pathlib import Path

LANDING_TABLES = ("work", "resources", "assignments", "locations", "location_travel", "changes")

_TS_FORMATS = (
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
)


def parse_ts(value):
    """Parse a timestamp. Returns None rather than guessing when the value is unusable."""
    if value in (None, "", "null"):
        return None
    if isinstance(value, (datetime, date)):
        return value
    text = str(value).strip()
    for fmt in _TS_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def parse_date(value):
    ts = parse_ts(value)
    return ts.date() if isinstance(ts, datetime) else ts


def parse_int(value):
    if value in (None, "", "null"):
        return None
    try:
        return int(float(str(value).strip()))
    except ValueError:
        return None


def opaque_id(*parts, prefix="", length=12) -> str:
    """A stable, content-free id. Same inputs always give the same id."""
    digest = hashlib.sha256("\x1f".join(str(p) for p in parts).encode("utf-8")).hexdigest()
    return f"{prefix}{digest[:length]}"


def read_table(export_dir: Path, table: str):
    """Read one source table from the export directory.

    Accepts <table>.csv or <table>.json. Returns a list of dicts keyed by column name.
    Returns an empty list when the file is absent, so a partial export still loads.
    """
    stem = export_dir / table
    csv_path = Path(f"{stem}.csv")
    json_path = Path(f"{stem}.json")
    if csv_path.exists():
        with csv_path.open(newline="", encoding="utf-8-sig") as handle:
            return list(csv.DictReader(handle))
    if json_path.exists():
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        return payload["records"] if isinstance(payload, dict) else payload
    return []


def links(value):
    """Normalise a linked-record cell to a list of ids.

    Airtable exports render links as a JSON array of objects, a JSON array of ids,
    or a comma separated string. All three land here.
    """
    if value in (None, "", "null"):
        return []
    if isinstance(value, list):
        out = []
        for item in value:
            if isinstance(item, dict):
                if item.get("id"):
                    out.append(item["id"])
            elif item:
                out.append(str(item))
        return out
    text = str(value).strip()
    if text.startswith("["):
        try:
            return links(json.loads(text))
        except json.JSONDecodeError:
            pass
    if re.fullmatch(r"rec[A-Za-z0-9]{14}(\s*,\s*rec[A-Za-z0-9]{14})*", text):
        return [part.strip() for part in text.split(",")]
    return [part.strip() for part in text.split(",") if part.strip()]


def scalar(value):
    """Normalise a select or lookup cell to a plain string."""
    if value in (None, "", "null"):
        return None
    if isinstance(value, dict):
        return value.get("name") or value.get("id")
    if isinstance(value, list):
        if not value:
            return None
        return scalar(value[0])
    text = str(value).strip()
    if text.startswith("{") or text.startswith("["):
        try:
            return scalar(json.loads(text))
        except json.JSONDecodeError:
            return text
    return text or None


def stamp(rows, source_system, extracted_at):
    """Attach provenance columns to every row that carries them."""
    for row in rows:
        row.setdefault("source_system", source_system)
        row.setdefault("extracted_at", extracted_at)
    return rows
