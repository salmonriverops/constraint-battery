# The key, and the protocol

The key is the list of constraints already known from the constraint inventory. It
exists to score the battery, not to guide it.

`answer_key.csv` has the columns `key_id, type, statement, source, notes`. Assembling
it, and filling in `match.csv` afterwards, is hand work. There is no matcher in this
codebase and there should never be one.

## The three steps, in order

**1. Freeze the key.** Assemble `answer_key.csv` from the constraint inventory. When
it is complete, hash it and commit both files before any run.

    shasum -a 256 key/answer_key.csv | cut -d' ' -f1 > key/key_hash.txt
    git add key/answer_key.csv key/key_hash.txt
    git commit -m "Freeze the answer key"

`score.py` recomputes the hash and says in `score.md` whether the key still matches
what was frozen. A key edited after a run is a key that has been graded against.

Commit `key/provenance.json` at the same time. It records which model assembled the
key, on what date, from which documents, and whether web search was used. `score.md`
prints it on every run, so that record lives in the protocol rather than in memory.
Web search matters because published writing about this project describes the
constraint taxonomy and several findings, and a session that read it is contaminated.
See `ASSEMBLE_PROMPT.md`.

**2. Pre-register the run.** Execute `cli.py run` and commit `candidates.json`
before matching begins.

    python3 cli.py run --out runs/$(date +%F)
    git add runs/$(date +%F)/candidates.json
    git commit -m "Pre-registration: candidates for $(date +%F)"

That commit is the pre-registration and its timestamp is the evidence. `cli.py run`
cannot read `key/`. It is not asked not to, it is prevented: an audit hook aborts the
run if anything under `key/` is opened.

**3. Match, candidate by candidate.** Read a candidate, decide what it matches, move
on. Never scan the key looking for something a candidate might fit.

That ordering is the whole defence against grading your own work. Going key row by
key row instead invites you to find a candidate that could be read as matching, and
it invalidates the result.

Verdicts, one per candidate:

- `MATCH`, with a `key_id`. This candidate says the same thing as that key row.
- `NEW`. This is a real constraint and it is not in the key. These are the finds.
- `FALSE`. This is not a constraint.

Leave a candidate blank only if you have not got to it yet. `score.md` counts blanks
against precision, because an unfinished match is not a good result.

**One candidate can recover several key rows.** A probe states a rule once, in general
terms, where your inventory may hold one row per case. When a single candidate covers
more than one key row, write one `match.csv` row per pairing, repeating the
`candidate_id`:

    p04-ceiling-customers-per-work,K001,MATCH,covers both trip lengths
    p04-ceiling-customers-per-work,K002,MATCH,

Every key row named is credited to recall. The candidate is counted once in precision,
not once per pairing. `score.md` lists which candidates did this, so the effect on the
numbers is visible rather than buried.

This is what lets you write the key at whatever granularity your inventory actually
uses. Do not flatten real rules together to make the key line up with the probes: that
is tuning the key to the test.

## What the numbers mean

- **Recall.** Key rows with at least one MATCH, over total key rows. Also broken out
  by `type` and by `source`, and `score.md` reports the split between rules recalled
  unaided (`source` of `head`) and rules found in a document. The key is assembled
  memory first for that reason: once you have read your own rule tables you cannot
  un-read them.
- **Precision.** MATCH plus NEW, over total candidates.
- **Novelty.** Count of NEW. Real constraints the battery found that a two-year
  manual effort did not.
- **Unrecovered key rows.** Listed at the bottom of `score.md`. That list is the
  interview: each one is something the business knows and the data does not show.

