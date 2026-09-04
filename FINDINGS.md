# Rules learned from the battery, and what was done about them

Written after scoring on 2026-09-04, from the notes recorded in
`runs/2026-09-04-crewfix-full/match.csv` and `runs/2026-09-04-crewfix-lean/match.csv`.

Nothing here goes into `key/answer_key.csv`. That file is frozen evidence at
`8ab6bedd` and adding a row to it after a run means scoring against a key that
was edited once the answers were known. Findings live here instead.

Personal names are left out, as they are in the key. Where a finding concerns a
specific person's record, the run notes name them.

Status is one of: not yet written into the SOPs, added to the SOPs, added to
the conflict checker, rejected on reflection.

## What the run produced

| | full | lean |
| --- | --- | --- |
| Recall | 8%, 5 of 63 operating constraints | 2%, 1 of 63 |
| Precision | 79%, 23 of 29 | 50%, 4 of 8 |
| Novelty | 19 | 3 |
| Recall against memory alone | 6%, 2 of 35 | 3%, 1 of 35 |

Eighteen of the 29 candidates came from p08, the override log, and those 18
produced all four matches and 14 of the 19 finds. p04 and p05 produced one
find between them against six false positives. Remove the override log, which
is what the lean profile does, and recall falls to 2% and novelty to 3.

One caveat belongs at the top, because it is the first thing a sceptic will
raise. The battery did not state 19 rules. It found 19 places where an
undocumented rule was operating and the rule itself came from the operator,
prompted by the evidence. That is still a repeatable method for finding where
to ask. It is not a method for producing answers unaided.

## Rules about sharing equipment and people

| Rule as now understood | Conditions | From | Status |
| --- | --- | --- | --- |
| A bus can serve several trips in a day. | Timing and seat capacity must line up. Trips finishing together can share a bus only at the same location and time, or to the same destination. Worked example: drop a full day at 09:00, collect SRHAB at Lucile at 12:30, ready to collect the full day at Lucile at 15:00. | p03-exclusivity-bus | not yet written into the SOPs |
| A trailer or rig can serve several trips in a day. | Locations must be close and the hourly windows must work. Worked example: drop the full day at Spring Bar in the morning, collect the morning half day at Lucile around noon, then collect the full day and afternoon half day at Lucile. | p03-exclusivity-trailer | not yet written into the SOPs |
| A van can serve several trips in a day, on the same terms as a trailer. | Depends on the order of locations along the river and the distances between them. | p03-exclusivity-van, p04-ceiling-work-per-resource-per-day | not yet written into the SOPs |
| A guide assigned to a trip may also drive that trip's shuttles. | Only at defined drop and pickup points, at set times, and never while on the water guiding. Not a double booking and requires no additional staff. | p03-exclusivity-person | not yet written into the SOPs |
| A trailer stays tied to its trip while the trip is out, but only when gear and boats are still on it. | Once a trip is on the water the trailer sits idle and empty and can be used elsewhere. Keeping it tied avoids unloading and reloading gear. | p08 override, trailer reuse | not yet written into the SOPs |

## Rules about credentials

| Rule as now understood | Conditions | From | Status |
| --- | --- | --- | --- |
| Every guide must hold a current guide license, and current CPR and first aid certification. | | p08 override, guide license, two separate override families | not yet written into the SOPs |
| The owner holds an outfitting license and does not require a guide license. | Applies to the outfitting license holder only. | p08 override, owner license | not yet written into the SOPs |
| A guide assigned to lead a trip must be lead capable. | Being assigned as lead is not the same as being certified to lead. | p08 override, lead capability | not yet written into the SOPs |

## Rules about staffing levels

| Rule as now understood | Conditions | From | Status |
| --- | --- | --- | --- |
| Guide to guest ratios are advisory, not fixed. | A trip that recommends 5 guides can run with 4 when a group prefers to ride together in one boat. A trip that recommends 3 can run with 2 when more guests row their own boat or kayak, needing fewer raft seats. | p08 override, ratio | not yet written into the SOPs |

## Rules about shuttles and outside parties

