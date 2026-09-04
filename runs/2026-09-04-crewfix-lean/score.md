# Score, 2026-09-04-crewfix-lean

Profile: lean
Key frozen and unmodified: yes
Key sha256: `8ab6bedde066c997377f0c023efc0ff241c0a613bba90d5d5ca3269c5b32f2a3`

## Key provenance

- Assembled by: Grok 4 (xAI)
- Assembled on: 2026-09-03
- Method: conversational transcription from operator-supplied documents
- Web search used: no
- Source documents: operator memory dumps (head), Adventure Idaho.xlsx, Adventure Idaho - Email Inquiry Desk Playbook.docx, Adventure Idaho - Inquiry Desk Playbook.docx, Adventure Idaho - Rentals Checklist.xlsx, Adventure Idaho - Trip Templates & Operations Reference.docx, AI - Logisitcs.docx, Hagerman_Murtaugh SOPs.docx, Lower Salmon SOPs (Lead Guides).docx, Main Salmon SOPs.docx, French Creek Large Group Lead Guide Itinerary.docx, Middle Fork Leadership & SOPs.docx, Photos SOP.docx, Rafting Trip Calendar SOP.docx, Big Water Theory - SOPs.docx, Day Trips - Guest Experience SOPs.docx, Lead Guide Training_ Principles of Leadership.docx, Radio Communication Guidelines & Use Cases.docx, SOP_ Communications on the River and at the Office.docx, Rafting Checklists.xlsx, Trip Type Rules-Grid view.csv, Movement Types-Grid view.csv, Activity Mapping-Grid view.csv, Boats Inventory-Grid view.csv, Movement Templates-Grid view.csv, Vehicles-Grid view.csv, conflict_check_v6.35.js, dispatch board HTML (pasted-text.txt)
- Notes: Memory-only baseline marked source=head. Document-derived rows use the exact file name supplied. Airtable rule tables marked source=airtable. Hardcoded checker and board limits marked source=code. Soft/planned/note-only items from the conflict-checker tables were excluded. Some gear counts and vehicle-seat defaults remain qualitative where the operator supplied no hard numeric threshold beyond the values already recorded. The list prioritises completeness over tidiness; overlapping statements that apply to different trip types were kept separate.

## Headline

| Measure | Value | Of |
| --- | --- | --- |
| Recall | 2% | 1 of 63 operating constraints |
| Precision | 50% | 4 of 8 candidates |
| Novelty | 3 | real constraints the key did not contain |
| False | 4 | candidates that were not constraints |

Novelty is the number that matters. 3 constraint(s) here are real and a two year manual effort did not write them down.

The key also holds 11 row(s) marked `scope=interface`: warning thresholds, how far out a flag appears, defaults used when a field is blank. Those describe the dispatch tooling rather than the operation, and they sit outside the headline denominator by a decision made before the first run. The battery recovered 0 of them. Counting them in, recall over all 74 key rows is 1%.

## Recall by constraint type

| Type | Recovered | Of | Recall |
| --- | --- | --- | --- |
| availability | 0 | 3 | 0% |
| capacity | 1 | 18 | 6% |
| compliance | 0 | 3 | 0% |
| driver | 0 | 3 | 0% |
| eligibility | 0 | 6 | 0% |
| gear | 0 | 13 | 0% |
| jetboat | 0 | 1 | 0% |
| lead | 0 | 1 | 0% |
| role | 0 | 2 | 0% |
| sequencing | 0 | 3 | 0% |
| shuttle | 0 | 3 | 0% |
| staffing | 0 | 1 | 0% |
| timing | 0 | 7 | 0% |
| vehicle | 0 | 10 | 0% |

## Recall by source

| Source | Recovered | Of | Recall |
| --- | --- | --- | --- |
| airtable | 0 | 6 | 0% |
| code | 0 | 29 | 0% |
| head | 1 | 35 | 3% |
| rafting checklists.xlsx | 0 | 4 | 0% |

### Remembered against written down

- Rules recalled unaided: 1 of 35 recovered, 3%
- Rules found in a document: 0 of 39 recovered, 0%

## New constraints found

- **p03-exclusivity-person** (exclusivity) A person is sometimes booked on two jobs whose times overlap. This happened 98 times across 21 of them. Is the overlap allowed, or are these mistakes?
  - Guides may also drive on the same day when their guide assignment and driver movement times do not overlap, and required turnaround buffers are met.
