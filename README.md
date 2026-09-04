# Constraint discovery battery

An analysis tool, not a product. It reads an export of one business's operational
data and produces a list of candidate constraints for a human to confirm or reject.

Probes emit candidates. Only a human creates a constraint.

## Run it

    pip install duckdb
    export AIRTABLE_TOKEN=pat...              # a token with data.records:read on the base
    python3 tools/export_airtable.py --base appXXXXXXXXXXXXXX --out data/export
    python3 cli.py load data/export           # validate against the denylist, load into duckdb
    python3 cli.py run  --out runs/$(date +%F) # run all probes, write candidates.json
    python3 cli.py score runs/$(date +%F)      # after match.csv is filled in, write score.md

No server. DuckDB over flat exports, so it runs on a laptop in somebody else's
office. Postgres is for the eventual client install, which is a different tool.

`tools/export_airtable.py` pulls the export. Airtable's built in CSV export is not
usable: it omits record ids and renders linked records as display names, so resources
would load with no id and the join from assignments to resources would collapse. The
exporter goes through the REST API instead. What it fetches is derived from
`extract/airtable_map.json`, so it cannot drift from the adapter, and it requests only
the columns the map names. `--dry-run` prints the plan without fetching.

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

## Two profiles, and why the delta is the finding

The full export is far more structured than a typical target business will ever be.
Two years of schema work went into it. A normal client has booking transaction
history, maybe an assignment record, message threads, and some SOPs in a document
nobody reads.

So the battery runs twice on the same probes, and the delta is the real result.

    python3 tools/export_airtable.py --base app... --out data/export   # once
    python3 cli.py load data/export --profile full --db battery-full.duckdb
    python3 cli.py load data/export --profile lean --db battery-lean.duckdb
    python3 cli.py run --db battery-full.duckdb --out runs/<date>-full
    python3 cli.py run --db battery-lean.duckdb --out runs/<date>-lean
    python3 cli.py score --compare runs/<date>-full runs/<date>-lean

Export once, load twice. Exporting twice would let the source data change between
pulls, and the delta would then be measuring that drift as well as the degradation.
One export means both runs provably read identical bytes.

The cut list is in `extract/profiles.py`, declarative, with the reasoning for each
line. The principle: drop anything that exists because the operator built it rather
than because the operation produced it.

The six table schema never changes between profiles. A dropped table is present and
empty, a dropped column is present and null. That is the honest model of a leaner
client, and it means p05, which measures fill rates, sees the thinning rather than
being blinded to it.

Both runs get committed before matching, and each needs its own `match.csv`.
`delta.md` reports recall and precision side by side, which constraint types survive,
and the key rows recovered in the richer run but lost in the leaner one. That last
list is the deliverable for the next client: it names what a business has to be
instrumented to produce before the battery is worth running on it.

## Handing this to someone else

`BRIEFING.md` explains the project to a fresh session, for review or code work.
`key/ASSEMBLE_PROMPT.md` is a separate prompt for getting help writing the answer key,
deliberately withholding what the probes look for. Use that one in a session that has
not read the briefing, for the reason it explains.

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