| Rule as now understood | Conditions | From | Status |
| --- | --- | --- | --- |
| Bus drivers must be confirmed manually by text. | They are part time, and do not use Slack or the dispatch board. Two separate override families exist for this, 23 events each, together the heaviest pair in the log. | p08 overrides, bus confirmation | not yet written into the SOPs |
| Lower Salmon guest shuttle must be coordinated, and the vehicle depends on group size. | Up to about 10 people with dry bags fit one 15 passenger van. 11 to 14 needs a van and a trailer. More than that needs two vans and two drivers. Route is Pittsburg Landing to Hammer Creek. Some groups self shuttle for a lower trip price. | p08 override, lower shuttle | not yet written into the SOPs |
| Main Salmon and Lower Salmon require confirming that guests have their own shuttle arranged. | | p08 override, guest shuttle | not yet written into the SOPs |
| Lower Salmon and the 4 day Main Salmon have jetboat pickups that must be confirmed with the jetboat company. | Confirmation depends on where the group camps the last night, which is not known in advance. Current practice is to acknowledge the flag and wait for the group's text, then forward it. | p08 override, jetboat | not yet written into the SOPs |
| The Middle Fork shuttle must be coordinated with the Main Salmon launch. | When the dates align, Main Salmon guides can drive the Middle Fork rig to the takeout, because the drop and pickup are on the way. When the Middle Fork trip finishes before the Main Salmon crew can move their truck, it needs a custom movement or an outside shuttle company. | p08 override, middle fork shuttle | not yet written into the SOPs |

## Exemptions

| Rule as now understood | Conditions | From | Status |
| --- | --- | --- | --- |
| SRHAB day 1 guests self shuttle, so seat counts do not apply. | Monday or Thursday launches. The checker repeatedly flags that all guests need a ride when they do not. | p08 override, seat counts | not yet written into the SOPs |
| The Middle Fork scout truck carries guides only, never guests. | The scouts run their own bus shuttle. It only needs to hold the 5 guides. | p08 override, seat counts | not yet written into the SOPs |

## Capacity, where the stated number looks conservative

| Rule as now understood | Conditions | From | Status |
| --- | --- | --- | --- |
| The stated combined day volume of 120 looks low. | French Creek and SRHAB alone run near 120, and other day trips run at the same time. Realistic total is nearer 140. Highest single record observed is 127. It gets tight but it works. | p04-ceiling-customers-per-work | needs checking against seats, PFDs and guide count before adopting |
| Hagerman runs tighter turnarounds than elsewhere. | The 10:00 and 14:00 launch pair works there. | p03-turnaround-person, lean run | not yet written into the SOPs |

## Instrumentation gaps

These are not constraints. They are the reasons the battery could not see more,
and each one is fixable. Several of them cost more than any single rule above.

| Gap | Consequence | Status |
| --- | --- | --- |
| The override log records the acknowledgement but not what provoked it. The key names the entity, not the condition. | Three different situations produce an identical record. The log cannot explain itself without opening Airtable revision history, which is retained by plan and may be gone. Fixable by storing the rule id alongside the acknowledgement. | not yet fixed |
| An acknowledgement means both "this rule does not apply here" and "not done yet, will fix". | The same field carries an exemption and a snooze, and nothing can separate them. Every override analysis inherits the ambiguity. | not yet fixed |
| No record anywhere links a boat to the trip it ran. | 60 boats sit in the fleet and never appear in an assignment. Every boat rule in the key, the gear boat minimum, trailer boat capacity, paddle boat guest limits, is unrecoverable from this export by construction. | not yet fixed |
| Movement Type is empty on most movements. | Shuttles cannot be grouped by kind. 294 movements arrive untyped. | not yet fixed |
| Two heavy override families were caused by stale credential records, not by real exceptions. | Two guides were licensed and had shown their certificates, but the records were never updated, so the same conflict was overridden repeatedly. The overrides record a filing failure, not an operating rule. | not yet fixed |
| There is no way to represent a guide leaving a trip early and another taking their place. | A swap looks like a zero minute turnaround. One of the seven turnaround exceptions in the lean run is exactly this. | not yet fixed |
| `Guide Availability` on Daily Ops was empty on all 412 records while the crew lived in five other link fields. | Fixed in `extract/airtable_map.json` during this run. Recorded because the same shape of error is likely elsewhere. | fixed in the loader |

## Open item

`p04-ceiling-customers-per-work` was judged NEW in the full run and MATCH
against K012 in the lean run. The same candidate cannot be both. This is the
only inconsistency between the two sets of verdicts and it is the sole reason
K012 appears as recovered in the leaner run only. Resolve it, re-score, and
note the correction in `PRE-REGISTRATION.md` before publishing any number.
