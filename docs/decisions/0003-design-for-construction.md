---
doc_id: BNL-DDR-003
title: BinLevel design for construction
project: BinLevel
doc_type: Design decision record
version: "0.3"
status: Draft
date: '2026-10-02'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-30'
  author: Amish Chadha
  change: Changes that make the concept physically buildable, with the reason for each; made under Amish's 2026-09-30 instruction and open for his review
- version: "0.2"
  date: '2026-10-01'
  author: Amish Chadha
  change: Budget treated as a value-engineering target
- version: "0.3"
  date: '2026-10-02'
  author: Amish Chadha
  change: Accepted by Amish, including the recommendation for A2
---

# 0003: Design for construction

- **Date:** 2026-09-30
- **Status:** accepted. Amish, 2026-10-02: "i approve your recommendations for all 555 open decisions." This covers every change in Tables 1 and 2 and the recommendation for A2, now decided as recommended and recorded in the design decisions register (BNL-DEC-001). A1 is a value-engineering note, not a decision; it is carried in the register's Value engineering section. Made under Amish's 2026-09-30 instruction to make the design physically buildable. Nothing here changes what BinLevel does, its pitch or its safety case.

## Context

On 2026-09-30 Amish asked for every repo to carry an illustrated prototype build plan that shows how each component is made and how it fits the next, and wrote: "If you are realising that the design cannot be built as per concept - fix the design assumptions to match and be physically feasible as you draw the illustrations." The TRL 3 model of BNL-DDR-002 was a massing model: it showed what BinLevel does, but several of its parts floated, overlapped or had no fixing, and one bought part (the ultrasonic driver board) was missing. Checking the model with build123d found the eleven problems below. The review note of 2026-09-26 had already found three of them (the bolt shank above the head, the nut inside the plate and the missing sealing washer).

The changes keep what the unit does: the same sensing (ultrasonic plus ToF, same positions along the box), radio, cell, antenna, mounting under the lid with four tamper bolts on the same 130 x 60 mm pattern, and the same privacy and safety features. Every change is in `cad/src/model.py`, which now builds every component by name and runs 192 constructability checks (`python cad/src/model.py --check`): no two parts overlap, the 32 pairs that must touch do touch, the 0.5 mm gap round the transducer is within what silicone can fill, 22 clearances are met, every part touches at least one other, and the unit fits the R16 envelope. All 192 pass.

## Decision

*Table 1. Changes made to the model, the BOM and the calculations.*

| # | Problem in the concept | Change made | Why this way |
| --- | --- | --- | --- |
| P1 | The box had no fixing to the bracket. Two 60 x 30 mm end tabs hung from the plate to "clamp the enclosure ends", but nothing held them to the box, and their fold lines lay 16.5 mm in from the plate ends, so they could not be folded from a flat blank. | Tabs removed. Four M4 x 12 flush-head press-in studs in the plate (80 x 36 mm pattern) pass through 4.5 mm holes in the base floor; inside, an M4 bonded sealing washer and an M4 x 30 hex standoff go on each stud and clamp the base to the plate. | The plate's top face stays flat against the lid (the stud heads are flush), the box seals at each hole, and the standoffs also carry the electronics board. Press-in studs are a routine sheet-metal shop operation. Each stud carries 12 N at 20 g against a pull-through strength of about 2,100 N [J3]. |
| P2 | The M6 x 40 bolts ran 2.7 mm above their heads and 24 mm below the nut; the nyloc nuts overlapped the plate by 2 mm; the sealing washers were in the BOM but not the model. | M6 x 20 tamper bolts with an 18 mm sealing washer under each head on top of the lid; an M6 plain washer and nyloc nut under the plate, 1.5 mm clear of the box end. | Grip of 16 mm plus two threads. The nut is turned with an open spanner from the side while the bolt is held from above. |
| P3 | The ultrasonic module's driver board (about 41 x 28 mm, part of BOM line 3) was not in the model, and there was no room for it in a 45 mm tall box. | Box height 45 to 55 mm (115 x 65 x 55 mm). The driver board hangs under the electronics board on four 4 mm nylon standoffs, between the transducer and the ToF holder. | The cell (26 mm) above the board and the driver board and sensors below it need 50 mm inside. The unit is now 71.5 mm below the lid, inside R16's 100 mm. |
| P4 | The carrier board floated at mid height with no fixing, cut 0.1 mm into the top of the transducer, and at 105 x 55 mm clashed with the corner screw towers that every stock box has. The board layout is TRL 4 work. | For the prototype, a 90 x 50 mm perforated prototyping board with bought breakouts stands in for the carrier PCB. It hangs from the four standoffs on M4 x 8 screws, 10 mm above the transducer. | Same function and parts; clear of the towers by 1.6 mm. Board slots carry the cell strap (P9). |
| P5 | The transducer sat in its 25 mm hole with nothing holding it. | A printed ASA collar slides over the probe inside the cover and is bonded to the floor with plastics epoxy; an M3 nylon-tipped grub screw clamps the probe; neutral-cure silicone fills the 0.5 mm gap in the hole. | Holds the probe at its 14.5 mm protrusion without new holes in the box, and lets the probe be replaced. |
| P6 | The ToF board floated 4.8 mm above the floor, and the window was drawn as a plug inside the 11 mm hole. | A printed ASA holder is bonded over the hole. It holds a 16 x 1.5 mm PMMA or glass window disc against the floor (sealed with silicone) and the breakout, sensor down, in a pocket 3.5 mm above the window. | The window seals from inside, so water pressure pushes it onto its seat. |
| P7 | The M8 vent was in BOM line 9 but not in the model. | Vent in the cover floor on the short centre line, 20 mm toward the front edge, facing down, its nut inside. | Faces down so it drains; clear of the driver board by 4.8 mm. |
| P8 | The gasket was drawn as a ring outside the box walls, cutting into them. The box was one solid. | Box modelled as a base (fixed to the plate) and a 15 mm cover (carrying the sensors), with the stock gasket in the base rim groove, four corner screw towers and four cover screws. | Matches a stock IP67 box; the cover faces down, so it is opened from below with the bin lid lifted. |
| P9 | The cell floated 2 mm above the board in no holder. | Cell holder on the board's top face; a 10 mm hook-and-loop strap passes round the cell and through two 12 x 3 mm slots in the holder base and the board. | Retains the cell at 20 g (10 N needed [J2]). |
| P10 | The radio module floated above the board. | The RAK3172 on its maker's breakout, on 3 mm header pins. | Bought part for the prototype. |
| P11 | The sensors in the cover were wired to the board with no way to take the cover off. | The transducer cable and a six-way ToF lead end in plugs at the board. | The cover comes away from below once both plugs are out. |

