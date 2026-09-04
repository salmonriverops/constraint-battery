# Delta, 2026-09-04-crewfix-full against 2026-09-04-crewfix-lean

- Richer run: `2026-09-04-crewfix-full`, profile full
- Leaner run: `2026-09-04-crewfix-lean`, profile lean
- Key frozen and unmodified: yes
- Key sha256: `8ab6bedde066c997377f0c023efc0ff241c0a613bba90d5d5ca3269c5b32f2a3`

## Key provenance

- Assembled by: Grok 4 (xAI)
- Assembled on: 2026-09-03
- Method: conversational transcription from operator-supplied documents
- Web search used: no
- Source documents: operator memory dumps (head), Adventure Idaho.xlsx, Adventure Idaho - Email Inquiry Desk Playbook.docx, Adventure Idaho - Inquiry Desk Playbook.docx, Adventure Idaho - Rentals Checklist.xlsx, Adventure Idaho - Trip Templates & Operations Reference.docx, AI - Logisitcs.docx, Hagerman_Murtaugh SOPs.docx, Lower Salmon SOPs (Lead Guides).docx, Main Salmon SOPs.docx, French Creek Large Group Lead Guide Itinerary.docx, Middle Fork Leadership & SOPs.docx, Photos SOP.docx, Rafting Trip Calendar SOP.docx, Big Water Theory - SOPs.docx, Day Trips - Guest Experience SOPs.docx, Lead Guide Training_ Principles of Leadership.docx, Radio Communication Guidelines & Use Cases.docx, SOP_ Communications on the River and at the Office.docx, Rafting Checklists.xlsx, Trip Type Rules-Grid view.csv, Movement Types-Grid view.csv, Activity Mapping-Grid view.csv, Boats Inventory-Grid view.csv, Movement Templates-Grid view.csv, Vehicles-Grid view.csv, conflict_check_v6.35.js, dispatch board HTML (pasted-text.txt)
- Notes: Memory-only baseline marked source=head. Document-derived rows use the exact file name supplied. Airtable rule tables marked source=airtable. Hardcoded checker and board limits marked source=code. Soft/planned/note-only items from the conflict-checker tables were excluded. Some gear counts and vehicle-seat defaults remain qualitative where the operator supplied no hard numeric threshold beyond the values already recorded. The list prioritises completeness over tidiness; overlapping statements that apply to different trip types were kept separate.

## Headline

| Measure | Richer | Leaner | Change |
| --- | --- | --- | --- |
| Recall | 8% | 2% | -6 points |
| Precision | 79% | 50% | -29 points |
| Novelty | 19 | 3 | -16 |
| Candidates | 29 | 8 | -21 |

## Input volumes

| Landing table | Richer | Leaner |
| --- | --- | --- |
| assignments | 3,206 | 1,632 |
| changes | 400 | 0 |
| location_travel | 13 | 0 |
| locations | 35 | 35 |
| resources | 152 | 152 |
| work | 706 | 412 |

## Candidates by probe

| Probe | Richer | Leaner |
| --- | --- | --- |
| p03 | 4 | 4 |
| p04 | 5 | 4 |
| p05 | 2 | 0 |
| p08 | 18 | 0 |

## Which constraint types survive the degradation

| Type | Richer | Leaner | Survives |
| --- | --- | --- | --- |
| availability | 0/3 | 0/3 | neither run found it |
| capacity | 0/18 | 1/18 | only in the leaner run |
| compliance | 0/3 | 0/3 | neither run found it |
| driver | 0/3 | 0/3 | neither run found it |
| eligibility | 2/6 | 0/6 | **no, lost entirely** |
| gear | 0/13 | 0/13 | neither run found it |
| jetboat | 1/1 | 0/1 | **no, lost entirely** |
| lead | 1/1 | 0/1 | **no, lost entirely** |
| role | 0/2 | 0/2 | neither run found it |
| sequencing | 0/3 | 0/3 | neither run found it |
| shuttle | 0/3 | 0/3 | neither run found it |
| staffing | 0/1 | 0/1 | neither run found it |
| timing | 0/7 | 0/7 | neither run found it |
| vehicle | 2/10 | 0/10 | **no, lost entirely** |

## Which sources survive the degradation

| Source | Richer | Leaner | Survives |
| --- | --- | --- | --- |
| airtable | 0/6 | 0/6 | neither run found it |
| code | 4/29 | 0/29 | **no, lost entirely** |
| head | 2/35 | 1/35 | **partly, 1 lost** |
| rafting checklists.xlsx | 0/4 | 0/4 | neither run found it |

## Recovered in the richer run, lost in the leaner one

This is the deliverable for the next client. Each line names something the battery can only find if the business is instrumented to produce it.

- **K014** (eligibility) Each multi-day trip requires one lead guide (typically 2-3 years experience).
  - found by: p08-override-work-ovr-384927112582
- **K017** (eligibility) A guide may be assigned to only one boat at a time on the same trip.
  - found by: p08-override-work-ovr-6bd33d092af5
- **K043** (vehicle) The same vehicle or trailer cannot be assigned to two same-launch-day operations unless cleared by stacking shuttle-pool or rig-group rules.
  - found by: p08-override-work-ovr-208d44cad2d2
- **K044** (jetboat) A jetboat trip type (Lower Salmon 4-Day or Main Salmon 4-Day) on a today-or-future date must have Jetboat confirmed checked.
  - found by: p08-override-work-ovr-264e4cce27ff
- **K063** (lead) Designated lead for a multi-day section must be one of a small fixed set of named leads for that section in the 2026 season (one named lead for Middle Fork two for Lower one for Main one for French/SRHAB).
  - found by: p08-override-work-ovr-384927112582
- **K069** (vehicle) Two jobs on the same rig are clear if the gap between their time windows is at least 60 minutes; a smaller gap with no overlap is a soft tight-turnaround flag; real overlap is hard.
  - found by: p08-override-work-ovr-208d44cad2d2

## Recovered in the leaner run only

Unexpected. Worth understanding before trusting either number.

- **K012** Day-trip and French Creek maximum combined volume is 120 people.
  - found by: p04-ceiling-customers-per-work

## Candidates present in one run only

Only in `2026-09-04-crewfix-full` (24):

- p03-exclusivity-bus
- p03-exclusivity-trailer
- p03-exclusivity-van
- p04-ceiling-work-per-location-per-day
- p05-exemption-work-type-by-status-planned
- p05-population-work-type-by-status
- p08-override-work-ovr-0a9e36c5ef2f
- p08-override-work-ovr-0cd7af36191f
- p08-override-work-ovr-1b495b2aa25b
- p08-override-work-ovr-208d44cad2d2
- p08-override-work-ovr-264e4cce27ff
- p08-override-work-ovr-384927112582
- p08-override-work-ovr-4d682831618d
- p08-override-work-ovr-6bd33d092af5
- p08-override-work-ovr-6c27f1502e50
- p08-override-work-ovr-6f14edf07cf2
- p08-override-work-ovr-7b8042acacfd
- p08-override-work-ovr-9e3bdb99b27b
- p08-override-work-ovr-b41bb92b8955
- p08-override-work-ovr-bf5efa29e136
- p08-override-work-ovr-e4b5f5e2c2d1
- p08-override-work-ovr-e87673c6f82a
- p08-override-work-ovr-f3ebe5d06d50
- p08-override-work-ovr-fc4e6af39b2a

Only in `2026-09-04-crewfix-lean` (3):

- p03-exclusivity-vehicle
- p03-turnaround-person
- p03-turnaround-vehicle

