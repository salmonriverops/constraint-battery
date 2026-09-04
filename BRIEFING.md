# Briefing: what the constraint battery is and how it is meant to work

Paste this into a fresh Claude session that needs to understand the project. It is
safe for review, code work, or explanation.

It is NOT safe for assembling the answer key. Use `key/ASSEMBLE_PROMPT.md` for that,
and use a session that has not read this file. The reason is in step 3 below.

## What it is

An analysis tool, not a product. It reads an export of one business's operational
data and produces a list of candidate constraints for a human to confirm or reject.

The business is a whitewater rafting outfitter. The point of the exercise is to find
out whether operational constraints can be recovered from transaction records alone,
because if they can, the same battery works on the next client without a two year
manual discovery effort. That is the reusable asset.

Probes emit candidates. Only a human creates a constraint. Nothing in the codebase
asserts that a rule exists.

## Where it lives

Repository `salmonriverops/justinsmith-build`, branch
`claude/constraint-discovery-battery-yozhm3`, directory `constraint-battery/`.

It is deliberately not in the company ops repository. The battery is a personal
reusable asset. The company's production environment and data are the company's
contribution. Keeping that boundary is cheap now and expensive later.

## The three boundaries that are not negotiable

**1. No business data in git.** `data/`, `runs/*/export/`, `*.duckdb` and
`*.labelmap.json` are gitignored, and have been since the first commit. Code in git,
data on disk.

**2. The denylist.** Some source tables are the answer key: Conflict Rules, Config
and Thresholds, Trip Type Rules, Capacity Tiers, Movement Types, Day Cap Locks, the
Automation Registry, and anything from the conflict checker or the dispatch board.
The loader checks every file in the export directory against this list before reading
a byte and refuses the whole run on a match. There is no override flag.

Loading any of them makes this an open book exam that proves nothing. The battery is
supposed to rediscover those rules from transaction records. If it is handed them, a
perfect score means only that it can read.

There is one field level extension. The acknowledgement fields on the operational
tables hold one human override per entry, in the form `label :: who :: date`. The
override history is legitimate evidence. The label is the conflict checker's own rule
name, so the adapter replaces it with an opaque id and writes the id to label map
outside git, to be read after matching rather than before.

**3. The probes never read `key/`.** This is enforced by an audit hook that aborts
the run, not by a comment asking nicely.

## The landing schema

Six tables in `schema/001_landing.sql`: `work`, `resources`, `assignments`,
`locations`, `location_travel`, `changes`. Resist adding a seventh. If a business
seems to need one, say so rather than adding it.

`kind` and `role` are free strings. No probe branches on a specific value of either.
If one needs to, the probe is wrong. `money` is deliberately omitted from version one.

## The probes

Four of them, in `probes/`. Each emits candidates carrying a plain sentence a non
technical person could confirm or deny, the evidence behind it, and the volumes that
make it worth believing. Every probe is guarded against thin data and every probe is
deterministic: same input, same candidates, same order, byte for byte.

Read the files for what each one looks for. That detail is deliberately not repeated
here, because this briefing is meant to be readable by someone who may later help
assemble the answer key, and knowing what the probes look for would let them shape
key statements to match.

## The protocol, and why the order is the whole point

1. **Freeze the key.** `key/answer_key.csv` is the list of constraints already known,
   assembled from the constraint inventory. Hash it into `key/key_hash.txt`. Commit
   both before any run. The scorer recomputes the hash and reports whether the key
   still matches what was frozen.

2. **Pre-register the run.** Execute `cli.py run` and commit `candidates.json` before
   matching begins. That commit is the pre-registration and its timestamp is the
   evidence. `candidates.json` carries no wall clock, so a rerun on the same input is
   byte identical and the commit means what it says.

3. **Match candidate by candidate.** Read a candidate, decide what it matches, move
   on. Never scan the key looking for something a candidate might fit.

That ordering is the entire defence against grading your own work. Reversing it
invites you to find a key row a candidate could be read as matching, and it
invalidates the result.

## Scoring

`score/score.py` reports recall, precision, novelty, recall by constraint type, and
the unrecovered key rows. Recall is key rows with at least one MATCH over total key
rows. Precision is MATCH plus NEW over total candidates, counting each candidate once
however many key rows it recovers. Novelty is the count of NEW: real constraints the
battery found that a two year manual effort did not.

The unrecovered list is the most useful output. Each line is something the business
knows that the data does not show, and that list is the interview.

## What is done and what is next

Done: schema, loader, denylist, the Airtable exporter, four probes, scorer, protocol
docs. The pipeline runs end to end on a synthetic fixture
(`tools/make_fixture.py`) and is deterministic across reruns.

Not done: the answer key is an empty stub, and the exporter's HTTP path has never run
against the live Airtable API. The first real export is also its first test.

## What not to do

- Do not write a matcher. Assembling the key and filling in `match.csv` is hand work,
  by design. An AI deciding MATCH is the measurement, not a step in it.
- Do not load a denylisted table, or add an override flag to let someone.
- Do not commit anything under `data/` or `runs/*/export/`.
- Do not add a seventh landing table. Say the business needs one instead.
- No em dashes in code comments, docs or output.
