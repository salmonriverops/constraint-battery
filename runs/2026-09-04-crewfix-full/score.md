# Score, 2026-09-04-crewfix-full

Profile: full
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
| Recall | 10% | 6 of 63 operating constraints |
| Precision | 79% | 23 of 29 candidates |
| Novelty | 18 | real constraints the key did not contain |
| False | 6 | candidates that were not constraints |

2 candidate(s) recovered more than one key row. Each is counted once in precision and credits every key row it named:

- p08-override-work-ovr-208d44cad2d2 covers K043, K069
- p08-override-work-ovr-384927112582 covers K063, K014

Novelty is the number that matters. 18 constraint(s) here are real and a two year manual effort did not write them down.

The key also holds 11 row(s) marked `scope=interface`: warning thresholds, how far out a flag appears, defaults used when a field is blank. Those describe the dispatch tooling rather than the operation, and they sit outside the headline denominator by a decision made before the first run. The battery recovered 1 of them. Counting them in, recall over all 74 key rows is 9%.

## Recall by constraint type

| Type | Recovered | Of | Recall |
| --- | --- | --- | --- |
| availability | 0 | 3 | 0% |
| capacity | 1 | 18 | 6% |
| compliance | 0 | 3 | 0% |
| driver | 0 | 3 | 0% |
| eligibility | 2 | 6 | 33% |
| gear | 0 | 13 | 0% |
| jetboat | 1 | 1 | 100% |
| lead | 1 | 1 | 100% |
| role | 0 | 2 | 0% |
| sequencing | 0 | 3 | 0% |
| shuttle | 0 | 3 | 0% |
| staffing | 0 | 1 | 0% |
| timing | 0 | 7 | 0% |
| vehicle | 2 | 10 | 20% |

## Recall by source

| Source | Recovered | Of | Recall |
| --- | --- | --- | --- |
| airtable | 0 | 6 | 0% |
| code | 4 | 29 | 14% |
| head | 3 | 35 | 9% |
| rafting checklists.xlsx | 0 | 4 | 0% |

### Remembered against written down

- Rules recalled unaided: 3 of 35 recovered, 9%
- Rules found in a document: 4 of 39 recovered, 10%

## New constraints found

- **p03-exclusivity-bus** (exclusivity) A Bus is sometimes booked on two jobs whose times overlap. This happened 80 times across 2 of them. Is the overlap allowed, or are these mistakes?
  - buses can serve muutlipe trips if the timing and seat capacities line up. multiple trips getting off at the same time can share a bus but only if at the same location and time. and same destination bus can also drop off full day at 9am be back to pickup at srhab at lucile at 1230 then be ready to pickup the full day at 3 at lucile
- **p03-exclusivity-person** (exclusivity) A person is sometimes booked on two jobs whose times overlap. This happened 1161 times across 26 of them. Is the overlap allowed, or are these mistakes?
  - guides can also drive at certain times, not when they are on the water guiding. > Guides assigned to a trip also run that trip's shuttles.   <- talk, Enter > Only at defined drop and pickup points, at set times.      <- talk, Enter > Not a double booking and does not need extra staff.
- **p03-exclusivity-trailer** (exclusivity) A Trailer is sometimes booked on two jobs whose times overlap. This happened 196 times across 6 of them. Is the overlap allowed, or are these mistakes?
  - trailers can serve multiple trips on the same day, if they are close and falls within hourly timeframes taht work. rigs can drop off full day at spring bar in the morning then be back to pickup the morning haalf day at lucile around noon. then it can pickup the full day and afternoon half day at lucile.
- **p03-exclusivity-van** (exclusivity) A Van is sometimes booked on two jobs whose times overlap. This happened 337 times across 6 of them. Is the overlap allowed, or are these mistakes?
  - > trailers can serve multiple trips on the same day, if they are close and falls within hourly timeframes taht work. rigs can drop off full day at spring bar in the morning then be back to pickup the morning alf day at lucile around noon. then it can pickup the full day and afternoon half day at lucile. here i mean vans instread of trailers
