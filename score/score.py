"""Scoring.

Reads the frozen key/answer_key.csv and a hand-filled match.csv, writes score.md.

This module does not match anything. Matching is done by a human, candidate by
candidate. There is no matcher here and there should never be one.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

VERDICTS = {"MATCH", "NEW", "FALSE"}


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        return [row for row in csv.DictReader(handle)
                if any((value or "").strip() for value in row.values())]


def load_key(key_dir: Path):
    """The frozen key, its hash state, and its provenance."""
    key_path = key_dir / "answer_key.csv"
    if not key_path.exists():
        raise SystemExit(f"missing {key_path}")
    key_rows = read_csv(key_path)
    if not key_rows:
        raise SystemExit(f"{key_path} has no rows. Assemble and freeze the key first.")

    provenance = {}
    prov_path = key_dir / "provenance.json"
    if prov_path.exists():
        try:
            provenance = json.loads(prov_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            provenance = {"notes": "provenance.json is present but does not parse"}

    digest = hashlib.sha256(key_path.read_bytes()).hexdigest()
    hash_path = key_dir / "key_hash.txt"
    if hash_path.exists():
        recorded = hash_path.read_text(encoding="utf-8").split()[0].strip()
        frozen = "yes" if recorded == digest else "NO, THE KEY HAS CHANGED SINCE IT WAS FROZEN"
    else:
        frozen = "NO, key_hash.txt does not exist"
    return key_rows, digest, frozen, provenance


def tally(run_dir: Path, key_rows):
    """Read one run's candidates and match.csv and count them up.

    No matching happens here. It reads the verdicts a human already wrote.
    """
    run_dir = Path(run_dir)
    match_path = run_dir / "match.csv"
    candidates_path = run_dir / "candidates.json"
    for path in (match_path, candidates_path):
        if not path.exists():
            raise SystemExit(f"missing {path}")

    payload = json.loads(candidates_path.read_text(encoding="utf-8"))
    candidates = payload["candidates"]
    by_id = {c["candidate_id"]: c for c in candidates}
    key_by_id = {row["key_id"]: row for row in key_rows}

    problems = []
    matched_keys, per_candidate = defaultdict(list), {}
    for row in read_csv(match_path):
        cid = (row.get("candidate_id") or "").strip()
        verdict = (row.get("verdict") or "").strip().upper()
        key_id = (row.get("key_id") or "").strip()
        if not cid:
            continue
        if cid not in by_id:
            problems.append(f"match.csv names candidate {cid!r}, which is not in candidates.json")
            continue
        if not verdict:
            continue
        if verdict not in VERDICTS:
            problems.append(f"{cid}: verdict {verdict!r} is not one of {sorted(VERDICTS)}")
            continue
        if verdict == "MATCH" and not key_id:
            problems.append(f"{cid}: verdict MATCH with no key_id")
            continue
        if key_id and key_id not in key_by_id:
            problems.append(f"{cid}: key_id {key_id!r} is not in the answer key")
            continue
        # One candidate may recover more than one key row. Write one match.csv row
        # per pairing, repeating the candidate_id. Recall credits every key row
        # named. Precision counts the candidate once, never once per pairing.
        entry = per_candidate.setdefault(cid, {"verdict": verdict, "key_ids": [], "notes": []})
        if entry["verdict"] != verdict:
            problems.append(
                f"{cid}: rows disagree on the verdict, {entry['verdict']} then {verdict}")
            continue
        if key_id and key_id not in entry["key_ids"]:
            entry["key_ids"].append(key_id)
        note = (row.get("note") or "").strip()
        if note and note not in entry["notes"]:
            entry["notes"].append(note)
        if verdict == "MATCH":
            matched_keys[key_id].append(cid)

    verdicts = Counter(entry["verdict"] for entry in per_candidate.values())
    total_candidates = len(candidates)
    precision_num = verdicts["MATCH"] + verdicts["NEW"]

    by_type = defaultdict(lambda: [0, 0])
    for row in key_rows:
        ktype = (row.get("type") or "(untyped)").strip() or "(untyped)"
        by_type[ktype][1] += 1
        if row["key_id"] in matched_keys:
            by_type[ktype][0] += 1

    by_source = defaultdict(lambda: [0, 0])
    for row in key_rows:
        ksource = (row.get("source") or "").strip().lower() or "(unrecorded)"
        by_source[ksource][1] += 1
        if row["key_id"] in matched_keys:
            by_source[ksource][0] += 1

    by_probe = Counter(c["probe"] for c in candidates)

    return {
        "run_dir": run_dir,
        "profile": (payload.get("profile") or {}).get("profile", "unknown"),
        "input_volumes": payload.get("input_volumes", {}),
        "candidates": candidates,
        "by_id": by_id,
        "by_probe": by_probe,
        "problems": problems,
        "per_candidate": per_candidate,
        "matched_keys": matched_keys,
        "verdicts": verdicts,
        "total_candidates": total_candidates,
        "scored": len(per_candidate),
        "unscored": total_candidates - len(per_candidate),
        "recall": len(matched_keys) / len(key_rows),
        "precision": precision_num / total_candidates if total_candidates else 0.0,
        "precision_num": precision_num,
        "by_type": by_type,
        "by_source": by_source,
        "multi": sorted(cid for cid, e in per_candidate.items() if len(e["key_ids"]) > 1),
    }


def provenance_lines(provenance, key_rows):
    lines = ["## Key provenance", ""]
    if provenance and provenance.get("assembled_by"):
        lines.append(f"- Assembled by: {provenance.get('assembled_by')}")
        lines.append(f"- Assembled on: {provenance.get('assembled_on') or 'not recorded'}")
        lines.append(f"- Method: {provenance.get('method') or 'not recorded'}")
        searched = provenance.get("web_search_used")
        if searched is True:
            lines.append("- Web search used: **yes**. The key may be contaminated by "
                         "published writing about this project. Read the recall numbers "
                         "with that in mind.")
        elif searched is False:
            lines.append("- Web search used: no")
        else:
            lines.append("- Web search used: not recorded")
        sources = provenance.get("source_documents") or []
        lines.append(f"- Source documents: {', '.join(sources) if sources else 'not recorded'}")
        claimed = provenance.get("rows")
        if isinstance(claimed, int) and claimed and claimed != len(key_rows):
            lines.append(f"- Row count: provenance says {claimed}, the key file has "
                         f"{len(key_rows)}. They disagree.")
        if provenance.get("notes"):
            lines.append(f"- Notes: {provenance['notes']}")
    else:
        lines.append("Not recorded. `key/provenance.json` is missing or still a stub, so "
                     "there is no record of which model assembled this key or when.")
    lines.append("")
    return lines


def recall_by(buckets, heading, column):
    lines = [f"## Recall by {heading}", "", f"| {column} | Recovered | Of | Recall |",
             "| --- | --- | --- | --- |"]
    for name in sorted(buckets):
        hit, total = buckets[name]
        lines.append(f"| {name} | {hit} | {total} | {hit / total:.0%} |")
    lines.append("")
    return lines


def memory_split(by_source):
    """Recall against rules recalled unaided, against rules found in a document.

    The key is assembled memory first, before any document is opened, so rows sourced
    to 'head' are what the operator could produce without looking anything up. That
    door only opens once, and the split is worth reporting on its own.
    """
    remembered = by_source.get("head")
    if not remembered:
        return []
    hit, total = remembered
    other_hit = sum(h for name, (h, _) in by_source.items() if name != "head")
    other_total = sum(t for name, (_, t) in by_source.items() if name != "head")
    lines = ["### Remembered against written down", ""]
    lines.append(f"- Rules recalled unaided: {hit} of {total} recovered, "
                 f"{hit / total:.0%}")
    if other_total:
        lines.append(f"- Rules found in a document: {other_hit} of {other_total} "
                     f"recovered, {other_hit / other_total:.0%}")
    lines.append("")
    return lines


def score_run(run_dir: Path, key_dir: Path):
    run_dir, key_dir = Path(run_dir), Path(key_dir)
    key_rows, digest, frozen, provenance = load_key(key_dir)
    t = tally(run_dir, key_rows)

    unrecovered = [row for row in key_rows if row["key_id"] not in t["matched_keys"]]
    novel = [(cid, "; ".join(t["per_candidate"][cid]["notes"]))
             for cid in sorted(t["per_candidate"])
             if t["per_candidate"][cid]["verdict"] == "NEW"]

    lines = []
    add = lines.append
    add(f"# Score, {run_dir.name}")
    add("")
    add(f"Profile: {t['profile']}")
    add(f"Key frozen and unmodified: {frozen}")
    add(f"Key sha256: `{digest}`")
    add("")
    lines.extend(provenance_lines(provenance, key_rows))
    if t["unscored"]:
        add(f"> {t['unscored']} of {t['total_candidates']} candidates carry no verdict. "
            f"Precision below counts them against the battery, which is the honest "
            f"reading of an unfinished match.csv.")
        add("")
    if t["problems"]:
        add("## Problems in match.csv")
        add("")
        for problem in t["problems"]:
            add(f"- {problem}")
        add("")

    v = t["verdicts"]
    add("## Headline")
    add("")
    add("| Measure | Value | Of |")
    add("| --- | --- | --- |")
    add(f"| Recall | {t['recall']:.0%} | {len(t['matched_keys'])} of {len(key_rows)} key rows |")
    add(f"| Precision | {t['precision']:.0%} | {t['precision_num']} of {t['total_candidates']} candidates |")
    add(f"| Novelty | {v['NEW']} | real constraints the key did not contain |")
    add(f"| False | {v['FALSE']} | candidates that were not constraints |")
    add("")
    if t["multi"]:
        add(f"{len(t['multi'])} candidate(s) recovered more than one key row. Each is "
            f"counted once in precision and credits every key row it named:")
        add("")
        for cid in t["multi"]:
            add(f"- {cid} covers {', '.join(t['per_candidate'][cid]['key_ids'])}")
        add("")
    if v["NEW"]:
        add(f"Novelty is the number that matters. {v['NEW']} constraint(s) here are real "
            f"and a two year manual effort did not write them down.")
        add("")

    lines.extend(recall_by(t["by_type"], "constraint type", "Type"))
    lines.extend(recall_by(t["by_source"], "source", "Source"))
    lines.extend(memory_split(t["by_source"]))

    add("## New constraints found")
    add("")
    if novel:
        for cid, note in novel:
            add(f"- **{cid}** ({t['by_id'][cid]['proposed_type']}) {t['by_id'][cid]['statement']}")
            if note:
                add(f"  - {note}")
    else:
        add("None.")
    add("")

    add("## Unrecovered key rows")
    add("")
    add("This list is the interview.")
    add("")
    if unrecovered:
        for row in unrecovered:
            add(f"- **{row['key_id']}** ({(row.get('type') or '').strip()}) "
                f"{(row.get('statement') or '').strip()}")
    else:
        add("None. Every key row was recovered.")
    add("")

    text = "\n".join(lines) + "\n"
    (run_dir / "score.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


def compare_runs(rich_dir: Path, lean_dir: Path, key_dir: Path, out_dir=None):
    """Report the delta between two runs of the same probes on different profiles.

    The delta is the finding. The full export is far more structured than a typical
    target business will ever be, so what survives the degradation is what the battery
    can be expected to find at the next client.
    """
    rich_dir, lean_dir, key_dir = Path(rich_dir), Path(lean_dir), Path(key_dir)
    key_rows, digest, frozen, provenance = load_key(key_dir)
    a = tally(rich_dir, key_rows)
    b = tally(lean_dir, key_rows)

    lines = []
    add = lines.append
    add(f"# Delta, {rich_dir.name} against {lean_dir.name}")
    add("")
    add(f"- Richer run: `{rich_dir.name}`, profile {a['profile']}")
    add(f"- Leaner run: `{lean_dir.name}`, profile {b['profile']}")
    add(f"- Key frozen and unmodified: {frozen}")
    add(f"- Key sha256: `{digest}`")
    add("")
    if a["profile"] == b["profile"]:
        add(f"> Both runs carry the profile {a['profile']!r}. A delta between two runs of "
            f"the same profile measures nothing about degradation.")
        add("")
    lines.extend(provenance_lines(provenance, key_rows))

    for label, t in ((rich_dir.name, a), (lean_dir.name, b)):
        if t["unscored"]:
            add(f"> {label}: {t['unscored']} of {t['total_candidates']} candidates carry "
                f"no verdict, counted against precision.")
    if a["unscored"] or b["unscored"]:
        add("")

    add("## Headline")
    add("")
    add("| Measure | Richer | Leaner | Change |")
    add("| --- | --- | --- | --- |")
    add(f"| Recall | {a['recall']:.0%} | {b['recall']:.0%} | "
        f"{(b['recall'] - a['recall']) * 100:+.0f} points |")
    add(f"| Precision | {a['precision']:.0%} | {b['precision']:.0%} | "
        f"{(b['precision'] - a['precision']) * 100:+.0f} points |")
    add(f"| Novelty | {a['verdicts']['NEW']} | {b['verdicts']['NEW']} | "
        f"{b['verdicts']['NEW'] - a['verdicts']['NEW']:+d} |")
    add(f"| Candidates | {a['total_candidates']} | {b['total_candidates']} | "
        f"{b['total_candidates'] - a['total_candidates']:+d} |")
    add("")

    add("## Input volumes")
    add("")
    add("| Landing table | Richer | Leaner |")
    add("| --- | --- | --- |")
    for table in sorted(set(a["input_volumes"]) | set(b["input_volumes"])):
        add(f"| {table} | {a['input_volumes'].get(table, 0):,} | "
            f"{b['input_volumes'].get(table, 0):,} |")
    add("")

    add("## Candidates by probe")
    add("")
    add("| Probe | Richer | Leaner |")
    add("| --- | --- | --- |")
    for probe in sorted(set(a["by_probe"]) | set(b["by_probe"])):
        add(f"| {probe} | {a['by_probe'].get(probe, 0)} | {b['by_probe'].get(probe, 0)} |")
    add("")

    add("## Which constraint types survive the degradation")
    add("")
    add("| Type | Richer | Leaner | Survives |")
    add("| --- | --- | --- | --- |")
    for ktype in sorted(set(a["by_type"]) | set(b["by_type"])):
        ah, at = a["by_type"].get(ktype, [0, 0])
        bh, bt = b["by_type"].get(ktype, [0, 0])
        total = at or bt or 1
        if ah and bh:
            verdict = "yes" if bh >= ah else f"**partly, {ah - bh} lost**"
        elif ah and not bh:
            verdict = "**no, lost entirely**"
        elif not ah and bh:
            verdict = "only in the leaner run"
        else:
            verdict = "neither run found it"
        add(f"| {ktype} | {ah}/{total} | {bh}/{total} | {verdict} |")
    add("")

    add("## Which sources survive the degradation")
    add("")
    add("| Source | Richer | Leaner | Survives |")
    add("| --- | --- | --- | --- |")
    for ksource in sorted(set(a["by_source"]) | set(b["by_source"])):
        ah, at = a["by_source"].get(ksource, [0, 0])
        bh, bt = b["by_source"].get(ksource, [0, 0])
        total = at or bt or 1
        if ah and bh:
            verdict = "yes" if bh >= ah else f"**partly, {ah - bh} lost**"
        elif ah and not bh:
            verdict = "**no, lost entirely**"
        elif not ah and bh:
            verdict = "only in the leaner run"
        else:
            verdict = "neither run found it"
        add(f"| {ksource} | {ah}/{total} | {bh}/{total} | {verdict} |")
    add("")

    lost = [row for row in key_rows
            if row["key_id"] in a["matched_keys"] and row["key_id"] not in b["matched_keys"]]
    gained = [row for row in key_rows
              if row["key_id"] in b["matched_keys"] and row["key_id"] not in a["matched_keys"]]

    add("## Recovered in the richer run, lost in the leaner one")
    add("")
    add("This is the deliverable for the next client. Each line names something the "
        "battery can only find if the business is instrumented to produce it.")
    add("")
    if lost:
        for row in lost:
            add(f"- **{row['key_id']}** ({(row.get('type') or '').strip()}) "
                f"{(row.get('statement') or '').strip()}")
            add(f"  - found by: {', '.join(a['matched_keys'][row['key_id']])}")
    else:
        add("Nothing. Every key row the richer run recovered survived the degradation.")
    add("")

    if gained:
        add("## Recovered in the leaner run only")
        add("")
        add("Unexpected. Worth understanding before trusting either number.")
        add("")
        for row in gained:
            add(f"- **{row['key_id']}** {(row.get('statement') or '').strip()}")
            add(f"  - found by: {', '.join(b['matched_keys'][row['key_id']])}")
        add("")

    only_rich = sorted(set(a["by_id"]) - set(b["by_id"]))
    only_lean = sorted(set(b["by_id"]) - set(a["by_id"]))
    add("## Candidates present in one run only")
    add("")
    if only_rich:
        add(f"Only in `{rich_dir.name}` ({len(only_rich)}):")
        add("")
        for cid in only_rich:
            add(f"- {cid}")
        add("")
    if only_lean:
        add(f"Only in `{lean_dir.name}` ({len(only_lean)}):")
        add("")
        for cid in only_lean:
            add(f"- {cid}")
        add("")
    if not only_rich and not only_lean:
        add("Both runs produced the same candidate ids.")
        add("")

    text = "\n".join(lines) + "\n"
    target = Path(out_dir) if out_dir else rich_dir
    target.mkdir(parents=True, exist_ok=True)
    (target / "delta.md").write_text(text, encoding="utf-8")
    print(text)
    return 0
