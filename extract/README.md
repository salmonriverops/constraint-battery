# Adapters

One file per source system. An adapter reads an export directory and returns rows
for the six landing tables. It never writes to the database and never reads `key/`.

Current adapters:

- `airtable.py` with its column map in `airtable_map.json`. Edit the map, not the
  code, when the export changes.

## The denylist

These source tables are the answer key. The loader checks every file in the export
directory against this list before reading a single byte, and refuses the whole run
if anything matches.

- Conflict Rules
- Config and Thresholds
- Trip Type Rules
- Capacity Tiers
- Movement Types
- Day Cap Locks
- Automation Registry
- Any source file from the conflict checker or the dispatch board

Loading any of them makes this an open-book exam that proves nothing. The check
lives in `denylist.py` and matches on a normalised name, so `Config / Thresholds.csv`,
`config_thresholds.csv` and `CONFIG-THRESHOLDS.CSV` are all rejected. There is no
override flag. If a run is rejected, remove the file and load again.

## The override log

This is an addition to the written denylist. It was made after inspecting the source
and it is the one place where the table-level list is not enough.

The acknowledgement fields on the operational tables hold one entry per human
override, in the form `<label> :: <who> :: <date>`. The override history is
legitimate operational evidence and `p08` needs it. The label attached to each
override is not: it is the conflict checker's own rule name, which means the raw
field carries answer-key content on an otherwise allowed table.

So the adapter loads the overrides with the label replaced by an opaque id. `p08`
can still rank by frequency, count actors, and measure lead time, because those
signals live in the counts and the dates rather than in the label. The id-to-label
map is written next to the export as `<export>.labelmap.json`, which is gitignored,
and it is meant to be read after matching, not before.

Field-level answer-key columns are listed in `denylist.ANSWER_KEY_FIELDS`.

`--reveal-override-labels` on `cli.py load` turns this off. Using it on a run that
will be scored invalidates the result.

## What may be extracted

Allowed: operational transaction records. What work happened, who and what was
assigned to it, when, where, what changed and when.

Everything else is out of scope for version one. `money` is deliberately omitted.