- **p08-override-work-ovr-0a9e36c5ef2f** (any) Somebody went back and changed ovr_0a9e36c5ef2f on 4 work records, 4 times in all, after it had already been set. Typically 3 day(s) before the job, and 0 of them on the day or after. What is the system getting wrong that keeps needing this?
  - FINDING: the override log records the acknowledgement but not what provoked it. The key names the vehicle, not the condition. Three different situations produce an identical record, so the log cannot explain itself without opening Airtable revision history. Fixable by storing the rule id alongside the acknowledgement. this is probably about bus driver confirmed, but can't confimr. bus drivers are part timers and need to manually confirmed by text to make sure they can drive. or we were short on seats and a bus had to be added which would result in a matched rule
- **p08-override-work-ovr-0cd7af36191f** (any) Somebody went back and changed ovr_0cd7af36191f on 23 work records, 23 times in all, after it had already been set. Typically 3 day(s) before the job, and 6 of them on the day or after. What is the system getting wrong that keeps needing this?
  - finding - bus drivers must be confirmed manually via text. they don't use our dashboard or slack. this helps us remember to verify that they can work
- **p08-override-work-ovr-1b495b2aa25b** (any) Somebody went back and changed ovr_1b495b2aa25b on 3 work records, 3 times in all, after it had already been set. Typically 3 day(s) before the job, and 0 of them on the day or after. What is the system getting wrong that keeps needing this?
  - multipel rules here. finding - each guide must have a guide license, CP each guide must have a current cpr and first aid cert a part time guide was verified as licensed but the record was never updated so we kept overriding the conflict
- **p08-override-work-ovr-4d682831618d** (any) Somebody went back and changed ovr_4d682831618d on 11 work records, 11 times in all, after it had already been set. Typically 1 day(s) before the job, and 3 of them on the day or after. What is the system getting wrong that keeps needing this?
  - guests counts which equal seat counts don't mattter on day 1 of srhab. mon or thursday. the conflict keeps showing saying all the guests need a ride buty they self shuttle on these days. for the middle fork scout truck one. the scouts handle the bus shuttle. we have nothing to do with it. the scout truck only needs to hold the 5 guides, never guests. finding
- **p08-override-work-ovr-6c27f1502e50** (any) Somebody went back and changed ovr_6c27f1502e50 on 8 work records, 8 times in all, after it had already been set. Typically 1 day(s) before the job, and 4 of them on the day or after. What is the system getting wrong that keeps needing this?
  - sometimes we run trips with different guides to guest ratios. some trips will reccoemdn 5 guides but we can do it with 4 if a group would rather ride together on one boat. Others will reccomend 3 when it can be done with 2 guides if more people are interested in rowing their own boats or kayaking, not needing more raft seats.
- **p08-override-work-ovr-6f14edf07cf2** (any) Somebody went back and changed ovr_6f14edf07cf2 on 3 work records, 3 times in all, after it had already been set. Typically 5 day(s) before the job, and 0 of them on the day or after. What is the system getting wrong that keeps needing this?
  - we prefer to keep trailers tied to teh same trips, mostly when the gear/baots are not on the trips so it can be stored and we don't have to do extra work to remove the gear, use the trailer, then relaod teh gear. whiel the trip is out on the water, the trailer sits idle and empty and can be easily use for other uses - finding
- **p08-override-work-ovr-7b8042acacfd** (any) Somebody went back and changed ovr_7b8042acacfd on 7 work records, 7 times in all, after it had already been set. Typically 3 day(s) before the job, and 1 of them on the day or after. What is the system getting wrong that keeps needing this?
  - finding - the owner is the only person with an outfitting license. he does not need a guide licesne when he has an outfitting license
- **p08-override-work-ovr-9e3bdb99b27b** (any) Somebody went back and changed ovr_9e3bdb99b27b on 3 work records, 3 times in all, after it had already been set. Typically 4 day(s) before the job, and 0 of them on the day or after. What is the system getting wrong that keeps needing this?
  - fidnign - we have to remember to cooridinate the shuttle for the guests on the lower salmon. someetimes this is self shuttle for a lower trip cost or we set up a movement to pick them up after the trip. rule depends on groups size. we can fit about 10 people and dry bags in a 15 passenger van. 11 to 14 and we birng a trailer. more than that and we have to send 2 vans and drivers to bring the people from pittsburg landign to hammer creek
