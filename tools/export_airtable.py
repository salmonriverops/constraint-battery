#!/usr/bin/env python3
"""Pull an export out of Airtable, as JSON, with record ids intact.

Airtable's built in CSV export is not usable here. It omits record ids and renders
linked records as display names, so resources would load with no id at all and the
join from assignments to resources would collapse. This goes through the REST API
instead, which preserves ids.

What it fetches is derived from extract/airtable_map.json, so the exporter and the
adapter cannot drift apart. Only the columns the map actually names are requested.
Everything else stays in Airtable.

It refuses to fetch a denylisted table even if one is named on the command line.

Usage:
    export AIRTABLE_TOKEN=pat...
    python3 tools/export_airtable.py --base appXXXXXXXXXXXXXX --out data/export
    python3 tools/export_airtable.py --base appXXXXXXXXXXXXXX --out data/export --dry-run

The output directory is under data/, which is gitignored. Keep it that way.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from extract.denylist import DenylistViolation, check_table  # noqa: E402

MAP_PATH = ROOT / "extract" / "airtable_map.json"
API = "https://api.airtable.com/v0"
PAGE_SIZE = 100
SLEEP_BETWEEN_PAGES = 0.25   # Airtable allows 5 requests a second per base

# Which map keys name a source column, by landing table. Anything not listed here
# is a landing column name or a literal, not something to fetch.
COLUMN_KEYS = ["work_type", "start_ts", "end_ts", "location_id", "status",
               "customer_count", "fallback_date", "work_type_link", "location_link",
               "name", "home_location_id", "kind_column", "from_link", "to_link",
               "minutes", "sample_count", "ack_column", "work_date"]


def wanted(map_data):
    """Walk the column map and collect {source table: sorted list of columns}."""
    out = {}
    ids = {}
    for specs in map_data.values():
        if not isinstance(specs, list):
            continue
        for spec in specs:
            if not isinstance(spec, dict):
                continue                  # skips the _comment block
            table = spec.get("table")
            if not table:
                continue
            cols = out.setdefault(table, set())
            if spec.get("table_id"):
                ids[table] = spec["table_id"]
            for key in COLUMN_KEYS:
                value = spec.get(key)
                if isinstance(value, str):
                    cols.add(value)
            for key in ("roles", "work_link"):
                for column in (spec.get(key) or {}):
                    cols.add(column)
    return {table: sorted(cols) for table, cols in out.items()}, ids


def fetch_table(base, table, fields, token, address=None, verbose=True):
    """Fetch every record in a table, following pagination.

    address is the Airtable table id when the map pins one, otherwise the name.
    A name containing an ampersand or a slash is easy to get wrong through a URL,
    so pinning the id in the map is the safer choice for those.
    """
    address = address or table
    records, offset, page = [], None, 0
    while True:
        query = [("pageSize", str(PAGE_SIZE))]
        query += [("fields[]", field) for field in fields]
        if offset:
            query.append(("offset", offset))
        url = (f"{API}/{urllib.parse.quote(base)}/{urllib.parse.quote(address)}"
               f"?{urllib.parse.urlencode(query)}")
        request = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:400]
            raise SystemExit(
                f"\nAirtable returned {exc.code} for table {table!r}.\n{detail}\n\n"
                f"A 401 means the token is wrong. A 403 means the token cannot see this "
                f"base. A 404 usually means the table name does not match Airtable "
                f"exactly, including spaces and any ampersand. Pin the table id with "
                f"a \"table_id\" key in extract/airtable_map.json to avoid that.")
        for record in payload.get("records", []):
            row = dict(record.get("fields", {}))
            row["id"] = record["id"]
            records.append(row)
        page += 1
        if verbose:
            print(f"    page {page}, {len(records)} records so far", flush=True)
        offset = payload.get("offset")
        if not offset:
            break
        time.sleep(SLEEP_BETWEEN_PAGES)
    # Stable order, so two exports of unchanged data are byte identical.
    records.sort(key=lambda r: r["id"])
    return records


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", required=True, help="Airtable base id, appXXXXXXXXXXXXXX")
    parser.add_argument("--out", default="data/export", help="output directory, keep it under data/")
    parser.add_argument("--only", nargs="*", help="fetch only these tables, for a retry")
    parser.add_argument("--dry-run", action="store_true",
                        help="print what would be fetched and stop")
    args = parser.parse_args(argv)

    plan, table_ids = wanted(json.loads(MAP_PATH.read_text(encoding="utf-8")))
    if args.only:
        missing = [t for t in args.only if t not in plan]
        if missing:
            raise SystemExit(f"not in the column map: {missing}. Known: {sorted(plan)}")
        plan = {t: plan[t] for t in args.only}

    # The denylist applies to what we ask for, not only to what lands on disk.
    for table in sorted(plan):
        try:
            check_table(table)
        except DenylistViolation as exc:
            print("\nEXPORT REFUSED\n", file=sys.stderr)
            print(str(exc), file=sys.stderr)
            print("\nNothing was fetched. Remove this table from "
                  "extract/airtable_map.json.", file=sys.stderr)
            return 2

    print(f"{len(plan)} tables to fetch from {args.base}, columns per the map:\n")
    for table in sorted(plan):
        pin = f"  [{table_ids[table]}]" if table in table_ids else ""
        print(f"  {table}{pin}")
        for column in plan[table]:
            print(f"      {column}")
    print()

    if args.dry_run:
        print("dry run, nothing fetched")
        return 0

    token = os.environ.get("AIRTABLE_TOKEN") or os.environ.get("AIRTABLE_API_KEY")
    if not token:
        raise SystemExit(
            "No token. Set AIRTABLE_TOKEN to a personal access token with data.records:read "
            "on this base, then run again.")

    out_dir = Path(args.out)
    if "data" not in out_dir.parts and "export" not in out_dir.name:
        print(f"warning: {out_dir} is not under data/. Business data must stay out of git.\n")
    out_dir.mkdir(parents=True, exist_ok=True)

    totals = {}
    for table in sorted(plan):
        print(f"  {table}")
        records = fetch_table(args.base, table, plan[table], token,
                              address=table_ids.get(table))
        (out_dir / f"{table}.json").write_text(
            json.dumps(records, indent=1, sort_keys=True), encoding="utf-8")
        totals[table] = len(records)

    print(f"\nwrote {sum(totals.values()):,} records to {out_dir}\n")
    width = max(len(t) for t in totals)
    for table in sorted(totals):
        print(f"  {table.ljust(width)}  {totals[table]:>7,}")
    print(f"\nnext:  python3 cli.py load {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
