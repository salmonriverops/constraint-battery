#!/usr/bin/env python3
"""Constraint discovery battery.

    cli.py load <export_dir>     validate against the denylist, load into duckdb
    cli.py run --out runs/<date> run all probes, write candidates.json
    cli.py score runs/<date>     after match.csv is filled in, write score.md

run never reads key/. That is enforced, not documented.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from extract.profiles import PROFILES  # noqa: E402

DEFAULT_DB = ROOT / "battery.duckdb"
KEY_DIR = (ROOT / "key").resolve()


class KeyDirectoryRead(Exception):
    """Raised if anything under key/ is opened during a run. The run is invalid."""


def forbid_key_reads():
    """Install an audit hook that hard-fails on any read under key/.

    The scoring protocol depends on the probes never having seen the key. A comment
    saying so is worth nothing, so this makes it an error the process cannot survive.
    """
    def hook(event, args):
        if event not in ("open", "os.open"):
            return
        try:
            target = Path(str(args[0])).resolve()
        except (TypeError, ValueError, OSError):
            return
        if target == KEY_DIR or KEY_DIR in target.parents:
            raise KeyDirectoryRead(
                f"run attempted to read {target}. cli.py run must never read key/. "
                f"The run is invalid.")
    sys.addaudithook(hook)


# -- load -----------------------------------------------------------------

def cmd_load(args):
    from extract.loader import load
    from extract.denylist import DenylistViolation
    try:
        result = load(args.export_dir, args.db, source=args.source,
                      reveal_labels=args.reveal_override_labels, profile=args.profile)
    except DenylistViolation as exc:
        print("\nLOAD REFUSED\n", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 2

    print(f"loaded {args.export_dir} -> {args.db}")
    print(f"  profile: {result['profile']}. {result['profile_description']}")
    print(f"  {result['files_checked']} files checked against the denylist, none matched")
    if result["skipped_source_tables"]:
        print(f"  source tables not read: {', '.join(result['skipped_source_tables'])}")
    if result["emptied_tables"]:
        print(f"  landing tables left empty: {', '.join(result['emptied_tables'])}")
    for table, columns in (result["nulled_columns"] or {}).items():
        print(f"  columns left null: {table}.{', '.join(columns)}")
    print()
    width = max(len(t) for t in result["counts"])
    for table, count in result["counts"].items():
        print(f"  {table.ljust(width)}  {count:>8,}")
    if result["distinct_override_labels"]:
        print(f"\n  override log: {result['distinct_override_labels']} distinct labels, "
              f"loaded as opaque ids")
        if result["label_map_path"]:
            print(f"  label map written outside git: {result['label_map_path']}")
    if result["missing_columns"]:
        print("\n  columns named in the map but absent from the export:")
        for table, column in result["missing_columns"]:
            print(f"    {table}.{column}")
    for note in result["notes"]:
        print(f"\n  note: {note}")
    return 0


# -- run ------------------------------------------------------------------

def cmd_run(args):
    forbid_key_reads()
    import duckdb
    from probes import p03_exclusivity, p04_ceilings, p05_population, p08_overrides

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    guards = {
        "min_assignments_per_resource": args.min_assignments,
        "min_instances_per_work_type": args.min_instances,
        "min_populated_rows_per_field": args.min_populated,
        "min_observations": args.min_observations,
        "min_change_events": args.min_change_events,
    }

    sidecar = Path(f"{args.db}.profile.json")
    profile = json.loads(sidecar.read_text(encoding="utf-8")) if sidecar.exists() else {
        "profile": "unknown",
        "description": "no profile sidecar beside this database, so the load predates "
                       "profiles or the sidecar was removed"}

    con = duckdb.connect(str(args.db), read_only=True)
    candidates = []
    order = [p03_exclusivity, p04_ceilings, p05_population, p08_overrides]
    if args.probes:
        wanted = set(args.probes)
        order = [m for m in order if m.PROBE in wanted]
    for module in order:
        candidates.extend(module.run(con, guards))

    # Deterministic order: probe, then type, then candidate_id.
    candidates.sort(key=lambda c: (c["probe"], c["proposed_type"], c["candidate_id"]))

    volumes = {t: con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
               for t in ("work", "resources", "assignments", "locations",
                         "location_travel", "changes")}
    con.close()

    # candidates.json carries no wall clock, so a rerun on the same input is
    # byte identical and the pre-registration commit means what it says.
    (out_dir / "candidates.json").write_text(
        json.dumps({"profile": profile, "guards": guards, "input_volumes": volumes,
                    "candidates": candidates}, indent=2, sort_keys=False,
                   default=str) + "\n", encoding="utf-8")

    (out_dir / "run_meta.json").write_text(
        json.dumps({"generated_at": datetime.utcnow().isoformat(timespec="seconds"),
                    "db": str(args.db), "probes": [m.PROBE for m in order]},
                   indent=2) + "\n", encoding="utf-8")

    stub = out_dir / "match.csv"
    if not stub.exists():
        lines = ["candidate_id,key_id,verdict,note"]
        lines += [f"{c['candidate_id']},,," for c in candidates]
        stub.write_text("\n".join(lines) + "\n", encoding="utf-8")

    by_probe = {}
    for c in candidates:
        by_probe[c["probe"]] = by_probe.get(c["probe"], 0) + 1
    print(f"profile: {profile.get('profile')}")
    print(f"{len(candidates)} candidates -> {out_dir / 'candidates.json'}")
    for probe in sorted(by_probe):
        print(f"  {probe}  {by_probe[probe]:>4}")
    print(f"\nblank match.csv written to {stub}")
    print("commit candidates.json before you start matching. That commit is the "
          "pre-registration.")
    return 0


# -- score ----------------------------------------------------------------

def cmd_score(args):
    from score.score import compare_runs, score_run
    if args.compare:
        first, second = args.compare
        return compare_runs(Path(first), Path(second), ROOT / "key",
                            Path(args.out) if args.out else None)
    if not args.run_dir:
        raise SystemExit("give a run directory, or --compare <run_a> <run_b>")
    return score_run(Path(args.run_dir), ROOT / "key")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="cli.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_load = sub.add_parser("load", help="validate against the denylist, load into duckdb")
    p_load.add_argument("export_dir")
    p_load.add_argument("--db", default=str(DEFAULT_DB))
    p_load.add_argument("--source", default="airtable")
    p_load.add_argument("--profile", default="full", choices=sorted(PROFILES),
                        help="full is the export as it stands. lean keeps only what a "
                             "typical operation would plausibly produce.")
    p_load.add_argument("--reveal-override-labels", action="store_true",
                        help="load override labels verbatim. Invalidates a scored run.")
    p_load.set_defaults(func=cmd_load)

    p_run = sub.add_parser("run", help="run all probes, write candidates.json")
    p_run.add_argument("--out", default=f"runs/{date.today().isoformat()}")
    p_run.add_argument("--db", default=str(DEFAULT_DB))
    p_run.add_argument("--probes", nargs="*", help="probe ids to run, default all")
    p_run.add_argument("--min-assignments", type=int, default=20,
                       help="a resource needs at least this many assignments")
    p_run.add_argument("--min-instances", type=int, default=10,
                       help="a work_type needs at least this many instances")
    p_run.add_argument("--min-populated", type=int, default=50,
                       help="a field needs at least this many populated rows")
    p_run.add_argument("--min-observations", type=int, default=50,
                       help="a distribution needs at least this many observations")
    p_run.add_argument("--min-change-events", type=int, default=3,
                       help="an overridden field needs at least this many events")
    p_run.set_defaults(func=cmd_run)

    p_score = sub.add_parser("score", help="write score.md from a filled in match.csv")
    p_score.add_argument("run_dir", nargs="?")
    p_score.add_argument("--compare", nargs=2, metavar=("RUN_A", "RUN_B"),
                         help="write delta.md comparing two runs, richer first")
    p_score.add_argument("--out", help="where delta.md goes, default the first run dir")
    p_score.set_defaults(func=cmd_score)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