- **p03-exclusivity-vehicle** (exclusivity) A vehicle is sometimes booked on two jobs whose times overlap. This happened 67 times across 5 of them. Is the overlap allowed, or are these mistakes?
  - vehicles can be used for multiple jobs if the times align or they can make multiple stops at sites along the route
- **p03-turnaround-person** (turnaround) After a person finishes a job, at least 30 minutes almost always passes before it starts the next one: 825 of 832 consecutive pairs. The 7 exception(s) go as low as 0 minutes. Is 30 minutes a required turnaround that got broken those times, or is there no minimum?
  - hagerman has tighter turnaround times. the 10am and 2pm lauch times work - finding a guide was removed from the rafting bootcamp that day. another guide took his spot. currenlty dont have a great way for data to represent a guide swapping off a trip early and putting someone esle on

## Unrecovered key rows

This list is the interview.

- **K001** (capacity) Lower Salmon 4-Day maximum is 30 total people (5 guides and 25 guests).
- **K002** (capacity) Main Salmon 5-Day (or 4-Day high-water variant) maximum is 30 total people (5 guides and 25 guests).
- **K003** (capacity) Jetboat shuttle maximum is 24 guests.
- **K004** (sequencing) Lower Salmon requires a shuttle driver to drop guides boats and gear at Hammer Creek launch; the driver returns the van and trailer; a driver van and trailer must pick up at Heller Bar on the afternoon of day 4.
- **K005** (sequencing) Main Salmon requires a driver van and trailer to drop at Corn Creek (approximately 10 hours from launch); the crew camps overnight; trip starts 9 am the following morning; the driver returns the van/trailer to Riggins after launch.
- **K006** (capacity) Typical full multi-day boat mix is 2 large gear boats and 3 paddle boats; smaller groups may run fewer paddle boats or a Mammoth but always require at least one gear boat.
- **K007** (eligibility) Buses require a CDL-qualified driver.
- **K008** (timing) Maximum one full-day trip per day.
- **K009** (timing) Maximum two half-day trips per day (10 am and 2 pm).
- **K010** (timing) Main Salmon has assigned launch dates.
- **K011** (timing) Lower Salmon preferred launch days are Monday and Tuesday; other days permitted when needed.
- **K013** (capacity) One seat and one PFD required per guest.
- **K014** (eligibility) Each multi-day trip requires one lead guide (typically 2-3 years experience).
- **K015** (capacity) Day-trip paddle boats limited to 9 guests on a 16-ft boat.
- **K016** (capacity) French Creek / SRHAB paddle boats limited to 10 guests on a 16-ft boat.
- **K017** (eligibility) A guide may be assigned to only one boat at a time on the same trip.
- **K018** (eligibility) Ruby (old van) must not tow.
- **K019** (eligibility) Buses must not travel to Vinegar (French Creek / SRHAB launch).
- **K020** (sequencing) French Creek / SRHAB requires multiple drivers and vehicles (typically one van + mega trailer plus another van; larger trips need two vans and two trailers) for both drop and pickup.
- **K021** (staffing) One person must work the store each working day.
- **K022** (gear) Two oars required for each boat.
- **K023** (gear) One paddle required for each person in a paddle boat.
- **K024** (gear) Helmets required during high water; helmets always required in inflatable kayaks or on scout rafting trips.
- **K025** (gear) First-aid kit required on each trip.
- **K026** (gear) Each raft requires a perimeter-line rope.
- **K027** (gear) Thwarts/seats must be set for the correct passenger count; boats must be properly inflated.
- **K028** (gear) Each trip requires a pump.
- **K029** (compliance) Safety talk required before every trip.
- **K030** (gear) One throw rope required per boat.
- **K031** (compliance) Main Salmon and Middle Fork permits and camps must be submitted at least two weeks before launch.
- **K032** (compliance) Other rivers (BLM) report usage only at end of season.
- **K033** (timing) Two half-days on the same day (Hagerman or Riggins) are a hard limit.
- **K034** (eligibility) A guide must not be sent alone on Murtaugh multi-day trips or any high-water trip; solo is permitted on low-water Hagerman and on Riggins full-day and half-day trips.
- **K035** (gear) Day-trip paddle boats each require 4 straps.
- **K036** (gear) Frame straps required at 4 per boat (6 for big boats).
- **K037** (gear) Spare PFDs required at 1 per 15 people.
- **K038** (gear) One invasive-species sticker required per boat.
- **K039** (gear) SRHAB / French Creek requires one boat pump for every 4 boats.
- **K040** (availability) A guide with an approved Blackout request or Assignment block on a trip date cannot be assigned that day.
- **K041** (role) Store Staff cannot also hold a guide driver or food role on the same day.
- **K042** (role) A guide assigned to a multi-day trip cannot take any other overlapping assignment for the duration of that trip.
- **K043** (vehicle) The same vehicle or trailer cannot be assigned to two same-launch-day operations unless cleared by stacking shuttle-pool or rig-group rules.
- **K044** (jetboat) A jetboat trip type (Lower Salmon 4-Day or Main Salmon 4-Day) on a today-or-future date must have Jetboat confirmed checked.
- **K045** (capacity) Main Salmon and Middle Fork trips are hard-capped at 25 guests and 5 guides.
- **K046** (vehicle) A trip that has boats to haul (Total boats > 0) must have a trailer assigned when a van/driver is present.
- **K047** (vehicle) Boats on a trip may not exceed the assigned trailer’s Boat capacity (standard = 5 mega = 10).
- **K048** (vehicle) A rental operation’s assigned vehicle or trailer is blocked for the full rental span and cannot be assigned elsewhere on intervening days.
- **K049** (vehicle) Each vehicle assigned to a movement must have its own driver.
- **K050** (driver) A CDL-required vehicle must be driven by a CDL-qualified driver.
- **K051** (availability) A guide assigned to a trip whose date falls before their Season start date or after their Season end date is invalid.
- **K052** (driver) A driver whose Drivers License Expiration has passed or whose CDL/DOT medical has expired cannot be assigned.
- **K053** (vehicle) A vehicle on manual hold or with an open critical issue cannot be assigned to a trip.
- **K054** (availability) Movement drivers are subject to the same time-off blackout and season rules as Daily Op crew.
- **K055** (shuttle) A Middle Fork trip with no Shuttle details is invalid.
- **K056** (shuttle) A Main Salmon Lower Salmon or Overnighter trip with Guest shuttle coordinated unchecked is invalid when inside the hard window.
- **K057** (capacity) For Full Day Half Day Overnighter or SRHAB day-3 operations 1–11 people require 1 van.
- **K058** (capacity) For Full Day Half Day Overnighter or SRHAB day-3 operations 12–23 people require 2 vans.
- **K059** (capacity) For Full Day Half Day Overnighter or SRHAB day-3 operations 24–25 people require 3 vans.
- **K060** (capacity) For Full Day Half Day Overnighter or SRHAB day-3 operations 26–36 people require 3 vans or 1 bus.
- **K061** (capacity) For Full Day Half Day Overnighter or SRHAB day-3 operations 37 or more people require a bus.
- **K062** (capacity) Standard day-trip 16-ft boats are limited to 9 guests; SRHAB / French Creek 16-ft boats are limited to 10 guests.
- **K063** (lead) Designated lead for a multi-day section must be one of a small fixed set of named leads for that section in the 2026 season (one named lead for Middle Fork two for Lower one for Main one for French/SRHAB).
- **K064** (capacity) Soft capacity warning fires when boats exceed the comfortable load of 4 on a standard trailer or 8 on a Mega trailer.
- **K065** (driver) A driver on big drives three consecutive days triggers a soft fatigue flag on the third day.
- **K066** (timing) A guide or driver finishing a movement needs at least 180 minutes before starting a day-trip assignment; shorter gaps are a soft tight-turnaround flag.
- **K067** (capacity) When a Vehicle record has no Passenger seats value the default seat count used for capacity checks is 15.
- **K068** (vehicle) A pickup movement with 25 or more riders and no bus assigned triggers a soft “bus likely needed” flag.
- **K069** (vehicle) Two jobs on the same rig are clear if the gap between their time windows is at least 60 minutes; a smaller gap with no overlap is a soft tight-turnaround flag; real overlap is hard.
- **K070** (vehicle) A movement carrying people with no vehicle assigned is hard within 1 day of the trip soft within 3 days and silent further out.
- **K071** (vehicle) “Bus driver not confirmed” only flags within 4 days of the trip.
- **K072** (shuttle) Guest-shuttle-not-coordinated with no details is hard within 2 days of the trip and soft further out.
- **K073** (timing) A Riggins day-trip operation with zero guests is treated as not running; its movements do not commit rigs or crew.
- **K074** (capacity) Middle Fork trips are exempt from the per-movement passenger-seat capacity check.

