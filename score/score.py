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


def score_run(run_dir: Path, key_dir: Path):
    run_dir, key_dir = Path(run_dir), Path(key_dir)
    key_path = key_dir / "answer_key.csv"
    hash_path = key_dir / "key_hash.txt"
    match_path = run_dir / "match.csv"
    candidates_path = run_dir / "candidates.json"

    for path in (key_path, match_path, candidates_path):
        if not path.exists():
            raise SystemExit(f"missing {path}")

    key_rows = read_csv(key_path)
    if not key_rows:
        raise SystemExit(f"{key_path} has no rows. Assemble and freeze the key first.")

    digest = hashlib.sha256(key_path.read_bytes()).hexdigest()
    if hash_path.exists():
        recorded = hash_path.read_text(encoding="utf-8").split()[0].strip()
        frozen = "yes" if recorded == digest else "NO, THE KEY HAS CHANGED SINCE IT WAS FROZEN"
    else:
        frozen = "NO, key_hash.txt does not exist"

    candidates = json.loads(candidates_path.read_text(encoding="utf-8"))["candidates"]
    by_id = {c["candidate_id"]: c for c in candidates}
    key_by_id = {row["key_id"]: row for row in key_rows}

    matches = read_csv(match_path)
    problems = []
    verdicts, matched_keys, per_candidate = Counter(), defaultdict(list), {}
    for row in matches:
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
        entry = per_candidate.setdefault(
            cid, {"verdict": verdict, "key_ids": [], "notes": []})
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
    multi = sorted(cid for cid, entry in per_candidate.items() if len(entry["key_ids"]) > 1)

    total_candidates = len(candidates)
    scored = len(per_candidate)
    unscored = total_candidates - scored

    recall = len(matched_keys) / len(key_rows)
    precision_num = verdicts["MATCH"] + verdicts["NEW"]
    precision = precision_num / total_candidates if total_candidates else 0.0

    # Recall by constraint type, using the type column in the key.
    by_type = defaultdict(lambda: [0, 0])
    for row in key_rows:
        ktype = (row.get("type") or "(untyped)").strip() or "(untyped)"
        by_type[ktype][1] += 1
        if row["key_id"] in matched_keys:
            by_type[ktype][0] += 1

    unrecovered = [row for row in key_rows if row["key_id"] not in matched_keys]
    novel = [(cid, "; ".join(per_candidate[cid]["notes"])) for cid in sorted(per_candidate)
             if per_candidate[cid]["verdict"] == "NEW"]

    lines = []
    add = lines.append
    add(f"# Score, {run_dir.name}")
    add("")
    add(f"Key frozen and unmodified: {frozen}")
    add(f"Key sha256: `{digest}`")
    add("")
    if unscored:
        add(f"> {unscored} of {total_candidates} candidates carry no verdict. "
            f"Precision below counts them against the battery, which is the honest "
            f"reading of an unfinished match.csv.")
        add("")
    if problems:
        add("## Problems in match.csv")
        add("")
        for problem in problems:
            add(f"- {problem}")
        add("")

    add("## Headline")
    add("")
    add("| Measure | Value | Of |")
    add("| --- | --- | --- |")
    add(f"| Recall | {recall:.0%} | {len(matched_keys)} of {len(key_rows)} key rows |")
    add(f"| Precision | {precision:.0%} | {precision_num} of {total_candidates} candidates |")
    add(f"| Novelty | {verdicts['NEW']} | real constraints the key did not contain |")
    add(f"| False | {verdicts['FALSE']} | candidates that were not constraints |")
    add("")
    if multi:
        add(f"{len(multi)} candidate(s) recovered more than one key row. Each is counted "
            f"once in precision and credits every key row it named:")
        add("")
        for cid in multi:
            add(f"- {cid} covers {', '.join(per_candidate[cid]['key_ids'])}")
        add("")
    if verdicts["NEW"]:
        add(f"Novelty is the number that matters. {verdicts['NEW']} constraint(s) here are "
            f"real and a two-year manual effort did not write them down.")
        add("")

    add("## Recall by constraint type")
    add("")
    add("| Type | Recovered | Of | Recall |")
    add("| --- | --- | --- | --- |")
    for ktype in sorted(by_type):
        hit, total = by_type[ktype]
        add(f"| {ktype} | {hit} | {total} | {hit / total:.0%} |")
    add("")

    add("## New constraints found")
    add("")
    if novel:
        for cid, note in novel:
            add(f"- **{cid}** ({by_id[cid]['proposed_type']}) {by_id[cid]['statement']}")
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
