# Pre-registration

Published to LinkedIn on 2026-09-04, before the answer key was frozen and before any
run. It is committed here so the claim is dated and cannot be quietly revised once the
numbers exist.

---

I am about to run a test on the company I run, and I might not like the answer.

Over about two years I built an operating model of that operation. Rules, constraints,
qualifications, equipment. I built all of this while knowing every answer, because I
run the place.

The question that decides what I am actually building: can rules like those be found
by analysis instead of by memory?

So this week I am pointing a set of analyses at the operation's raw data, with the
rule tables deliberately withheld, and measuring what share of the rules come back
with me out of the room.

Four things make it mean anything. The rule tables are on a denylist the loader
refuses to read, with no override. The candidate list gets committed before I score
it, so the timestamp is the evidence. Matching goes candidate by candidate, never
scanning the answers for something a candidate could be read as fitting. And the
answer key is being assembled by a model that has never seen the analyses or my
working notes.

I am also running it twice. Once on everything we have, and once on only what a normal
business would plausibly produce. Our data is far more structured than most operations
of this size, and the gap between those two numbers is the honest one.

If most of the rules come back, discovery is largely mechanical and this works on
businesses I have never seen.

If very few come back, then what happened here is that I already knew the answers, and
what I have is judgment rather than a method. That is a different business with a
different price on it.

I am posting this before I know, because a test you publish after seeing the result is
not a test.

Numbers coming soon.

If you work on getting rules or requirements out of people, in research or in a
product, I would like to compare notes.

---

## What this commits the project to

Each claim above maps to something in the repository, and each is checkable.

| Claim | Where it lives |
| --- | --- |
| Rule tables on a denylist, no override | `extract/denylist.py`, refused before a byte is read |
| Candidate list committed before scoring | `key/README.md`, step 2 of the protocol |
| Matching candidate by candidate | `key/README.md`, step 3. There is no matcher in the codebase |
| Key assembled by a model that has not seen the analyses | `key/ASSEMBLE_PROMPT.md`, recorded in `key/provenance.json` |
| Run twice, full and lean | `extract/profiles.py`, compared by `cli.py score --compare` |

The numbers, when they exist, go in `runs/<date>-full/score.md`,
`runs/<date>-lean/score.md` and `delta.md`. Whatever they say.

---

## Exposure note, 2026-09-04

On 2026-09-04 the conflict checker source and the dispatch board source were
pasted into the Claude session that built this battery. Both are on the
denylist. They were sent by mistake and were meant for the key assembly
session instead.

What this does not affect. All probe logic, thresholds and the scorer were
committed and pushed on 2026-08-29, six days earlier, in `b2355c6` and
`4af86f6`. The lean profile landed in `0ff7326` on 2026-09-04 at 01:53 UTC,
about two hours before the exposure. Git timestamps are the evidence. No
part of the battery was written or tuned with knowledge of those files.

What it does affect. From this point the build session is no longer a
disinterested party on probe design. Any change after this note that alters
what the battery detects, including any threshold, any new probe or any
change to `probes/base.py`, is a v2 and needs its own pre-registration. It is
not an edit to this one. Mechanical changes such as crash fixes, export
plumbing and CLI wiring are unaffected.

The answer key was assembled in a separate model with no access to this
repository or this session, so the key itself is untouched.

---

## What counts, decided 2026-09-04 before any run

The key holds 74 rows. Thirty-one came from the conflict checker and the
dispatch board. Eleven of those describe how the dispatch tooling behaves
rather than how the operation is constrained, and they sit outside the
headline recall denominator. The headline number is therefore recall over 63
operating constraints. All 74 are still scored and `score.md` reports both.

A row is `scope=interface` when its subject is the software: a warning
threshold, how far ahead of a trip a flag appears, a default used when a
field is blank, a required checkbox, or an exemption from a check. The eleven
are K044, K055, K056, K064, K067, K068, K070, K071, K072, K073 and K074.

