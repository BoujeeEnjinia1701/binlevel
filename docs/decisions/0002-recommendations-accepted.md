---
doc_id: BNL-DDR-002
title: BinLevel recommendations accepted
project: BinLevel
doc_type: Design decision record
version: "0.1"
status: Draft
date: '2026-09-25'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: Record Amish's acceptance of all recommendations and the changes made in the repo
---

# 0002: Recommendations accepted

- **Date:** 2026-09-25
- **Status:** accepted. Every item below that carried a recommendation is "Decided by Amish, 2026-09-25: go with recommendation". Items without a recommendation remain "Proposed, awaiting Amish".

## Context

On 2026-09-25 Amish wrote, in chat: "i accept all your recommendations, go with them across all repos." BinLevel had ten items adopted for TRL 3 under his earlier instruction and open for his review (BNL-DDR-001, D1 to D10), four new items raised by the sizing note BNL-CAL-001 v0.1 with a recommendation each, one suggestion on the reporting interval, and two items with no recommendation (O1, O2). Where a recommendation offered several options, the recommended option is the decision. TRL 4 remains on hold by Amish's instruction, and the repo stays at TRL 3.

## Decision

*Table 1. Items decided by Amish, 2026-09-25: go with recommendation.*

| # | Item | Decision | What changed in the repo |
| --- | --- | --- | --- |
| D1 to D10 | TRL 2 review items (BNL-DDR-001): communal containers first, ultrasonic plus ToF, C cell, LoRaWAN on RAK3172, FieldNode and TwinKit reuse, 80 % and 1 h defaults, heat alert, lid mounting, stock IP67 enclosure, no budget change | As recommended | Status wording in BNL-DDR-001 (v0.2), BNL-PRB-001, BNL-PRC-001 and README; no design change |
| N1 | R16 mass: (a) 2 mm aluminium bracket, (b) relax R16 to 450 g, (c) perforated stainless | (a) 2 mm 5052-class aluminium bracket | `cad/src/model.py` plate 1.5 mm stainless to 2.0 mm aluminium; STEP and STL re-exported; BOM item 2 renamed and respecified (price unchanged at $5.00); drawing BNL-DWG-001 to Rev P2; BNL-CAL-001 v0.2: unit mass 435 g to 334 g, envelope below the lid 61.0 to 61.5 mm, shock load 85 to 66 N; R16 from not met to met |
| N2 | R6 upper limit | Raise from 60 to 70 °C; name the RAK3172-T (-40 to 85 °C) for cold sites | BNL-REQ-001 R6 target; BNL-CAL-001 speed-of-sound range now -20 to 70 °C (uncompensated error up to +8.2 %, was +6.6 %); R6 stays at risk (3 K margin, transducer rating unconfirmed) |
| N3 | R9 rate-of-rise rule | Count the 15 K rise in 15 min only when the unit is already above 50 °C; keep the 70 °C absolute alert | BNL-REQ-001 R9 target; BNL-PRC-001 firmware rule; BNL-CAL-001 new checks H3 and H4 (unit about 43 °C under cloud, below the gate; worst rise above the gate 10.9 K); R9 from at risk to met on paper |
| N4 | 11-byte payload and 5 min temperature reads | Keep both, as applied at TRL 3 | Status wording only |
| N5 | Reporting interval stretch (suggestion in BNL-CAL-001 v0.1) | Stretch the routine interval to 2 h at SF12 only; SF11 stays hourly (21.4 s a day, inside TTN's 30 s) | BNL-REQ-001 R3, BNL-PRC-001, BNL-CAL-001 section E, concept media key figures; worst-case battery life unchanged at 16.3 years |
| N6 | Budget | No change was recommended | `budget_usd` stays $60; parts total stays $55.00 |

*Table 2. Items still open.*

| # | Item | Status |
| --- | --- | --- |
| O1 | Steel containers: (a) external lid antenna variant (about $8, total $63.00, over budget) or (b) exclude steel containers from the first pilot. No recommendation was made. | Proposed, awaiting Amish |
| O2 | First partner and region for co-design and a pilot; also sets the radio plan (EU868, US915 or IN865). No preference stated. | Proposed, awaiting Amish |

*Table 3. Decided but on hold or outside this repo.*

| Item | Status |
| --- | --- |
| TRL 4 work named in the review note (bench build, lab test report, ranging on real waste, current and cold-start measurements, link loss in HDPE and steel containers, lid temperature in sun, shake and drop) | Decided as the next step, on hold: TRL 4 is on hold by Amish's instruction |
| FieldNode's 20-byte payload exceeds the 11-byte US915 DR0 limit found here, and FieldNode stretches its interval from SF10 | Cross-repo action for FieldNode, listed in `docs/REVIEW.md`; FieldNode not edited |

## Consequences

- Requirement status (BNL-CAL-001 v0.2): not met 2 (R5 IP69K; R10 in steel containers), at risk 2 (R2, R6), not verifiable at TRL 3 2 (R7, R12), met 10 (R1, R3, R4, R9, R14, R16 by calculation; R8, R11, R13, R15 by design). Before this record: not met 3, at risk 3, met 8.
- Controlled documents bumped: BNL-PRB-001 v0.4, BNL-PRC-001 v0.4, BNL-REQ-001 v0.4, BNL-CAL-001 v0.2, BNL-DDR-001 v0.2; drawing BNL-DWG-001 Rev P2.
- The stainless bolts now pass through an aluminium plate. Galvanic isolation (anodized plate or insulating washers) is a review suggestion, not a decision.
- `trl: 3` and `trl_target: 3` are unchanged.