- **p08-override-work-ovr-b41bb92b8955** (any) Somebody went back and changed ovr_b41bb92b8955 on 9 work records, 9 times in all, after it had already been set. Typically 4 day(s) before the job, and 2 of them on the day or after. What is the system getting wrong that keeps needing this?
  - finding gudies must have curent guide license. a guide was licensed and had shown the certificate, but it was never uploaded into the system
- **p08-override-work-ovr-bf5efa29e136** (any) Somebody went back and changed ovr_bf5efa29e136 on 7 work records, 7 times in all, after it had already been set. Typically 6 day(s) before the job, and 1 of them on the day or after. What is the system getting wrong that keeps needing this?
  - lower salmon and 4 day main salmon trips have jetboat pickups finding - this must be manually confirmed and cooridinated with teh jetbaot company based on where the group is camping the last night of the trip. its easier to just check the override and wait for thier text to come in. then i forward to the jetbaot company
- **p08-override-work-ovr-e4b5f5e2c2d1** (any) Somebody went back and changed ovr_e4b5f5e2c2d1 on 5 work records, 5 times in all, after it had already been set. Typically 5 day(s) before the job, and 1 of them on the day or after. What is the system getting wrong that keeps needing this?
  - m middle fork shuttle must be cooridated with our main salmon launch. if the dates align the main salmon guides can drive the middle fork rig to the takeout, as the pickup and dropoff is on the way to the main  salmon. if the dates do not align, as in there is the middle fork trips gets off before the main salmon crew can move their truck, we have set up a custom movemnt to have someone driver over and shuttle it or have a hsuttle comapny do it. finding
- **p08-override-work-ovr-e87673c6f82a** (any) Somebody went back and changed ovr_e87673c6f82a on 23 work records, 23 times in all, after it had already been set. Typically 1 day(s) before the job, and 8 of them on the day or after. What is the system getting wrong that keeps needing this?
  - bus drivers don't use slack or our dispatch schedule board link so we text them manually with each update and confirm if they can drive the route
- **p08-override-work-ovr-f3ebe5d06d50** (any) Somebody went back and changed ovr_f3ebe5d06d50 on 3 work records, 3 times in all, after it had already been set. Typically 5 day(s) before the job, and 0 of them on the day or after. What is the system getting wrong that keeps needing this?
  - when a guide is assigned to lead a trip but not lead guide certified. guides must be lead capable
- **p08-override-work-ovr-fc4e6af39b2a** (any) Somebody went back and changed ovr_fc4e6af39b2a on 14 work records, 14 times in all, after it had already been set. Typically 2 day(s) before the job, and 5 of them on the day or after. What is the system getting wrong that keeps needing this?
  - on main salmon and lower salmon - reminder that we must confirm that guests have their shuttle cooridinated.

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
- **K015** (capacity) Day-trip paddle boats limited to 9 guests on a 16-ft boat.
- **K016** (capacity) French Creek / SRHAB paddle boats limited to 10 guests on a 16-ft boat.
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
- **K064** (capacity) Soft capacity warning fires when boats exceed the comfortable load of 4 on a standard trailer or 8 on a Mega trailer.
- **K065** (driver) A driver on big drives three consecutive days triggers a soft fatigue flag on the third day.
- **K066** (timing) A guide or driver finishing a movement needs at least 180 minutes before starting a day-trip assignment; shorter gaps are a soft tight-turnaround flag.
- **K067** (capacity) When a Vehicle record has no Passenger seats value the default seat count used for capacity checks is 15.
- **K068** (vehicle) A pickup movement with 25 or more riders and no bus assigned triggers a soft “bus likely needed” flag.
- **K070** (vehicle) A movement carrying people with no vehicle assigned is hard within 1 day of the trip soft within 3 days and silent further out.
- **K071** (vehicle) “Bus driver not confirmed” only flags within 4 days of the trip.
- **K072** (shuttle) Guest-shuttle-not-coordinated with no details is hard within 2 days of the trip and soft further out.
- **K073** (timing) A Riggins day-trip operation with zero guests is treated as not running; its movements do not commit rigs or crew.
- **K074** (capacity) Middle Fork trips are exempt from the per-movement passenger-seat capacity check.