Two judgment calls inside that rule, stated so they can be argued with. K066
and K069 both name a minimum gap between jobs and both are enforced as soft
flags. They stayed in the headline denominator because the statement's
subject is the operation and the flag is only how it is surfaced. Someone
could reasonably put them the other way. K073 went out because treating a
zero-guest operation as not running is a reading of a record, not a limit on
the business.

The rule was applied by the session that built the battery, which had by then
been exposed to the denylisted source files. See the exposure note above.
That is the weakest link in this decision, and it is why the split is written
down here with the row ids named, before a number exists, rather than settled
after one.

`answer_key.csv` was frozen at hash `2e8541eb` on 2026-09-04 at 04:07 UTC and
re-frozen at `8ab6bedd` the same day after the duplicate merge, the name
redaction and this scope decision. No run had been executed against real data
at either point. From `8ab6bedd` the key is read-only.

---

## A second run, and why, 2026-09-04

The first run is pre-registered at `3b03f21` (full) and `4598a25` (lean) and
stays in the repository exactly as it is. A second pair of runs follows it,
because the first was built on a mapping error in the loader.

The error. `extract/airtable_map.json` drew the crew on a Daily Op from a
column named `Guide Availability`. That column exists, which is why nothing
failed, but it is empty on all 412 records. The crew actually lives in five
link columns: `Lead Guide (link)`, `Other Guides (link)`, `Drivers (link)`,
`Store Staff` and `Food Crew`. So every guide on every day trip was absent
from `assignments`, and the only people the battery could see on a day trip
were drivers arriving through Rig Assignments.

Why this is a legitimate correction rather than a second attempt at a better
number. It is decidable without looking at any result: a column empty on 412
of 412 records is objectively the wrong column, and the fix would be correct
whether it raised the score or lowered it. It was found while reading a
candidate, not while reading a score. No run has been scored at the time of
writing, and `match.csv` for the first run is partly filled but not tallied.

What does not change. The answer key stays frozen at `8ab6bedd`. No probe
logic, threshold or guard is touched. The only change is which Airtable
columns the adapter reads.

What is reported. Both runs. The first is the result of the battery against a
partial export, the second against a complete one, and the difference between
them is itself a finding about how much the recoverable set depends on the
operation instrumenting its own crew.

Verdicts recorded against the first run are not carried across. The second run
is judged from scratch.

## Confirmed by the operator, 2026-09-04

Nothing in the base links a trip to the boats that ran it. The 60 boats in
`resources` can never appear in `assignments`, so every boat rule in the key
is unrecoverable from this export by construction rather than by any failure
of a probe. This is recorded before scoring so it cannot be offered afterwards
as an excuse for a number.

---

## A corrected verdict, 2026-09-04, after scoring

`p04-ceiling-customers-per-work` was judged NEW in the full run and MATCH
against K012 in the lean run. It is the same candidate with the same statement
in both, so the two verdicts cannot both stand. This was the only inconsistency
between the two sets of verdicts, and it was the sole reason K012 appeared in
the delta as recovered in the leaner run only.

Resolved to MATCH K012 in both runs. The reasoning, recorded by the operator:
127 guests on one job is the busiest figure observed, not a cap, and the
candidate is pointing at the same limit K012 states rather than at a new one.

Effect on the reported numbers. The full run's operating recall moves from 5 of
63 to 6 of 63, and its novelty from 19 to 18. Precision is unchanged at 23 of
29, because MATCH and NEW both count as a correct candidate. The lean run is
unchanged. The correction raises the headline recall, which is worth stating
plainly: it went in the flattering direction, and it was made because the two
runs disagreed with each other rather than because the number was low.

The key was not touched. It remains frozen at `8ab6bedd`. The operator's
revised understanding of the 120 limit, that it applies to French Creek and
SRHAB volume while other day trips may run the same day and the realistic total
is nearer 140, is recorded in `FINDINGS.md` and deliberately not written back
into the key.
