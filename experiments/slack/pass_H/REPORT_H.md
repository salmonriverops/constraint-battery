# Pass H: Slack, humans only

Window: 2026-07-14 00:00 through 2026-08-01 23:59 MDT (19 days). All 32 channels in the workspace, public and private, no DMs. Seven channels had no messages in the window (#0-urgent, #0-start-here, #incidents, #photos, #trip-murtaugh, and the two archived channels).

Files in this folder: `constraints_H.csv` (S001 to S048), `override_events_H.csv` (EH001 to EH049), `four_fields_H.csv`, `recurring_types_H.csv`, `volume_table.md`, `metrics_H.json`, and the provenance block at the bottom of this file. Roles only; the raw dumps used to build these stay in the session workspace and are not delivered. In this published copy `constraints_H.csv` and `override_events_H.csv` are withheld and the report is redacted; see the README for what was removed and why. Their frozen hashes are in `SHA256SUMS_frozen.txt`.

## How "posted by an app, bot or integration" was decided

This needed a judgement call and it affects the H versus A comparison, so it is stated up front. Bot-authored messages (Zapier dispatch posts, the booking feed, the reviews feed, the inquiries feed, the daily conditions post, Airtable issue and time-off posts, Slackbot, and the SMS relay that mirrors guides' texts into #field-comms) were excluded on the author field. But the operator's generated posts are not all bot-authored: the trip manifests, food-allergy digests, unpaid-balance lists, phone digests and the balance-report thread continuations are published under the GM's own user account. Those were excluded by content pattern (templated recurring feed). Everything else under a human account was kept, including a handful of one-off reports the GM clearly drafted with software help (a tip payout table, a bus parts write-up) because a human chose to post them and they are not a recurring feed.

Result: 1,204 messages in the window, 673 human, 531 automation. The 673 human messages are the Pass H universe.

## 1. Constraints

48 rows in `constraints_H.csv`, all beyond the 39 baseline rows. Type mix: compliance 7, gear 8, capacity 4, sequencing 8, staffing 6, eligibility 3, timing 3, and 9 rows typed `policy` for internal administrative rules (tips, discounts, time off, yard rules, cleaning) that fit none of the baseline types. If the downstream taxonomy has no `policy` type, fold those into compliance.

Where the rules came from, by channel kind: per-trip channels 15, team-site channels 14, management 9, owners 5, field-comms 2, announcements 2, ops-issues 1, training-safety 0. Per-trip channels were the richest single source of rules and nearly all of their rules are about sequencing and gear for a specific river (where guests meet, which takeout, how boats ride on the trailer, what the crew carries).

The strongest new rules, in the sense of being stated as a rule by someone with authority rather than inferred from a practice: the BLM camp-running stipulation (S001), the roster freeze once a Main Salmon permit is submitted (S002), lapsed licence blocks assignment (S004), the DVIR items as compliance blockers (S006), the seatbelt and bald-tire vehicle rules (S008, S009), rubber-on-rubber trailer loading (S010), the tip split rules (S041, S042) and the no-sleeping-in-the-yard rule (S044). The rest are practices that read as rules because they recur or because a manager corrected someone against them.

## 2. Override events

49 events in `override_events_H.csv`: 31 high confidence, 12 medium, 6 low. "High" means the entity, the decision and the decider are all explicit in the messages. "Medium" means one of those is inferred. "Low" means the decision itself is not visible.

Rate: 544 operational human messages, 31 high-confidence events, so 5.7 high-confidence events per 100 operational messages (9.0 per 100 counting every confidence level). GroupMe was 5.3. The prediction for Pass H was 15.

So the headline is that on the fair comparison Slack-with-humans does not produce more decision events per operational message than GroupMe did. It produces roughly the same density. What differs, and differs a lot, is what can be recovered about each event, which is section 3.

Where the events were found: team-site channels 13, per-trip channels 12, management 7, owners 7, field-comms 5, training-safety 2, ops-issues 1, rentals 1, food 1. High-confidence events split per-trip 8, team-site 8, management 5, field-comms 4, owners 3, other 3. Per-trip channels were the densest source relative to their message count.

## 3. The four fields

Share of the 49 events where each field was recoverable, and why.

Entity, 96 percent (47 of 49). This is the hypothesis under test and it held, but not for the reason expected. Per-trip channels did give the entity for free in the 12 events found there. The other 35 events were in team, management, owner and field-comms channels, and the entity was still recoverable in 33 of them because the operator's habit is to name the trip and date in the first line ("Main Salmon launch logistics - week of July 21", "2pm tomorrow updated from 4 people to 18", "Friday - our most short staffed day"). The two failures were a licence question about a guide with no trip attached and the bowline proposal, which is about all boats. The channel structure helped; the writing habit helped more.

Rule, 80 percent (39 of 49). Recoverable when the event maps to a baseline row (K015 boat capacity, K009 slot pattern, K021 store, K014 lead experience) or to a rule stated elsewhere in the window (S-rows). The 10 failures are events where the thing being overridden is an inventory fact (cots, sleeping pads), a custom itinerary, a rendezvous convention, or a conduct expectation that nobody wrote down. Note that "rule recoverable" here includes rules that only exist because this pass extracted them; against the 39-row baseline alone it would be nearer 40 percent.

Actor, 84 percent (41 of 49), role only. Recoverable because the decider is usually the poster, and roles are stable: the GM makes most calls, owners make permit, discount and food calls, the office manager makes shuttle-timing calls, site leads make Hagerman calls. The 8 failures are the "raised but not answered" cases where a question was posted and no reply exists in the human messages. Slack threads did not help much here; most decisions were made in the main channel, not in a thread, and the eight open questions are open in both.

Lead time, 84 percent (41 of 49). This was the biggest gain over GroupMe. Recoverable because Slack timestamps are precise and the trip date is usually in the message, so the gap is arithmetic. Spread: 12 events decided with less than six hours of lead, 17 between six hours and two days, 12 with three days or more, 8 not applicable (asset faults, policy, conduct). The failures are the asset and policy cases where there is no job to measure against.

Net: the hypothesis "per-trip channels give the entity for free" is true where it applies, but only a quarter of the events lived in per-trip channels. Entity and lead time were recoverable because the operator names trips and dates in the first line and because Slack keeps clock time, not because of the channel structure alone.

## 4. Recurring types

Counts from `recurring_types_H.csv`, grouped:

- Decision visible but outcome not stated: 8 (see section 5).
- Vehicle or bus capacity shortfall worked around: 5.
- Owner or manager personally fills a guide or driver slot: 5.
- Gear shortfall accepted (cots, pads, sleeping bags, tents, a patched boat): 4.
- Vehicle fault with restricted use accepted: 4.
- Boat capacity limit stretched: 3.
- Eligibility decisions (exception granted, enforced, or raised): 5 across three sub-kinds.
- Pricing exceptions (contractor discount, family-and-friends Main spots): 2.
- Singletons: trip added beyond the daily pattern, itinerary change at guest request, safety incident with guidance, late booking growth, standby guide used, human override of the shuttle timer, store hours flexed, rendezvous failure, OTA booking artefact, time off honoured, conduct issue deferred, default plan under missing information.

The two dominant patterns are the same as an operator would guess: vehicles (buses and vans) are the binding constraint in peak season, and the fix for any staffing hole is that the GM or an owner does it themselves.

## 5. Volume and what defeated the pass

Volumes are in `volume_table.md`. Summary by channel kind (human messages / operational): per-trip 140/136, field-comms 129/129, team-site 118/102, social 100/4, management 74/73, owners 29/29, rentals 19/19, announcements 17/13, ops-issues 15/15, feeds 13/8, food 7/7, training-safety 7/7, other 5/2. Total 673 human, 544 operational.

Field-comms is worth a note: its 129 human messages are almost all one-line status calls ("half day push 10:26", "full day guests have arrived"). They are operational and they are what makes lead time and entity recoverable for the shuttle events, but they contain almost no decisions. The decisions live in team-site, management, owners and per-trip channels.

Where a decision was visibly being made and the pass could not tell what it was:

1. Whether a charter bus was hired for the Friday French pickup on Jul 17 (EH005).
2. Whether a sixth guide was added to the 51-person half day on Jul 18 (EH009).
3. Whether the Main Salmon takeout on Jul 27 got a Carey Creek lunch or an earlier bus (EH014).
4. Whether the one-lap guide was put on the Jul 31 Main gear boat (EH016).
5. Whether an eligibility question raised about a guide was resolved (EH017).
6. Whether bowlines were removed (EH023).
7. Whether the Hagerman guide found cover for the Jul 27 second run (EH028).
8. Who drove the Middle Fork shuttle on Aug 3 (EH034, after the window).
9. Whether the Hagerman Aug 1 afternoon got a sixth guide (EH042).
10. Whether the Hagerman Jul 22 2 pm ran after three cancellations (EH047).
11. Whether the bus driver's late arrival on Jul 17 produced the improvised safety talk (EH007).

The pattern behind these: the question was posted in Slack and the answer was given in person, by phone, or by the dispatch system. Several of them ("add a sixth guide?", "no driver assigned") are exactly what the automation in Pass A answers.

Two other things defeated the pass in a smaller way. First, the same trip is discussed across four or five channels (owners, management, team-site, per-trip, field-comms) and stitching one event together requires reading all of them; a session that read only the per-trip channel would have found a third of the events. Second, several of the GM's posts are generated summaries under a human account; the line between "human" and "integration" is a content judgement, stated above, and a different judgement would move the operational count by a few dozen messages and the rate by a few tenths.

## Predictions versus result (Pass H)

| item | predicted | result |
|---|---|---|
| high-confidence events per 100 operational | 15 | 5.7 |
| entity recoverable | 20 % | 96 % |
| lead time recoverable | 26 % | 84 % |
| coverage of the 24 withheld rules | 5 of 24 | not scorable here; the withheld list was not given to this session |
| coverage of the 18 findings | 2 of 18 | not scorable here; same reason |

The claim "Pass H beats GroupMe by at least 10 on events per 100" is not supported: the margin is 0.4. The pre-registered conclusion for that case reads: "operator tooling is the key change." Whether that sentence is right depends on Pass A.

## Provenance

```json
{
  "pass": "H",
  "assembled_by": "Claude (Cowork session), fresh session, Slack read-only",
  "assembled_on": "2026-09-04",
  "web_search_used": false,
  "window": "2026-07-14 00:00 to 2026-08-01 23:59 MDT, 19 days",
  "channels_read": 32,
  "messages_total": 673,
  "messages_operational": 544,
  "messages_from_bots_excluded": 531,
  "constraint_rows": 48,
  "override_events": 49,
  "override_events_high_confidence": 31,
  "entity_recoverable_pct": 96,
  "rule_recoverable_pct": 80,
  "actor_recoverable_pct": 84,
  "lead_time_recoverable_pct": 84,
  "notes": "messages_total is the human-only universe; the full window holds 1204 messages. 'Bot' = bot-authored (author id B*/Slackbot/Airtable app user) OR templated recurring feed posted under the GM's account (manifests, allergy digests, unpaid-balance lists, phone digests, balance-report thread continuations). SMS relayed into #field-comms by the phone integration counted as bot for this pass. Operational = about running trips, staff, vehicles, gear, guests, money or safety; 129 of 544 are one-line status calls in #field-comms. Confidence is this session's judgement; the GroupMe rate was a different session's judgement of the same scale."
}
```
