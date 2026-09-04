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
