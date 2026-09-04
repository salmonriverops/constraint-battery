#!/usr/bin/env python3
"""Constraint discovery battery.

    cli.py load <export_dir>     validate against the denylist, load into duckdb
    cli.py run --out runs/<date> run all probes, write candidates.json
    cli.py score runs/<date>     after match.csv is filled in, write score.md

run never reads key/. That is enforced, not documented.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import textwrap
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from extract.profiles import PROFILES  # noqa: E402


def _prefix_to_table_id():
    """Landing id prefix to Airtable table id, read from the map so it cannot drift."""
    out = {}
    path = ROOT / "extract" / "airtable_map.json"
    if not path.exists():
        return out
    for specs in json.loads(path.read_text(encoding="utf-8")).values():
        if not isinstance(specs, list):
            continue
        for spec in specs:
            if isinstance(spec, dict) and spec.get("id_prefix") and spec.get("table_id"):
                # First writer wins. location_travel reuses the lc_ prefix but points at
                # Routes, and a location id must link to the Locations record.
                out.setdefault(spec["id_prefix"], spec["table_id"])
    return out


PREFIX_TO_TABLE_ID = _prefix_to_table_id()

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


def _label_map(path, db_path):
    """Opaque override id to the raw label, read from the sidecar outside git.

    The battery loads override labels as opaque ids so the rule vocabulary never
    reaches a probe. Judging one is a different job: a person cannot say whether
    an override is a rule without knowing what it was. The map is read here at
    display time from the gitignored sidecar, and it never enters candidates.json.
    """
    candidates = []
    if path:
        candidates.append(Path(path))
    else:
        data = Path(db_path).parent / "data"
        candidates.extend(sorted(data.glob("*.labelmap.json")))
    for candidate_path in candidates:
        if candidate_path.exists():
            try:
                return json.loads(candidate_path.read_text(encoding="utf-8")), candidate_path
            except ValueError:
                continue
    return {}, None


def _resolver(db_path):
    """Map a landing id to something a person can recognise.

    Candidates carry ids because the committed record has to be stable and free of
    names. Reading them is a different job: a human checking a candidate against the
    source needs to see which guide and which trip. The names are resolved at display
    time from the local database and never enter candidates.json.
    """
    import duckdb

    labels = {}
    if not Path(db_path).exists():
        return labels
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        for rid, kind, name in con.execute(
                "SELECT resource_id, kind, name FROM resources").fetchall():
            labels[rid] = f"{name} ({kind})" if kind else str(name)
        for wid, wtype, start in con.execute(
                "SELECT work_id, work_type, start_ts FROM work").fetchall():
            day = start.strftime("%a %Y-%m-%d %H:%M") if start else "no start time"
            labels[wid] = f"{wtype or 'untyped'} on {day}"
        for lid, name in con.execute(
                "SELECT location_id, name FROM locations").fetchall():
            labels[lid] = str(name)
    finally:
        con.close()
    return labels


def _airtable_url(landing_id, base):
    """A link straight to the record, so a candidate can be checked in one click."""
    if not base or "_rec" not in str(landing_id):
        return None
    prefix, _, record = str(landing_id).partition("_")
    table_id = PREFIX_TO_TABLE_ID.get(prefix + "_")
    if not table_id or not record.startswith("rec"):
        return None
    return f"https://airtable.com/{base}/{table_id}/{record}"


_TIMESTAMP = re.compile(r"^(\d{4})-(\d{2})-(\d{2})([ T]\d{2}:\d{2}(:\d{2})?)?$")


def _with_weekday(text):
    """Prefix a bare timestamp with its day name.

    Which day of the week a job falls on is often the whole point of a candidate, and
    2026-06-23 does not say Tuesday to anyone.
    """
    match = _TIMESTAMP.match(text)
    if not match:
        return text
    try:
        day = date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return text
    return f"{day.strftime('%a')} {text}"


def _describe(value, labels, base):
    """Render one evidence value with its human label and link when there is one."""
    text = str(value)
    label = labels.get(text)
    if label is None:
        return _with_weekday(text)
    url = _airtable_url(text, base)
    return f"{label}" + (f"  {url}" if url else f"  [{text}]")


def cmd_show(args):
    """Print the candidates one at a time, in match.csv order.

    This displays. It does not decide. Reading a candidate and judging it is the
    hand work the protocol reserves for a person, and nothing here proposes a
    verdict or narrows the key rows worth considering.
    """
    run_dir = Path(args.run_dir)
    labels = _resolver(args.db)
    overrides, map_path = _label_map(getattr(args, "labels", None), args.db)
    labels.update(overrides)
    if map_path:
        print(f"override labels resolved from {map_path}\n")
    if not labels:
        print(f"note: {args.db} not found, so ids cannot be resolved to names. "
              f"Pass --db if the database is elsewhere.\n")
    payload = json.loads((run_dir / "candidates.json").read_text(encoding="utf-8"))
    candidates = payload["candidates"]

    done = {}
    match_path = run_dir / "match.csv"
    if match_path.exists():
        with match_path.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if (row.get("verdict") or "").strip():
                    done.setdefault(row["candidate_id"], []).append(row)

    remaining = [c for c in candidates if c["candidate_id"] not in done]
    if args.todo:
        candidates = remaining

    width = 78
    for index, candidate in enumerate(candidates, 1):
        cid = candidate["candidate_id"]
        print("=" * width)
        print(f"[{index} of {len(candidates)}]  {cid}   probe {candidate['probe']}   "
              f"proposed type: {candidate['proposed_type']}")
        print("=" * width)
        print()
        for line in textwrap.wrap(candidate["statement"], width):
            print(f"  {line}")
        print()
        evidence = candidate.get("evidence") or {}
        if evidence:
            print("  evidence")
            # Scalars first, they are the counts that make a candidate worth reading.
            # Example rows go last and are capped, because the point of an example is
            # to be checkable in the base, not exhaustive.
            scalars = {k: v for k, v in evidence.items() if not isinstance(v, list)}
            listy = {k: v for k, v in evidence.items() if isinstance(v, list)}
            for key in sorted(scalars):
                print(f"    {key}: {scalars[key]}")
            for key in sorted(listy):
                values = listy[key]
                shown = values[:args.examples]
                print(f"    {key}: {len(values)}")
                for item in shown:
                    if isinstance(item, dict):
                        print("      -")
                        for k, v in item.items():
                            print(f"          {k}: {_describe(v, labels, args.base)}")
                    else:
                        print(f"      - {_describe(item, labels, args.base)}")
                if len(values) > len(shown):
                    print(f"      ... and {len(values) - len(shown)} more, "
                          f"see candidates.json")
            print()
        if cid in done:
            for row in done[cid]:
                print(f"  already recorded: {row['verdict']} {row.get('key_id') or ''}")
        else:
            print(f"  match.csv row to fill:  {cid},<key_id or blank>,<MATCH|NEW|FALSE>,")
        print()

    print(f"{len(remaining)} of {len(payload['candidates'])} candidates still unjudged "
          f"in {match_path}")
    return 0


def _render(candidate, labels, base, examples, index, total):
    """One candidate, printed for a person to read. Shared by show and judge."""
    lines = []
    add = lines.append
    width = 78
    cid = candidate["candidate_id"]
    add("=" * width)
    add(f"[{index} of {total}]  {cid}   probe {candidate['probe']}   "
        f"proposed type: {candidate['proposed_type']}")
    add("=" * width)
    add("")
    for line in textwrap.wrap(candidate["statement"], width):
        add(f"  {line}")
    add("")
    evidence = candidate.get("evidence") or {}
    field = str(evidence.get("field") or "")
    if field.startswith("ovr_"):
        label = labels.get(field)
        if label:
            add(f"  the override is labelled: {label!r}")
        else:
            add(f"  no label found for {field}. Pass --labels with the path to the "
                f"labelmap.json the loader wrote, or re-run load to write it.")
        add("")
    if evidence:
        add("  evidence")
        scalars = {k: v for k, v in evidence.items() if not isinstance(v, list)}
        listy = {k: v for k, v in evidence.items() if isinstance(v, list)}
        for key in sorted(scalars):
            add(f"    {key}: {scalars[key]}")
        for key in sorted(listy):
            values = listy[key]
            shown = values[:examples]
            add(f"    {key}: {len(values)}")
            for item in shown:
                if isinstance(item, dict):
                    add("      -")
                    for k, v in item.items():
                        add(f"          {k}: {_describe(v, labels, base)}")
                else:
                    add(f"      - {_describe(item, labels, base)}")
            if len(values) > len(shown):
                add(f"      ... and {len(values) - len(shown)} more, see candidates.json")
        add("")
    return lines


def _read_match(match_path):
    """Existing verdicts, keyed by candidate id. One candidate can hold several rows."""
    recorded = {}
    if not match_path.exists():
        return recorded
    with match_path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if (row.get("verdict") or "").strip():
                recorded.setdefault(row["candidate_id"], []).append(row)
    return recorded


def _write_match(match_path, candidates, recorded):
    """Rewrite match.csv in candidate order, quoting whatever the notes contain."""
    with match_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["candidate_id", "key_id", "verdict", "note"])
        writer.writeheader()
        for candidate in candidates:
            cid = candidate["candidate_id"]
            rows = recorded.get(cid)
            if not rows:
                writer.writerow({"candidate_id": cid, "key_id": "", "verdict": "", "note": ""})
                continue
            for row in rows:
                writer.writerow({"candidate_id": cid, "key_id": row.get("key_id", ""),
                                 "verdict": row.get("verdict", ""),
                                 "note": row.get("note", "")})


def _prompt_note():
    """Read a note that may run to many lines. Blank line ends it.

    Dictation produces long unbroken text with commas and quotes in it, which is
    miserable to type into a spreadsheet cell and easy to corrupt. Taking it here and
    writing it through the csv module means the file stays valid whatever is said.
    """
    print("  note, as long as you like. Blank line when done:")
    lines = []
    while True:
        try:
            line = input("  > ")
        except EOFError:
            break
        if not line.strip():
            break
        lines.append(line.strip())
    return " ".join(lines)


def cmd_judge(args):
    """Record verdicts one candidate at a time.

    This is data entry, not matching. It shows a candidate, asks what the person
    decided, and writes it down. It proposes nothing, ranks nothing, suggests no key
    row, and never reads key/. The judgement is the operator's and this only saves
    them from hand editing a CSV while dictating.
    """
    run_dir = Path(args.run_dir)
    labels = _resolver(args.db)
    overrides, map_path = _label_map(args.labels, args.db)
    labels.update(overrides)
    if map_path:
        print(f"override labels resolved from {map_path}")
    payload = json.loads((run_dir / "candidates.json").read_text(encoding="utf-8"))
    candidates = payload["candidates"]
    match_path = run_dir / "match.csv"
    recorded = _read_match(match_path)

    queue = [c for c in candidates if args.redo or c["candidate_id"] not in recorded]
    if not queue:
        print(f"every candidate in {match_path} already has a verdict. "
              f"Use --redo to go through them again.")
        return 0

    print(f"{len(queue)} candidate(s) to judge.\n")
    print("  m  MATCH   this says the same thing as a rule already in your key.")
    print("             You will be asked which key id, or ids if it covers several.")
    print("  n  NEW     this is a real constraint and your key does not contain it.")
    print("             These are the finds. This is the number the experiment is about.")
    print("  f  FALSE   this is not a constraint. A data artifact, a coincidence, or")
    print("             a pattern with no rule behind it.")
    print("  s  SKIP    come back to it. Nothing is recorded and it stays in the queue.")
    print("  q  QUIT    stop. Everything already judged is saved.")
    print()
    print("  If you cannot decide between MATCH and NEW, it is NEW only when you are")
    print("  sure no key row says it. Otherwise skip it and look the key row up first.")
    print()

    for position, candidate in enumerate(queue, 1):
        cid = candidate["candidate_id"]
        print("\n".join(_render(candidate, labels, args.base, args.examples,
                                position, len(queue))))
        try:
            verdict = ""
            while verdict not in ("MATCH", "NEW", "FALSE"):
                answer = input("  verdict  [m]atch  [n]ew  [f]alse  [s]kip  [q]uit: ")
                answer = answer.strip().lower()
                if answer in ("q", "quit"):
                    print(f"\nstopped. {match_path} holds everything judged so far.")
                    return 0
                if answer in ("s", "skip", ""):
                    verdict = None
                    break
                verdict = {"m": "MATCH", "n": "NEW", "f": "FALSE"}.get(answer[:1], "")
                if not verdict:
                    print("  m, n, f, s or q.")
            if verdict is None:
                continue

            key_ids = [""]
            if verdict == "MATCH":
                raw = input("  key id(s), comma separated if it covers several: ")
                key_ids = [k.strip().upper() for k in raw.split(",") if k.strip()] or [""]

            note = _prompt_note()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\nstopped. {match_path} holds everything judged so far.")
            return 0

        recorded[cid] = [{"key_id": key_id, "verdict": verdict, "note": note}
                         for key_id in key_ids]
        _write_match(match_path, candidates, recorded)
        print(f"  recorded {verdict} {' '.join(k for k in key_ids if k)}".rstrip())

    done = sum(1 for c in candidates if c["candidate_id"] in recorded)
    print(f"\n{done} of {len(candidates)} candidates judged in {match_path}")
    return 0


PEAKS = {
    "work_per_day": ("day", """
        SELECT cast(w.start_ts AS DATE) AS grp, count(*) AS n,
               string_agg(coalesce(w.work_type, 'untyped'), ', ' ORDER BY w.start_ts) AS detail
        FROM work w WHERE w.start_ts IS NOT NULL GROUP BY 1 ORDER BY n DESC, grp LIMIT ?"""),

    "work_per_location_per_day": ("location and day", """
        SELECT coalesce(l.name, w.location_id) || '  ' || cast(w.start_ts AS DATE) AS grp,
               count(*) AS n,
               string_agg(coalesce(w.work_type, 'untyped'), ', ' ORDER BY w.start_ts) AS detail
        FROM work w LEFT JOIN locations l ON l.location_id = w.location_id
        WHERE w.start_ts IS NOT NULL AND w.location_id IS NOT NULL
        GROUP BY 1 ORDER BY n DESC, grp LIMIT ?"""),

    "work_per_resource_per_day": ("resource and day", """
        SELECT coalesce(r.name, a.resource_id) || '  (' || coalesce(r.kind, 'unknown')
                 || ')  ' || strftime(cast(a.start_ts AS DATE), '%a %Y-%m-%d') AS grp,
               count(DISTINCT a.work_id) AS n,
               string_agg(DISTINCT coalesce(w.work_type, 'untyped') || ' '
                 || coalesce(strftime(a.start_ts, '%H:%M'), '') || ' as ' || a.role,
                 ' | ') AS detail
        FROM assignments a
        LEFT JOIN resources r ON r.resource_id = a.resource_id
        LEFT JOIN work w ON w.work_id = a.work_id
        WHERE a.start_ts IS NOT NULL GROUP BY 1 ORDER BY n DESC, grp LIMIT ?"""),

    "customers_per_work": ("job", """
        SELECT coalesce(w.work_type, 'untyped') || '  ' ||
               coalesce(strftime(w.start_ts, '%a %Y-%m-%d %H:%M'), 'no start') AS grp,
               w.customer_count AS n, w.work_id AS detail
        FROM work w WHERE w.customer_count IS NOT NULL ORDER BY n DESC, grp LIMIT ?"""),

    "resources_per_work": ("job", """
        SELECT coalesce(w.work_type, 'untyped') || '  ' ||
               coalesce(strftime(w.start_ts, '%a %Y-%m-%d %H:%M'), 'no start') AS grp,
               count(DISTINCT a.resource_id) AS n,
               string_agg(DISTINCT coalesce(r.name, a.resource_id), ', ') AS detail
        FROM assignments a JOIN work w ON w.work_id = a.work_id
        LEFT JOIN resources r ON r.resource_id = a.resource_id
        GROUP BY w.work_id, 1 ORDER BY n DESC, grp LIMIT ?"""),
}


def cmd_peak(args):
    """Show the rows behind the top of a p04 distribution.

    A ceiling candidate reports that the maximum was N and how rare N was, which
    is enough to ask the question and not enough to answer it. This names the
    days, jobs or people at the top so the claim can be checked against the
    source. It reads the database only. It touches no candidate and no verdict.
    """
    import duckdb

    if args.dimension not in PEAKS:
        raise SystemExit(f"unknown dimension {args.dimension!r}. "
                         f"Known: {', '.join(sorted(PEAKS))}")
    label, sql = PEAKS[args.dimension]
    con = duckdb.connect(str(args.db), read_only=True)
    try:
        rows = con.execute(sql, [args.top]).fetchall()
    finally:
        con.close()

    print(f"top {len(rows)} by {args.dimension}, one line per {label}\n")
    for grp, n, detail in rows:
        print(f"  {n:>4}   {grp}")
        if detail and not args.brief:
            for line in textwrap.wrap(str(detail), 68):
                print(f"         {line}")
    return 0


def cmd_day(args):
    """Every job on one date, with who and what was on it.

    The place a person lands when a candidate raises a question about a specific
    day. Reads the database, resolves ids to names, links each job back to its
    Airtable record. Writes nothing.
    """
    import duckdb

    con = duckdb.connect(str(args.db), read_only=True)
    try:
        jobs = con.execute("""
            SELECT w.work_id, coalesce(w.work_type, 'untyped') AS wtype,
                   w.start_ts, w.end_ts, w.customer_count, w.status,
                   coalesce(l.name, '') AS loc
            FROM work w LEFT JOIN locations l ON l.location_id = w.location_id
            WHERE cast(w.start_ts AS DATE) = cast(? AS DATE)
            ORDER BY w.start_ts, w.work_id""", [args.date]).fetchall()
        crew = {}
        for wid, name, kind, role in con.execute("""
                SELECT a.work_id, coalesce(r.name, a.resource_id),
                       coalesce(r.kind, '?'), a.role
                FROM assignments a LEFT JOIN resources r ON r.resource_id = a.resource_id
                WHERE a.work_id IN (SELECT w.work_id FROM work w
                                    WHERE cast(w.start_ts AS DATE) = cast(? AS DATE))
                ORDER BY 2""", [args.date]).fetchall():
            crew.setdefault(wid, []).append(f"{name} [{kind}] as {role}")
    finally:
        con.close()

    if not jobs:
        print(f"no jobs with a start time on {args.date}")
        return 0

    print(f"{len(jobs)} job(s) on {args.date}\n")
    for wid, wtype, start, end, guests, status, loc in jobs:
        when = start.strftime("%a %H:%M") if start else "no start"
        until = end.strftime("%H:%M") if end else "?"
        bits = [f"{guests} guests" if guests is not None else "no guest count"]
        if status:
            bits.append(str(status))
        if loc:
            bits.append(loc)
        print(f"  {when} to {until}   {wtype}")
        print(f"      {', '.join(bits)}")
        url = _airtable_url(wid, args.base)
        if url:
            print(f"      {url}")
        for line in crew.get(wid, []):
            print(f"      - {line}")
        if not crew.get(wid):
            print("      - nobody assigned")
        print()
    return 0


def cmd_override(args):
    """Every change recorded under one override, with the jobs it touched.

    A p08 candidate says an override was applied N times. Judging it needs the
    label and the actual jobs, so both are resolved here from the database and
    the gitignored label map. Nothing is written.
    """
    import duckdb

    overrides, map_path = _label_map(args.labels, args.db)
    field = args.field if args.field.startswith("ovr_") else f"ovr_{args.field}"
    label = overrides.get(field)
    print(f"{field}")
    if label:
        print(f"labelled: {label!r}" + (f"   from {map_path}" if map_path else ""))
    else:
        print("no label found. Pass --labels with the path to the labelmap.json.")
    print()

    con = duckdb.connect(str(args.db), read_only=True)
    try:
        rows = con.execute("""
            SELECT c.changed_at, c.changed_by, c.entity_id,
                   coalesce(w.work_type, 'untyped'), w.start_ts, w.customer_count,
                   c.old_value, c.new_value
            FROM changes c LEFT JOIN work w ON w.work_id = c.entity_id
            WHERE c.field = ? ORDER BY c.changed_at, c.entity_id""", [field]).fetchall()
    finally:
        con.close()

    if not rows:
        print("no changes recorded under that field")
        return 0

    print(f"{len(rows)} change(s)\n")
    for at, by, entity, wtype, start, guests, old, new in rows:
        when = at.strftime("%a %Y-%m-%d") if at else "no timestamp"
        job = start.strftime("%a %Y-%m-%d %H:%M") if start else "no start time"
        lead = (start.date() - at.date()).days if (at and start) else None
        print(f"  changed {when} by {by or 'unknown'}"
              + (f", {lead} day(s) before the job" if lead is not None else ""))
        print(f"    job: {wtype} on {job}"
              + (f", {guests} guests" if guests is not None else ""))
        url = _airtable_url(entity, args.base)
        if url:
            print(f"    {url}")
        if old or new:
            print(f"    {old!r} -> {new!r}")
        print()
    return 0


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

    p_show = sub.add_parser("show", help="print the candidates for reading and judging")
    p_show.add_argument("run_dir")
    p_show.add_argument("--db", default=str(DEFAULT_DB),
                        help="database to resolve ids to names against")
    p_show.add_argument("--base", default=os.environ.get("AIRTABLE_BASE", ""),
                        help="Airtable base id, to print a link to each record. "
                             "Defaults to $AIRTABLE_BASE.")
    p_show.add_argument("--labels", help="path to the labelmap.json the loader wrote")
    p_show.add_argument("--examples", type=int, default=6,
                        help="example rows to print per candidate, default 6")
    p_show.add_argument("--todo", action="store_true",
                        help="only the candidates with no verdict yet in match.csv")
    p_show.set_defaults(func=cmd_show)

    p_judge = sub.add_parser("judge", help="record verdicts one candidate at a time")
    p_judge.add_argument("run_dir")
    p_judge.add_argument("--db", default=str(DEFAULT_DB))
    p_judge.add_argument("--base", default=os.environ.get("AIRTABLE_BASE", ""))
    p_judge.add_argument("--labels", help="path to the labelmap.json the loader wrote")
    p_judge.add_argument("--examples", type=int, default=6)
    p_judge.add_argument("--redo", action="store_true",
                         help="go through candidates that already have a verdict")
    p_judge.set_defaults(func=cmd_judge)

    p_ovr = sub.add_parser("override", help="open one p08 override: its label and its jobs")
    p_ovr.add_argument("field", help="ovr_xxxxxxxxxxxx, or just the hex part")
    p_ovr.add_argument("--db", default=str(DEFAULT_DB))
    p_ovr.add_argument("--base", default=os.environ.get("AIRTABLE_BASE", ""))
    p_ovr.add_argument("--labels", help="path to the labelmap.json the loader wrote")
    p_ovr.set_defaults(func=cmd_override)

    p_peak = sub.add_parser("peak", help="show the rows behind the top of a p04 ceiling")
    p_peak.add_argument("dimension", help=", ".join(sorted(PEAKS)))
    p_peak.add_argument("--db", default=str(DEFAULT_DB))
    p_peak.add_argument("--top", type=int, default=5)
    p_peak.add_argument("--brief", action="store_true", help="counts only, no detail")
    p_peak.set_defaults(func=cmd_peak)

    p_day = sub.add_parser("day", help="every job on one date, with crew and links")
    p_day.add_argument("date", help="YYYY-MM-DD")
    p_day.add_argument("--db", default=str(DEFAULT_DB))
    p_day.add_argument("--base", default=os.environ.get("AIRTABLE_BASE", ""))
    p_day.set_defaults(func=cmd_day)

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
