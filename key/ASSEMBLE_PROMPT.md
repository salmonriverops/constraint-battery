# Assembling the answer key in a different model

The key is the list of constraints you already know, frozen before the battery runs.
It is the marking scheme, not an input. The probes cannot read it.

You do not have to type it by hand. You can talk or type your constraints to an AI
assistant and have it produce the CSV. That is transcription and formatting, which is
fine. Deciding what matches afterwards is not, and stays with you.

## Which assistant, and why it matters

Use a session that has never seen the probe code, the candidate output, this
repository, or your published writing about the project.

A session that knows the battery detects a particular shape will write key rows shaped
like that finding. Recall then measures how well the key was written to match the
probes, which is a mirror rather than a result. Contamination only runs one way: once
the key is frozen and committed, anything may see it.

**Web search is the live risk.** Published writing about this project describes the
constraint taxonomy and several findings. An assistant with search enabled will find
it. The prompt below forbids search, but turn it off in the interface as well if the
tool allows it. Belt and braces.

## What to bring to that session

- The constraint inventory.
- Exports or screenshots of the Airtable rule tables: Conflict Rules, Config and
  Thresholds, Trip Type Rules, Capacity Tiers, Day Cap Locks, Movement Types.
- Anything you know that was never written down anywhere.

Those rule tables are denylisted for the battery and are exactly the right source for
the key. That is the design: the battery has to rediscover from transaction records
what those tables state outright.

## What to do with the output

1. Save the CSV rows as `key/answer_key.csv`, header included.
2. Save the provenance block the session produces as `key/provenance.json`.
3. Hash and commit, before any run:

        shasum -a 256 key/answer_key.csv | cut -d' ' -f1 > key/key_hash.txt
        git add key/answer_key.csv key/key_hash.txt key/provenance.json
        git commit -m "Freeze the answer key"

`score.md` reports the hash check and the provenance on every run, so which model
assembled the key and when is part of the protocol record rather than your memory.

## What the assistant must not do

Filling in `match.csv` is yours. An assistant reading a candidate and a key row and
deciding MATCH is a matcher, and a matcher is the measurement rather than a step in
it. Do that one by hand, candidate by candidate.

---

Everything below this line is self contained. Paste it into the fresh session. It
assumes no access to any repository and no prior context.

---

## Your task

I run a whitewater rafting outfitter in Idaho. I am building a reference list of the
operating constraints my business runs under: the rules that decide whether a given
day's schedule is valid or broken.

Your job is to get what I know out of my head and my records and into a CSV. You are
transcribing, structuring and questioning. You are not inventing.

This list is going to be frozen and used later as the marking scheme for an unrelated
analysis. That is all you need to know about the analysis, and you should not ask
about it or speculate about it, because knowing what it looks for would bias how you
word these rules.

## Hard rules

1. **Do not search the web.** Not for my business, not for rafting industry norms, not
   for anything. If you have a search tool, do not call it. Everything you write must
   come from what I tell you or paste into this conversation. If you think you need
   outside information, ask me instead.
2. **Do not invent constraints.** Every row must trace to something I gave you. If you
   suspect a rule I have not mentioned, ask me an open question about that area. Do
   not write it down unless I confirm it.
3. **Do not guess numbers.** If I have not given you a threshold, ask for it. If I do
   not know it, leave the statement qualitative and record that in the notes.
4. **Do not merge distinct rules** to make a tidier list. If I have a separate limit
   per trip type, that is a separate row.
5. **No em dashes** anywhere in your output.

## Context you need to ask good questions

The operation runs roughly June to September. The moving parts are:

- **Trips**, sold to guests, each with a type, a date, a start and end time, a party
  size, and a status. Some are half day, some full day, some multi day.
- **Guides and staff**, assigned to trips, with certifications, driving eligibility,
  and availability.
- **Vehicles and trailers**, used to move people and boats.
- **Boats**, of various types and capacities.
- **Locations**, put in points, take out points, and bases.
- **Shuttles and movements**, vehicles repositioning between locations around trips.

Do not assume anything about how any of this is limited. Ask.

## Output format

A CSV with exactly these columns:

    key_id,type,statement,source,notes

- **key_id**: K001, K002, K003 and so on. Just a handle. Zero padded to three digits.
- **type**: a short lowercase category. Assign it only after the statement is written.
  Use these where they fit, and invent a new one rather than forcing a bad fit:
  `capacity`, `timing`, `exclusivity`, `eligibility`, `sequencing`, `dependency`,
  `exemption`. Never let this list suggest a rule I did not give you. If a category
  has no rows, that is a real signal, not a gap for you to fill.
- **statement**: one plain sentence, in my terms, stating the limit. A person who runs
  the business should be able to read it and say yes that is true, or no it is not.
- **source**: where it came from. A table or document name, or `inventory`, or `head`
  for rules that were never written down.
- **notes**: my doubts, scope limits, open questions. Often blank.

Quote any field containing a comma.

## What makes a good statement

A constraint limits which schedules are valid. It is not a process step, a goal, a
preference, or a piece of software behaviour.

- Good: "A guide cannot be assigned to two trips whose times overlap."
- Good: "No more than three trips launch from one put in per day."
- Good: "A full day trip carries no more than 18 guests."
- Bad, this is a mechanism: "The conflict checker throws an error when two guides
  collide." Ask me what limit that mechanism is enforcing, and write that instead.
- Bad, this is a preference: "We try to give guides a day off after three in a row."
  Write it as a row if I want it, and record in notes that it is a preference.
- Bad, this is a process step: "The dispatcher reviews the board each morning."

Every statement should in principle be checkable against a record of what actually
happened. If a rule could never be observed as kept or broken in a log of trips and
assignments, flag it to me and put it in with a note.

## How to work with me

1. Ask what I have. I will paste tables, describe rules out loud, and ramble. Take all
   of it.
2. Work through areas one at a time, asking open questions rather than proposing
   rules. Cover at least: people, certifications and eligibility, vehicles, trailers,
   boats, timing between jobs, daily volumes, per location limits, party sizes,
   paperwork and compliance, and who is allowed to do what.
3. After each area, show me the statements you have drafted as a numbered list so I
   can correct them. Do not produce the CSV until I say the whole list is done.
4. Ask me what is missing at the end. Aim for completeness over tidiness. A rule I
   leave out cannot be scored against, and leaving it out flatters the analysis.

## Final output

When I say the list is complete, produce two things.

First, the CSV, header included, in one code block, ready to save.

Second, a provenance block in one code block, as JSON, so I can save it alongside:

    {
      "assembled_by": "<your model name and version, as precisely as you know it>",
      "assembled_on": "<today's date, YYYY-MM-DD, as I have told you or as you know it>",
      "method": "conversational transcription from operator-supplied documents",
      "web_search_used": false,
      "source_documents": ["<list what I actually gave you>"],
      "rows": <number of rows in the CSV>,
      "notes": "<anything about the assembly a reader should know, including any area you think is thin>"
    }

If you did use a search tool at any point, set `web_search_used` to true and say so
plainly. An honest record of contamination is worth more than a clean one that is
wrong.
