# Defects found after the run was pre-registered

Nothing here is fixed. A change to probe logic changes `candidates.json` and
invalidates the pre-registration commit, so these are written down and carried
into a v2 with its own pre-registration instead.

## p03 counts assignment pairs, not overlapping jobs

Found 2026-09-04 while judging candidates, before scoring.

`_overlaps()` joins `assignments` to itself on `a.assignment_id <
b.assignment_id`. That stops the same pair of assignment rows being counted
twice, but it does not stop the same pair of *jobs* being counted many times.
A person who holds two roles on one trip has two assignment rows against that
trip, so every job overlapping it pairs with both and is counted twice.

It shows in the evidence as mirrored examples: the same resource and the same
two jobs with the same times, appearing once as A over B and once as B over A.

Effect. `overlapping_pairs` overstates how often the situation occurred, and
the candidate statement says "this happened N times", which a reader takes as
N distinct double bookings. The direction of the error is always upward.

What it does not affect. Whether the candidate is emitted at all, and which
resource kinds it is emitted for. Those depend on whether any overlap exists,
not on how many. So the candidate list is unchanged by this defect and the
verdicts recorded against it stay valid.

Fix for v2. Count distinct pairs of work ids per resource, and carry the
assignment roles as evidence rather than as separate rows.

## The map read an empty column for Daily Ops crew

Found 2026-09-04, before any run was scored. Fixed, and the run redone.

`Guide Availability` exists on Daily Ops and is empty on all 412 records. The
crew is in `Lead Guide (link)`, `Other Guides (link)`, `Drivers (link)`,
`Store Staff` and `Food Crew`. The presence check added earlier reported the
column as absent from the export, correctly, but the report was one line among
many and it was read as thin data rather than as a wrong column.

Effect on the first run. No guide on any day trip reached `assignments`.
Anything about who works a trip, how many people a trip takes, or one person
being in two places was measured against drivers alone.

Lesson worth keeping. The loader should probably refuse, not warn, when a
mapped column is absent from every record. A warning that appears next to nine
other warnings is not a signal. Left as a v2 change so it does not alter
behaviour mid protocol.

## work_type on a Movement is a record id, not a name

Found 2026-09-04 while reading `peak work_per_day` output. Not fixed, and
deliberately not re-run. See the reasoning below.

`Movement Type` is a linked record field. `base.links()` normalises a link cell
to a list of record ids, and `work()` takes `ids[0]`, so a Movement's work_type
lands as `recIoNaMNYNiH9vBf` rather than the type's name. Daily Ops trip types
come through a single select, which carries a name, which is why one table
reads properly and the other does not.

Why this is not being fixed mid protocol. The value is used only to partition:
two movements of the same type share the same id exactly as they would share
the same name, so every group, count and candidate is identical either way.
The defect is that the output is unreadable, not that it is wrong. Re-running
for a cosmetic fix would set the precedent that a run is repeated until it
reads better, and one re-run has already happened today for a defect that did
change what was detected. The bar for a second has to be higher than this.

Separately, and not a defect: most Movements have no `Movement Type` at all, so
they land as untyped. That is the data, not the loader.

Fix for v2. Carry the linked record's display name where Airtable supplies one
and fall back to the id, for work_type and for any other label read from a
link.
