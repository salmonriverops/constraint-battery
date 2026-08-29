# Constraint discovery battery

An analysis tool, not a product. It reads an export of one business's operational
data and produces a list of candidate constraints for a human to confirm or reject.

Probes emit candidates. Only a human creates a constraint.

## Run it

    pip install duckdb
    python3 cli.py load <export_dir>          # validate against the denylist, load into duckdb
    python3 cli.py run  --out runs/$(date +%F) # run all probes, write candidates.json
    python3 cli.py score runs/$(date +%F)      # after match.csv is filled in, write score.md

No server. DuckDB over flat exports, so it runs on a laptop in somebody else's
office. Postgres is for the eventual client install, which is a different tool.

`tools/make_fixture.py` writes a synthetic export with known structure planted in it,
for exercising the battery without real data.

## No business data in git

`data/`, `runs/*/export/`, `*.duckdb` and `*.labelmap.json` are gitignored, and have
been since the first commit. Code in git, data on disk. If you find yourself about to
commit a CSV of real records, stop.

## The landing schema

Six tables, in `schema/001_landing.sql`. This is the asset.

| Table | What it holds |
| --- | --- |
| `work` | what happened, when, where, for how many customers |
| `resources` | who and what is available to do it |
| `assignments` | which resource did which work, in which role, over which window |
| `locations` | where |
| `location_travel` | how long between two locations |
| `changes` | what was changed after being set, when and by whom |

Resist adding a seventh. If a business seems to need one, say so rather than adding it.

`kind` and `role` are free strings: "person", "vehicle", "trailer", "bay", "room";
"Lead Guide", "Painter", "Charge Nurse". No probe branches on a specific value of
either. If one needs to, the probe is wrong.

`money` is deliberately omitted from version one.

## The denylist, and why it exists

Some source tables are the answer key: the conflict rules, the thresholds, the trip
type rules, the capacity tiers, the movement types, the day cap locks, the automation
registry, and anything from the conflict checker or the dispatch board.

Loading any of them makes this an open-book exam that proves nothing. The battery is
supposed to rediscover those rules from the transaction records alone. If it is handed
them, a perfect score means only that it can read.

The loader checks every file in the export directory against the denylist before
reading a byte, and refuses the whole run on a match. There is no override flag. The
full list, and the field-level extension covering the override log, is in
`extract/README.md`.

## The four probes

| Probe | What it looks for | Types |
| --- | --- | --- |
| `p03_exclusivity` | one resource in two places at once, and the gap distribution between consecutive jobs | exclusivity, turnaround |
| `p04_ceilings` | the right edge of every countable dimension: a taper is a business limit, a cliff is a rule | capacity |
| `p05_population` | fields always filled for one partition and never for another | dependency, exemption |
| `p08_overrides` | what gets changed after being set, how often, by whom, how long before the work | any |

Every probe is deterministic. Same input, same candidates, same order, byte for byte.
`candidates.json` carries no wall clock for that reason; the run timestamp lives in
`run_meta.json` beside it.

Every probe is guarded. Minimum volumes are configurable and default conservative: a
resource needs at least 20 assignments, a work_type at least 10 instances, a field at
least 50 populated rows. Every candidate carries the volumes it passed, under
`confidence_inputs`, so you can see what it is standing on.

## Scoring, in three steps and in this order

1. **Freeze the key.** Assemble `key/answer_key.csv` from the constraint inventory,
   hash it into `key/key_hash.txt`, commit both, before any run.
2. **Pre-register.** Run the battery and commit `candidates.json` before matching
   begins. That commit is the pre-registration and its timestamp is the evidence.
   `cli.py run` cannot read `key/`: an audit hook aborts the run if anything tries.
3. **Match candidate by candidate.** Read a candidate, decide what it matches, move
   on. Never scan the key for something a candidate might fit. That ordering is the
   whole defence against grading your own work, and reversing it invalidates the
   result.

`score/score.py` then reports recall, precision, novelty, recall by constraint type,
and the unrecovered key rows. That last list is the interview.

Assembling the key and filling in `match.csv` is hand work. There is no matcher in
this codebase and there should never be one. The protocol is in `key/README.md`.
