"""Load an export into DuckDB.

Order of operations, and it matters:

  1. Check every file in the export directory against the denylist. Refuse the
     whole run if anything matches. Nothing is read before this passes.
  2. Run the adapter.
  3. Create the landing schema fresh and insert.

The loader never reads anything under key/.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import duckdb

from . import airtable, profiles
from .base import LANDING_TABLES
from .denylist import check_export_dir

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schema" / "001_landing.sql"

ADAPTERS = {"airtable": airtable}

COLUMNS = {
    "work": ["work_id", "work_type", "start_ts", "end_ts", "location_id", "status",
             "customer_count", "source_system", "source_id", "extracted_at"],
    "resources": ["resource_id", "kind", "name", "home_location_id", "active_from",
                  "active_to", "source_system", "source_id", "extracted_at"],
    "assignments": ["assignment_id", "resource_id", "work_id", "role", "start_ts",
                    "end_ts", "source_system", "source_id", "extracted_at"],
    "locations": ["location_id", "name"],
    "location_travel": ["from_id", "to_id", "minutes", "is_estimate"],
    "changes": ["change_id", "entity_table", "entity_id", "field", "old_value",
                "new_value", "changed_at", "changed_by", "source_system", "source_id",
                "extracted_at"],
}


def load(export_dir, db_path, source="airtable", reveal_labels=False, profile="full"):
    profile_spec = profiles.get(profile)
    export_dir = Path(export_dir)
    if not export_dir.is_dir():
        raise SystemExit(f"Export directory not found: {export_dir}")

    files = [p for p in export_dir.iterdir() if p.is_file()]
    check_export_dir(files)

    adapter_module = ADAPTERS.get(source)
    if adapter_module is None:
        raise SystemExit(f"No adapter named {source!r}. Known adapters: {sorted(ADAPTERS)}")

    extracted_at = datetime.utcnow().replace(microsecond=0)
    tables, adapter = adapter_module.build(
        export_dir, {"extracted_at": extracted_at, "reveal_labels": reveal_labels,
                     "profile": profile_spec})

    # The schema never changes between profiles. A dropped table is present and empty,
    # a dropped column is present and null. That is the honest model of a leaner client:
    # they have the concept, they just have no data in it.
    for table in profile_spec["drop_tables"]:
        tables[table] = []
    for table, columns in profile_spec["drop_columns"].items():
        for row in tables.get(table, []):
            for column in columns:
                row[column] = None

    db_path = Path(db_path)
    if db_path.exists():
        db_path.unlink()
    con = duckdb.connect(str(db_path))
    con.execute(SCHEMA_PATH.read_text(encoding="utf-8"))

    counts = {}
    for table in LANDING_TABLES:
        rows = tables.get(table, [])
        cols = COLUMNS[table]
        if rows:
            values = [tuple(row.get(col) for col in cols) for row in rows]
            placeholders = ", ".join("?" for _ in cols)
            con.executemany(
                f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})", values)
        counts[table] = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
    con.close()

    # The override label map is answer-key material. It goes next to the export,
    # which is gitignored, never into the repo.
    if adapter.label_map and not reveal_labels:
        map_path = export_dir.parent / f"{export_dir.name}.labelmap.json"
        map_path.write_text(
            json.dumps(adapter.label_map, indent=2, sort_keys=True), encoding="utf-8")
    else:
        map_path = None

    # The profile lives beside the database rather than inside it, so the landing
    # schema stays at six tables.
    Path(f"{db_path}.profile.json").write_text(
        json.dumps({"profile": profile_spec["label"],
                    "description": profile_spec["description"],
                    "export_dir": str(export_dir),
                    "skipped_source_tables": adapter.skipped,
                    "emptied_tables": profile_spec["drop_tables"],
                    "nulled_columns": profile_spec["drop_columns"],
                    "collapsed_resource_kind": profile_spec["collapse_resource_kind"]},
                   indent=2) + "\n", encoding="utf-8")

    return {
        "profile": profile_spec["label"],
        "profile_description": profile_spec["description"],
        "skipped_source_tables": adapter.skipped,
        "emptied_tables": profile_spec["drop_tables"],
        "nulled_columns": profile_spec["drop_columns"],
        "counts": counts,
        "files_checked": len(files),
        "missing_columns": adapter.missing_columns,
        "notes": adapter.notes,
        "label_map_path": str(map_path) if map_path else None,
        "distinct_override_labels": len(adapter.label_map),
    }
