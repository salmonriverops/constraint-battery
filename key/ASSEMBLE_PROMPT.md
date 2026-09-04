# Assembling the answer key with help

You do not have to type the key by hand. You can talk or type your constraints to a
Claude session and have it produce the CSV rows. What matters is which session, and
what it is allowed to know.

## The rule

The session helping you write the key must not have seen the probe code, the
candidates, or a briefing that describes what the probes look for. Its job is
transcription and formatting, not invention.

Use a **fresh session**. Not the one that built the battery, and not one that has read
`BRIEFING.md`. Give it the prompt below plus your own material: the constraint
inventory, screenshots or exports of Conflict Rules, Config and Thresholds, Trip Type
Rules, Capacity Tiers, Day Cap Locks, and anything you know that was never written
down.

Those tables are denylisted for the battery. They are exactly the right source for the
key. That is the whole design: the battery must rediscover from transaction records
what those tables state outright.

## Why the separation matters

A session that knows the battery detects, say, a ceiling on guests per trip will write
key rows shaped like that finding. Recall then measures how well the key was written to
match the probes, which is not a result. Keeping the key assembler ignorant of the
probes is what makes the number mean something.

The reverse contamination does not matter. Once the key is frozen and committed, any
session can see it.

## What AI must not do

Filling in `match.csv` is yours. An AI reading a candidate and a key row and deciding
MATCH is a matcher, and a matcher is the measurement rather than a step in it. Do that
one by hand, candidate by candidate, in the order the protocol sets out.

---

Everything below the line goes into the fresh session.

---

I am assembling a reference list of the operating constraints my business runs under.
It is going into a CSV that I will freeze before running an unrelated analysis. Your
job is to help me get what I know out of my head and my records, and into rows. You
are transcribing and formatting, not inventing.

The business is a whitewater rafting outfitter. Trips, guides, vehicles, trailers,
boats, shuttles between put in and take out points, a season roughly June to
September.

The CSV columns are:

    key_id, type, statement, source, notes

- `key_id`: K001, K002 and so on. Just a handle.
- `type`: a short category. Use consistent words across rows. Classify a row only
  after its statement is written, and never let the categories suggest a rule I did
  not give you.
- `statement`: one plain sentence, as the business states the rule. A non technical
  person should be able to read it and say yes that is true, or no it is not.
- `source`: where it came from. A table name, "inventory", or "head" for rules that
  were never written down.
- `notes`: my doubts, scope limits, questions. Free text, and it is fine to leave
  blank.

How to work with me:

1. Ask me what I have. I may paste tables, describe rules out loud, or ramble. Take
   all of it.
2. For each rule, write the statement in my terms. If I said it vaguely, ask me for
   the number or the scope rather than guessing.
3. Keep the granularity I actually use. If I have a separate limit per trip type,
   that is a separate row. Do not merge distinct rules to make a tidier list.
4. Flag anything I state as a mechanism rather than a limit. "The checker throws an
   error when two guides collide" is not a constraint. "A guide cannot be on two trips
   at once" is. Rewrite mechanisms as limits, or ask me what the underlying limit is.
5. Flag anything that is a preference or a goal rather than a hard limit. Put it in as
   a row if I want, with the doubt recorded in notes.
6. Ask me what is missing. Prompt me by area: people, vehicles, boats, timing between
   jobs, daily volumes, per location limits, required paperwork, who is allowed to do
   what. Do not propose specific rules, ask me open questions about each area.

Rules for you:

- Do not invent constraints. Every row must come from something I told you or gave
  you. If you think of a rule a rafting company might plausibly have, ask me whether
  it applies, and do not write it down unless I say yes.
- Do not guess numbers. If I have not given you one, ask, or leave the statement
  qualitative and note it.
- Aim for completeness over tidiness. A rule I leave out cannot be scored against.
- No em dashes anywhere in your output.

Output the finished rows as CSV I can paste into a file, with the header row included.
Before you produce the final CSV, show me the statements as a numbered list so I can
correct them.
