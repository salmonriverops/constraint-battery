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
