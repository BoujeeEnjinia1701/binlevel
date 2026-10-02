---
doc_id: BNL-DEC-001
title: BinLevel design decisions register
project: BinLevel
doc_type: Design decisions register
version: "0.3"
status: Draft
date: '2026-10-02'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
  - version: "0.1"
    date: '2026-09-30'
    author: Amish Chadha
    change: Register opened with the open decisions from the review note, the decision records and the build plan work
  - version: "0.2"
    date: '2026-10-01'
    author: Amish Chadha
    change: Budget treated as a value-engineering target
  - version: "0.3"
    date: '2026-10-02'
    author: Amish Chadha
    change: Amish approved the recommendations for open decisions 1 to 8 (BNL-DDR-003 accepted); moved to decisions made
---

# BinLevel design decisions register

Every design decision still to be made, and every decision made, in one place. Each decision is argued in full in its decision record under `docs/decisions/`; this register is the index Amish works from. The build plan (`docs/05-build-plan.md`) describes the design as it stands and does not list open decisions.

## Open decisions

None. All open decisions were decided on 2026-10-02.

## To confirm when parts are bought

| # | What to confirm | Why it matters | Source |
| --- | --- | --- | --- |
| 1 | The stock box: 115 x 65 x 55 mm outside, a 15 mm deep cover, corner towers about 9 mm across at about 51 and 26 mm from the centre lines, and a flat base floor | The board size, the stud positions and the sealing washers depend on it | BNL-DDR-003, P1, P4 and P8 |
| 2 | The transducer probe's diameter (24 mm assumed), its cable plug and its temperature rating | Sets the 25 mm hole and the collar bore; R6 is at risk on the rating | BNL-DDR-003, P5; BNL-CAL-001, section H |
| 3 | The driver board's size and mounting holes (about 41 x 28 mm assumed) | Sets the four driver holes in the electronics board and its clearance to the probe and the holder | BNL-DDR-003, P3 |
| 4 | The light sensor breakout's size, holes and sensor position (13 x 18 mm, sensor underneath, assumed) | Sets the holder pocket | BNL-DDR-003, P6 |
| 5 | The press-in stud's hole size, minimum sheet thickness and push-out rating in 2 mm 5052 aluminium (4.2 mm and about 900 N assumed) | The plate holes and the fixing check | BNL-CAL-001, [J3] |
| 6 | The cell holder takes a C cell with room for the strap slots | Cell retention at 20 g | BNL-CAL-001, [J2] |

## Value engineering

Value-engineering target: USD 60 (a hypothetical control target, not a limit). Estimated cost of the constructable design: USD 59 (USD 1 under the target). Main cost drivers and savings worth trying:

- The largest lines are the primary lithium cell and holder (USD 9), the LoRaWAN module (USD 9), the electronics board and small parts (USD 8), the ultrasonic transducer with driver (USD 7) and the enclosure (USD 6).
- Making the design constructable (BNL-DDR-003) took the parts from USD 55 to USD 59, adding box fixings (USD 2.50) and printed sensor mounts and window (USD 1.50) and respecifying lines 1, 2, 3, 6, 7 and 9.
- The external lid antenna for steel containers would add about USD 8 and bring the estimate to USD 67, USD 7 over the target. Steel containers are left out of the first pilot (decided 2026-10-02), so it is not in the estimate.
- Savings worth trying: confirm prices at TRL 4, and a cheaper generic box.

## Decisions made

| Date | Decision | Decided by | Record |
| --- | --- | --- | --- |
| 2026-09-25 | TRL 2 review items D1 to D10: communal containers first, ultrasonic plus ToF, C cell, LoRaWAN on RAK3172, FieldNode and TwinKit reuse, 80 % and 1 h defaults, heat alert, lid mounting with four tamper bolts, stock IP67 box, no budget change | Amish: "i accept all your recommendations, go with them across all repos." | [BNL-DDR-001](decisions/0001-trl2-review-decisions.md), [BNL-DDR-002](decisions/0002-recommendations-accepted.md) |
| 2026-09-25 | 2 mm 5052-class aluminium bracket; R6 upper limit 70 °C with the RAK3172-T for cold sites; heat rate rule counted only above 50 °C; 11-byte payload and 5 min temperature reads; 2 h interval at SF12 only; budget stays $60 | Amish, same instruction | [BNL-DDR-002](decisions/0002-recommendations-accepted.md), N1 to N6 |
| 2026-09-30 | Design for construction: box held on four studs and standoffs, no tabs, M6 x 20 bolts, 55 mm box, prototyping board on standoffs, printed sensor mounts, vent, plugged sensor leads | Made under Amish's 2026-09-30 instruction to make the design physically buildable ("fix the design assumptions to match and be physically feasible"); open for his review. The changes themselves were accepted on 2026-10-02 (below) | [BNL-DDR-003](decisions/0003-design-for-construction.md) |
| 2026-10-02 | Design for construction accepted: the changes P1 to P11 (box on studs and standoffs, no tabs, M6 x 20 bolts, 55 mm box, prototyping board, printed sensor mounts, vent, plugs), as made | Amish: "i approve your recommendations for all 555 open decisions." | BNL-DDR-003 |
| 2026-10-02 | Cell swap: accepted that a swap means lowering the electronics board on its four screws, since the cell lasts about 16 years | Amish: "i approve your recommendations for all 555 open decisions." | BNL-DDR-003, A2 |
| 2026-10-02 | Steel containers are left out of the first pilot, which uses plastic containers only; the external lid antenna is revisited once the link loss inside a steel container has been measured | Amish: "i approve your recommendations for all 555 open decisions." | BNL-DDR-001 and BNL-DDR-002, O1 |
| 2026-10-02 | First partner to approach: a municipal waste service or its contractor using EN 840 plastic communal containers in a city with public LoRaWAN coverage, by default a European city on the EU868 band; ask how the containers are washed before committing | Amish: "i approve your recommendations for all 555 open decisions." | BNL-DDR-001 and BNL-DDR-002, O2 |
| 2026-10-02 | Galvanic isolation: nothing fitted for the prototype; for deployments the plate is anodised before the studs are pressed in | Amish: "i approve your recommendations for all 555 open decisions." | BNL-DDR-002, Consequences; review note 2026-09-25 |
| 2026-10-02 | Pilot data layer: TwinKit, feeding a standard open-source vehicle routing tool; a city system only if the pilot partner already runs one | Amish: "i approve your recommendations for all 555 open decisions." | BNL-PRC-001, open questions |
| 2026-10-02 | Fill-rate estimate: left to the server; the spare payload byte stays free | Amish: "i approve your recommendations for all 555 open decisions." | BNL-PRC-001, open questions |
| 2026-10-02 | Renders: the 45 degree pose and the street bin accepted for renders only; the device label added as a note under BOM line 1; the renders are redrawn to the constructable design at the next render session | Amish: "i approve your recommendations for all 555 open decisions." | Review note 2026-09-26, items 1, 2 and 7 |
