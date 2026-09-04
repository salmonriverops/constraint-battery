# Pass A: Slack, everything

Same window and channels as Pass H (2026-07-14 to 2026-08-01 MDT, 32 channels, no DMs). Pass H was frozen and checksummed before this pass started and was not revised. Pass A files: `constraints_A.csv` (SA001 to SA062), `override_events_A.csv` (EA001 to EA067), `four_fields_A.csv`, `recurring_types_A.csv`, `metrics_A.json`. In this published copy the two CSVs naming rows and events are withheld and this report is redacted; see the README for what was removed and why.

Numbering: SA001 to SA048 are the Pass H rows renumbered, marked `[also in Pass H]` in notes. SA049 to SA062 are rows that needed the automation. EA001 to EA049 are the Pass H events; EA050 to EA067 are the 18 events that needed the automation, marked in `four_fields_A.csv` by their recurring kind and listed below. One of the 18 (EA052, the two-wave push logger) had its human half visible in Pass H and was missed there; it is flagged in the CSV and excluded from the gap arithmetic below.

## What the automation is

531 messages from integrations, in seven families: the dispatch board (Zapier into #field-comms: 49 push acknowledgements, 92 driver pickup alerts, 52 photographer alerts, 6 "no driver assigned" alerts, 6 manual heads-ups), the booking feed (96), trip manifests posted under the GM's account (84, of which 13 are updates with a one-line change note), the reviews feed (30), the inquiries feed (21), the daily conditions post (20), the SMS relay that mirrors guides' texts to the field-comms phone number into Slack (20), the food-allergy digests (18), unpaid-balance reports (16), the Airtable issue and time-off forms (15), phone digests (4) and two Slackbot deletions. 499 of the 531 count as operational (reviews and deletions do not).

The prompt's concern was the conflict checker reading the answer key out loud. In this window its rule-bearing output is small: six "no driver assigned" alerts on two days, and the landing-time estimates. There were no "clear, no conflicts" style posts in the window. Most of the automation volume is feeds (bookings, manifests, balances, SMS) rather than rule evaluation.

## 1. Constraints

62 rows: 48 carried from Pass H plus 14 A-only. Where the 14 came from: dispatch board 2 (SA051 driver must be assigned, SA052 shuttle timing model), manifest feed 2 (SA049 manifest timing, SA050 waiver tracking), issue form 1 (SA053 severity scheme), time-off form 1 (SA054), balance report 1 (SA055 deposit and review cadence), allergy digest 1 (SA056), SMS relay 3 (SA057 nightly camp report, SA058 jet boat confirmation, SA059 fuel card), booking feed 1 (SA060 bookings open to day-of), conditions feed 2 (SA061 Murtaugh on released water only, SA062 the "technical" flow threshold, both needing a human message to give the number meaning).

Only SA051 is the rule engine stating one of the rules it checks. SA052 is the engine's timing model, useful but not an operating constraint in the baseline sense. The other twelve A-only rows are process facts that a human wrote into a form, a text message, or a booking, and that an integration then carried into Slack.

## 2. Override events

67 events: 36 high, 20 medium, 11 low. 18 are A-only (5 high, 8 medium, 5 low). Where the A-only events came from: SMS relay 5, issue form 5, dispatch alerts and acknowledgements 4, balance reports 2, time-off form 1, manifest feed 1.

The five A-only high-confidence events: the no-driver alert on Jul 18 resolved by sending the contract bus driver (EA050); the phantom no-driver alert on Jul 20 dismissed as a test artefact (EA051); the Pittsburg van arranged overnight for a family that missed the jet boat shuttle (EA056); a vehicle kept in service for several days after a high-severity fault entry (EA060); a trip running on its launch day with a balance outstanding (EA066).

Rates. On the pre-registered definition, high-confidence events per 100 operational messages in the pass's own universe: Pass A is 36 / 1,043 = 3.5, against Pass H 5.7 and GroupMe 5.3. Including automation more than doubles the operational denominator (499 feed messages) while adding five high-confidence events, so the density falls. On the alternative reading, holding the denominator at the 544 human operational messages and asking how many more decisions the automation let the session see, Pass A is 36 / 544 = 6.6, a gain of 0.9 per 100 over Pass H. Both numbers are in the CSVs' companion `metrics_A.json`; the first is the one the prompt asked for.

## 3. The four fields

All 67 events: entity 97 percent, rule 82 percent, actor 76 percent, lead time 87 percent.

The 18 A-only events alone: entity 100 percent, rule 89 percent, actor 56 percent, lead time 94 percent. Automation makes the entity and the clock nearly free (every alert names the trip and the minute) and makes the rule easier to name (the form or alert carries its own category). It makes the actor harder to recover: an SMS relay shows who raised the problem, the answer came by phone; an issue-form post shows who logged the fault, not who decided to keep driving; a balance report shows the debt, not who chose to run the trip anyway. Eight of the eighteen have no visible decider, against eight of forty-nine in Pass H.

## 4. Recurring types

New kinds that only appear with automation: dispatch gap filled at the last minute (1), automation false alarm dismissed (1), automation limit worked around by hand (2), confirmation chased the night before (1), deposit rule waived (2), waiver gap accepted routinely (1), vehicle fault checked and cleared (1). The existing kinds that grew: vehicle fault with restricted use accepted (4 to 6), vehicle or bus capacity shortfall worked around (5 to 6), guest rendezvous problem (1 to 2), decision visible but outcome not stated (8 to 12).

That last one matters: automation surfaces more open questions than it closes. Five of the twelve unresolved cases are A-only (two vehicle fault entries, a time-off request, a fire question by SMS, two missing guest cars by SMS).

## 5. Volume and what defeated the pass

Totals: 1,204 messages, 1,043 operational (544 human, 499 automation). By channel kind, automation sits almost entirely in four places: #field-comms 227, the private feeds (#new-bookings 96, #new-inquiries 21) 117, per-trip channels 56 (manifests), and #reviews-riggins 30; the rest is #0-team-hagerman 28 (Hagerman manifests), #management-riggins 22, #conditions 20, #food 18, #ops-issues 13.

Where a decision was visibly being made and the pass could not tell what it was, beyond the Pass H list: whether the two guest cars that never reached the French Creek launch on Jul 16 were found (EA054); what was done about a trailer's high-severity fault entry (EA059); whether a vehicle's fault entry changed its use (EA062); whether the Aug 5 to 7 blackout and the Aug 23 last day were approved (EA064); and what the Main Salmon crew was told about the smoke at Mackay Bar on Jul 25 (EA058). All five have the same shape: an integration delivered the question into Slack, and the answer went back through the channel the question came from (a phone, a form, a face-to-face), which Slack never saw.

Two further limits. The dispatch board posted duplicate alerts (identical pairs at 11:53, 12:02, 14:58, 15:07, 16:13 and 16:22 on several days) and once ingested a human correction ("This is wrong, went off of 10 am") as a trip name; counting alerts as operational messages therefore over-states the automation's information content. And the manifests and allergy digests carry guest names, medical flags and reservation codes; nothing from them is quoted here beyond counts and the one-line change notes.

## The gap between H and A

| measure | Pass H | Pass A | gap |
|---|---:|---:|---:|
| operational messages | 544 | 1,043 | +499 |
| constraint rows beyond baseline | 48 | 62 | +14 |
| override events | 49 | 67 | +18 (+17 net of the one missed in H) |
| high-confidence events | 31 | 36 | +5 |
| high per 100 operational (pass's own universe) | 5.7 | 3.5 | -2.2 |
| high per 100 human operational | 5.7 | 6.6 | +0.9 |
| entity recoverable | 96 % | 97 % | +1 |
| rule recoverable | 80 % | 82 % | +2 |
| actor recoverable | 84 % | 76 % | -8 |
| lead time recoverable | 84 % | 87 % | +3 |

Decomposition of the 17 net A-only events by what carried them: relayed human text messages 5, humans filling the issue form 5, the dispatch rule engine 3 (2 high), balance reports 2 (1 high), manifest feed 1, time-off form 1. Of the 14 A-only constraints, 2 come from the rule engine and 12 from feeds and forms.

The prediction said Pass A would reach 25 per 100 and that a gap of 10 points over H would mean the advantage was the operator's tooling. Neither happened. The tooling adds about a sixth more high-confidence events and a third more rules, almost all of it from integrations that carry human input (texts, forms, bookings) rather than from the rule engine. On the density measure the tooling does not pull ahead; it dilutes.

## Provenance

```json
{
  "pass": "A",
  "assembled_by": "Claude (Cowork session), same session as Pass H, run after Pass H was frozen",
  "assembled_on": "2026-09-04",
  "web_search_used": false,
  "window": "2026-07-14 00:00 to 2026-08-01 23:59 MDT, 19 days",
  "channels_read": 32,
  "messages_total": 1204,
  "messages_operational": 1043,
  "messages_from_bots_excluded": 0,
  "constraint_rows": 62,
  "override_events": 67,
  "override_events_high_confidence": 36,
  "entity_recoverable_pct": 97,
  "rule_recoverable_pct": 82,
  "actor_recoverable_pct": 76,
  "lead_time_recoverable_pct": 87,
  "notes": "constraint_rows and override_events include the Pass H rows renumbered (48 and 49); A-only additions are 14 rows and 18 events, one of which (EA052) was H-visible and missed in H. Operational automation = all integration posts except the 30 review-feed posts and 2 Slackbot deletions. Automation read in full for non-templated families (SMS relay, issue/time-off forms, no-driver alerts, manifest change notes, allergy digests, balance reports, phone digests, inquiries); templated dispatch alerts, booking posts and conditions posts were read by pattern and counted. Rate on the pre-registered denominator is 3.5; on the human-operational denominator it is 6.6."
}
```
