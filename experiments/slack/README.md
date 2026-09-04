# Slack constraints and overrides experiment: results

Window 2026-07-14 to 2026-08-01 MDT, 19 days, all 32 Slack channels, no DMs, no web, no Airtable, no dispatch board, no booking system. Predictions were saved (`predictions.md`) before any message was read. Pass H was written, checksummed and made read-only before Pass A began. Every post-freeze edit to Pass H is logged in `pass_H/SHA256SUMS_frozen.txt`: a channel-name redaction in the volume table, a corrected lead-time bucket count in the report, and the publication redaction pass described under **What is not published** below. No Pass H event, constraint, rate or conclusion changed in any of them.

## The result in one table

| | GroupMe 2025 (baseline) | Pass H, humans only | Pass A, everything |
|---|---:|---:|---:|
| messages | 235 | 673 | 1,204 |
| operational | 170 | 544 | 1,043 |
| constraints beyond baseline | 10 | 48 | 62 |
| override events | 20 | 49 | 67 |
| high confidence | 9 | 31 | 36 |
| high per 100 operational | 5.3 | 5.7 | 3.5 (6.6 on the human denominator) |
| entity recoverable | unreliable | 96 % | 97 % |
| rule recoverable | unreliable | 80 % | 82 % |
| actor recoverable | role only | 84 % (role) | 76 % (role) |
| lead time recoverable | rarely | 84 % | 87 % |

## Predictions against results

| prediction | predicted | result |
|---|---:|---:|
| Pass H high per 100 operational | 15 | 5.7 |
| Pass H entity recoverable | 20 % | 96 % |
| Pass H lead time recoverable | 26 % | 84 % |
| Pass A high per 100 operational | 25 | 3.5 |
| A minus H gap that would mean "it's the tooling" | 10 points | -2.2 (or +0.9 on the human denominator) |
| Pass H beats GroupMe by at least 10 per 100 | | not supported: margin is 0.4 |
| coverage of 24 withheld rules / 18 findings | 5 / 2 | not scorable in this session; the withheld lists were not provided (and should not have been) |

## What the numbers say

1. Density of decisions per operational message is the same on Slack as on GroupMe. Slack-with-humans found 5.7 high-confidence events per 100 against 5.3. The "move to Slack" argument does not get support from event density.

2. What Slack changes is the fields. Entity went from unreliable to 96 percent and lead time from rare to 84 percent. Two things did that: precise timestamps, and an operator habit of naming the trip and date in the first line of a message. Per-trip channels gave the entity for free where they applied, but only 12 of 49 events lived in per-trip channels; the other 35 were recoverable from the writing habit, not the channel structure.

3. The pre-registered fallback conclusion ("operator tooling is the key change") is not supported either. Adding every integration added 18 events (5 high), 14 constraint rows, and 499 operational messages. On the pre-registered density measure that is a fall from 5.7 to 3.5. The dispatch rule engine itself contributed 2 constraints (one of them the rule it exists to check) and 3 events. The rest of the Pass A gain came from integrations that carry human input into Slack: guides' text messages relayed from the field phone, the vehicle issue form, the balance reports, and the manifests.

4. Automation lowers actor recoverability. The relay, the form, and the report all show who raised a problem; the answer went back through a phone or a form and Slack never saw it. Actor recoverable fell from 84 percent to 76 percent overall and is 56 percent on the A-only events.

5. The honest sentence for the write-up, replacing the pre-registered one: neither Slack nor the operator's tooling raised the number of decisions visible per operational message; Slack raised how much of each decision is recoverable, mostly through timestamps and naming habits, and the tooling adds entity and clock precision at the cost of hiding who decided.

## Caveats that matter

- "Bot" had to be defined by content as well as author, because the manifests, allergy digests and balance lists post under the GM's own account. The rule used is stated in `pass_H/REPORT_H.md`. A different line would move the operational count by a few dozen messages and the rate by a few tenths.
- "High confidence" is this session's judgement of the same scale the GroupMe session used. The two sessions were not calibrated against each other.
- Operational in Pass A counts templated dispatch alerts and booking posts, including duplicate alerts. That is why the density falls. The human-denominator rate (6.6) is the fairer reading of "how many more decisions did the automation let us see"; the pre-registered rate (3.5) is the one the experiment asked for.
- Roles only throughout. Outputs were scanned against the workspace member list, guest names appearing in feeds, phone numbers, reservation codes and Slack IDs.

## What is not published

Two of the six output families are withheld. `constraints_H.csv`, `constraints_A.csv`, `override_events_H.csv` and `override_events_A.csv` are the row-level records: one line per rule and one line per decision, each with the trip, the date, the vehicle or the person's role attached. Read together they identify guests, staff, client groups and specific vehicles on specific days, and several rows carry guest medical information, customers' outstanding balances on identifiable trips, a safety incident, and vehicles operated with known faults. None of that belongs on a public page about a measurement method. The counts, rates and type distributions computed from those rows are published in full, and their frozen SHA-256 hashes are in `pass_H/SHA256SUMS_frozen.txt`, so the withheld files are fixed and could be produced to anyone with a reason to check them.

The two published reports were redacted the same way before release: the vehicle names behind the "vehicle fault, restricted use accepted" count, the head counts behind the "capacity limit stretched" count, the site and outcome framing of one open eligibility question, two vehicle fault entries described by vehicle and date, one customer's unpaid balance on a named trip, and three channel labels (two social, one naming a client group). Removals only. Nothing was added, no number moved, and the redacted files were re-hashed with the reason logged.

## Files

- `predictions.md`: the block as saved before reading.
- `pass_H/`: `REPORT_H.md`, `four_fields_H.csv`, `recurring_types_H.csv`, `volume_table.md` (per-channel), `metrics_H.json`, `SHA256SUMS_frozen.txt`.
- `pass_A/`: `REPORT_A.md`, `four_fields_A.csv`, `recurring_types_A.csv`, `metrics_A.json`.
- Withheld: `constraints_H.csv` (S001-S048), `constraints_A.csv` (SA001-SA062), `override_events_H.csv` (EH001-EH049), `override_events_A.csv` (EA001-EA067). Hashes in `pass_H/SHA256SUMS_frozen.txt`; reasons above.

The `four_fields_*.csv` files are the per-event scoring sheets with the event text removed: event id, four 0/1 recoverability flags, the rule referenced, the confidence grade and the recurring kind. They are what the four-field percentages are computed from, and they carry no names.