*Table 2. Knock-on changes.*

| Item | Change | Reason |
| --- | --- | --- |
| Mass | 334 to 350 g, inside R16's 400 g [I1]. | Taller box (+20 g), fixings (+22 g), printed parts (+5 g); tabs (-20 g) and shorter bolts (-12 g) removed. |
| Envelope | Below the lid 150 x 80 x 61.5 mm to 150 x 80 x 71.5 mm (R16: 160 x 90 x 100) [I3]. | Box 10 mm taller. |
| Measurement geometry | Transducer face to container floor 1,011 to 1,000 mm; 80 % fill now 200 mm below the face; ultrasonic reads to 75.0 % fill and ToF from 60.0 %; R2 allowance ±100 mm [A1] to [A3], [B3]. | The face is 10 mm lower. R1 and R2 status unchanged. |
| Shock | 66 to 69 N on the fixing [J1]; new check of the studs [J3]. | Heavier unit. |
| Cost | BOM lines 1, 2, 3, 6, 7 and 9 respecified; lines 10 (box fixings, $2.50) and 11 (printed mounts and window, $1.50) added. Parts $55.00 to $59.00, within the unchanged $60 value-engineering target (`budget_usd`) by $1.00 [K1]; with the external lid antenna (O1) $67.00 [K2]. | Parts added for construction. |
| Drawings | BNL-DWG-001 Rev P4; making sketches BNL-DWG-101 to 106 added. | Follows the model. |
| Documents | BNL-CAL-001 v0.3, BNL-REQ-001 v0.5, BNL-PRC-001 v0.5: mass, envelope, geometry and cost figures updated. No requirement changed status. | Follows the model. |
| Thermal and radio | Unchanged. The unit's assumed heat capacity (400 J/K) already covered about 0.4 kg; the antenna stays on the inner back wall. | |

*Table 3. Items proposed for Amish; A2 accepted as recommended on 2026-10-02.*

| # | Question | Options | Recommendation |
| --- | --- | --- | --- |
| A1 | Value engineering (a note, not a decision). The estimated cost is $59.00 against the $60 value-engineering target, $1.00 under. | (a) confirm prices at TRL 4; (b) look for savings now (for example a cheaper generic box). | (a). |
| A2 | Swapping the cell now means lowering the electronics board (four screws) after the cover is off; the cell lasts about 16 years, so this is rare. | (a) accept; (b) move the cell below the board, which needs a taller box again. | (a). Accepted by Amish, 2026-10-02. |

## Consequences

- With A2 accepted, a cell swap means lowering the electronics board on its four screws after the cover is off.
- `design_state: constructable` in `project.yaml`. The build plan BNL-BLD-001 shows every component and step in pictures generated from the model (`cad/src/build_plan_media.py`).
- Requirement status is unchanged: not met 2 (R5 IP69K, R10 in steel containers), at risk 2 (R2, R6), not verifiable at TRL 3 2 (R7, R12), met 10 (BNL-CAL-001 v0.3).
- The photoreal renders (`media/render-*.png`), `media/card.png`, `media/social-preview.png` and the appearance model `cad/src/product_model.py` still show the concept: 45 mm box, end tabs and a full-size board. They need updating on Amish's Mac, where Blender is.
- The stock box, the transducer, the driver board, the ToF breakout and the studs are chosen at TRL 4; their sizes must be checked against the model then (design decisions register, "To confirm when parts are bought").
