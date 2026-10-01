---
doc_id: BNL-DEC-001
title: BinLevel design decisions register
project: BinLevel
doc_type: Design decisions register
version: "0.1"
status: Draft
date: '2026-09-30'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
  - version: "0.1"
    date: '2026-09-30'
    author: Amish Chadha
    change: Register opened with the open decisions from the review note, the decision records and the build plan work
---

# BinLevel design decisions register

Every design decision still to be made, and every decision made, in one place. Each decision is argued in full in its decision record under `docs/decisions/`; this register is the index Amish works from. The build plan (`docs/05-build-plan.md`) describes the design as it stands and does not list open decisions.

## Open decisions

| # | Decision needed | Options | Recommendation | Affects in the build | Source |
| --- | --- | --- | --- | --- | --- |
| 1 | Review the design-for-construction changes P1 to P11 (box on studs and standoffs, no tabs, M6 x 20 bolts, 55 mm box, prototyping board, printed sensor mounts, vent, plugs) | Accept; change any item | Accept | The whole build plan | BNL-DDR-003 |
| 2 | Budget margin of $1.00 after the parts added for construction ($59.00 against $60) | (a) accept and confirm prices at TRL 4; (b) look for savings now, for example a cheaper generic box | (a) | Bill of materials | BNL-DDR-003, A1 |
| 3 | Cell swap now means lowering the electronics board (four screws) after the cover is off | (a) accept, since the cell lasts about 16 years; (b) move the cell below the board, which needs a taller box | (a) | Steps 7 and 8 | BNL-DDR-003, A2 |
| 4 | Steel containers | (a) external lid antenna variant (about $8, parts $67.00, over budget); (b) leave steel containers out of the first pilot | None made | Antenna and bracket; budget | BNL-DDR-001 and BNL-DDR-002, O1 |
| 5 | First partner and region for co-design and a pilot | Partner and region; the region also sets the radio band (EU868, US915 or IN865) | None made | Radio module build and antenna band; whether IP67 is enough for the partner's washing practice | BNL-DDR-001 and BNL-DDR-002, O2 |
| 6 | Galvanic isolation between the stainless bolts and studs and the aluminium plate | (a) anodised plate; (b) insulating washers and sleeves; (c) nothing for the prototype, decide for deployments | (c) for the prototype, (a) for deployments | Bracket plate finish | BNL-DDR-002, Consequences; review note 2026-09-25 |
| 7 | Route planner and data layer for the pilot | TwinKit, a city system, or an open-source vehicle routing tool | None made | Not part of the TRL 3 build | BNL-PRC-001, open questions |
| 8 | Whether the payload also carries a rolling fill-rate estimate | Add it in the spare byte; leave it to the server | None made | Firmware only; not part of the TRL 3 build | BNL-PRC-001, open questions |
| 9 | Photoreal render choices: render pose turned 45° about the lid hinge, compact street bin as context, a device label with no BOM line | Accept each; change | Accept the pose and the street bin for renders only; add the label as a note under BOM line 1 if wanted | Renders only; the renders also need redrawing to the constructable design | Review note 2026-09-26, items 1, 2 and 7 |

## To confirm when parts are bought

| # | What to confirm | Why it matters | Source |
| --- | --- | --- | --- |
| 1 | The stock box: 115 x 65 x 55 mm outside, a 15 mm deep cover, corner towers about 9 mm across at about 51 and 26 mm from the centre lines, and a flat base floor | The board size, the stud positions and the sealing washers depend on it | BNL-DDR-003, P1, P4 and P8 |
| 2 | The transducer probe's diameter (24 mm assumed), its cable plug and its temperature rating | Sets the 25 mm hole and the collar bore; R6 is at risk on the rating | BNL-DDR-003, P5; BNL-CAL-001, section H |
| 3 | The driver board's size and mounting holes (about 41 x 28 mm assumed) | Sets the four driver holes in the electronics board and its clearance to the probe and the holder | BNL-DDR-003, P3 |
| 4 | The light sensor breakout's size, holes and sensor position (13 x 18 mm, sensor underneath, assumed) | Sets the holder pocket | BNL-DDR-003, P6 |
| 5 | The press-in stud's hole size, minimum sheet thickness and push-out rating in 2 mm 5052 aluminium (4.2 mm and about 900 N assumed) | The plate holes and the fixing check | BNL-CAL-001, [J3] |
| 6 | The cell holder takes a C cell with room for the strap slots | Cell retention at 20 g | BNL-CAL-001, [J2] |

## Decisions made

| Date | Decision | Decided by | Record |
| --- | --- | --- | --- |
| 2026-09-25 | TRL 2 review items D1 to D10: communal containers first, ultrasonic plus ToF, C cell, LoRaWAN on RAK3172, FieldNode and TwinKit reuse, 80 % and 1 h defaults, heat alert, lid mounting with four tamper bolts, stock IP67 box, no budget change | Amish: "i accept all your recommendations, go with them across all repos." | [BNL-DDR-001](decisions/0001-trl2-review-decisions.md), [BNL-DDR-002](decisions/0002-recommendations-accepted.md) |
| 2026-09-25 | 2 mm 5052-class aluminium bracket; R6 upper limit 70 °C with the RAK3172-T for cold sites; heat rate rule counted only above 50 °C; 11-byte payload and 5 min temperature reads; 2 h interval at SF12 only; budget stays $60 | Amish, same instruction | [BNL-DDR-002](decisions/0002-recommendations-accepted.md), N1 to N6 |
| 2026-09-30 | Design for construction: box held on four studs and standoffs, no tabs, M6 x 20 bolts, 55 mm box, prototyping board on standoffs, printed sensor mounts, vent, plugged sensor leads | Made under Amish's 2026-09-30 instruction to make the design physically buildable ("fix the design assumptions to match and be physically feasible"); open for his review (open decision 1) | [BNL-DDR-003](decisions/0003-design-for-construction.md) |
