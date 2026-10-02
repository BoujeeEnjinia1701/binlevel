---
doc_id: BNL-DDR-001
title: BinLevel TRL 2 review decisions
project: BinLevel
doc_type: Design decision record
version: "0.3"
status: Draft
date: '2026-10-02'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: Record the TRL 2 review recommendations adopted for TRL 3 work and the items that remain open
- version: "0.2"
  date: '2026-09-25'
  author: Amish Chadha
  change: Recommendations accepted by Amish (DDR-002)
- version: "0.3"
  date: '2026-10-02'
  author: Amish Chadha
  change: O1 and O2 decided by Amish on 2026-10-02 (recommendations approved, BNL-DEC-001)
---

# 0001: TRL 2 review decisions

- **Date:** 2026-09-25
- **Status:** accepted. Items D1 to D10 were decided by Amish on 2026-09-25 ("i accept all your recommendations, go with them across all repos"): go with recommendation. Items O1 and O2 carried no recommendation then; recommendations were written later and approved by Amish on 2026-10-02 ("i approve your recommendations for all 555 open decisions."), recorded in Table 2 and the design decisions register BNL-DEC-001. See BNL-DDR-002 for the follow-on decisions.

## Context

The TRL 2 review note (`docs/REVIEW.md`, session 2026-09-25, /populate) listed nine items as "Proposed, awaiting Amish", and the design precis BNL-PRC-001 v0.2 listed six key design choices, each with a rationale. On 2026-09-25 Amish asked for this batch of repos to be taken through the usual process with the instruction "you know the drill, nothing gets past TRL 3". He has not reviewed this repo's items one by one. Every item that carried a recommendation is therefore adopted as recommended for TRL 3 work, open for his review. Items without a recommendation stay open, and no choice is made for them.

## Options considered

The options for each item are those listed in `docs/REVIEW.md` (session 2026-09-25, /populate) and in BNL-PRC-001 v0.2, Key design choices.

## Decision

*Table 1. Items decided by Amish.*

| # | Item | Recommendation adopted | Status |
| --- | --- | --- | --- |
| D1 | First target container | (a) 660 to 1,100 L four-wheel communal containers (EN 840 class); street litter bins follow with the same electronics and a smaller bracket | Decided by Amish, 2026-09-25: go with recommendation |
| D2 | Sensing method | (a) Ultrasonic plus near-range ToF, because the 80 % threshold lies inside the ultrasonic blind zone | Decided by Amish, 2026-09-25: go with recommendation |
| D3 | Cell size | (a) C-size Li-SOCl2 for margin in cold climates and a 10-year service interval; AA revisited for litter bins | Decided by Amish, 2026-09-25: go with recommendation |
| D4 | Radio | (a) LoRaWAN on an STM32WL-class module shared with FieldNode | Decided by Amish, 2026-09-25: go with recommendation |
| D5 | Relationship to FieldNode and TwinKit | Reuse FieldNode's radio module family, payload conventions and decoder, not its enclosure, panel or cell; TwinKit as the reference gateway and data layer | Decided by Amish, 2026-09-25: go with recommendation |
| D6 | Default fill threshold and reporting interval | 80 % and 1 h (2 h at SF11 to SF12) | Decided by Amish, 2026-09-25: go with recommendation |
| D7 | Temperature alert | 70 °C or a rise of 15 K in 15 min, as a maintenance aid only | Decided by Amish, 2026-09-25: go with recommendation |
| D8 | Mounting (precis choice 2) | Under the lid, with four tamper-resistant through-bolts | Decided by Amish, 2026-09-25: go with recommendation |
| D9 | Enclosure (precis choice 5) | Stock IP67 enclosure at TRL 2 to 3; potted or IP69K design later | Decided by Amish, 2026-09-25: go with recommendation |
| D10 | Budget, pitch and problem | No change was recommended: `budget_usd` stays $60 and the pitch and problem lines stay as written | Decided by Amish, 2026-09-25: go with recommendation |

*Table 2. Items left open on 2026-09-25, decided on 2026-10-02.*

| # | Item | Options | Status |
| --- | --- | --- | --- |
| O1 | Steel containers | (a) External lid antenna as an optional variant (about $8, which takes the parts cost to $63, over the $60 budget); (b) exclude steel containers from the first pilot. No recommendation was made. | Decided by Amish, 2026-10-02 (recommendation approved): (b), steel containers left out of the first pilot, which uses plastic containers only; the external lid antenna is revisited once the link loss inside a steel container has been measured (BNL-DEC-001) |
| O2 | First partner and region for co-design and a pilot | No preference stated and no recommendation made. The region also sets the radio plan (EU868, US915 or IN865). | Decided by Amish, 2026-10-02 (recommendation approved): first partner to approach is a municipal waste service or its contractor using EN 840 plastic communal containers in a city with public LoRaWAN coverage, by default a European city on EU868; washing practice asked before committing (BNL-DEC-001) |

## Consequences

- BNL-PRB-001, BNL-PRC-001 and BNL-REQ-001 move to version 0.3. The target container, sensing method, cell, radio, thresholds and mounting are no longer described as proposed; they are the design basis for TRL 3, decided by Amish on 2026-09-25.
- No requirement target was relaxed or redefined by these decisions. R3 and R9 now carry the adopted defaults (D6, D7) as the design values.
- The sizing note BNL-CAL-001 checks the design against every requirement. It adds four findings that need Amish's review (see `docs/REVIEW.md`, session 2026-09-25, TRL 3): the unit is about 435 g against the 400 g limit of R16; hot dark lids reach about 67 °C, above the 60 °C of R6; the 15 K rate-of-rise trigger in D7 is at risk of false alarms on sunny days; and the payload is cut from 12 to 11 bytes so that it fits the US915 slowest data rate.
- The recommended budget is unchanged, so no budget figure awaits Amish.
- Update, 2026-09-25: Amish accepted all recommendations. D1 to D10 are decided; the four findings above were resolved by BNL-DDR-002 (aluminium bracket, R6 to 70 °C, gated rate-of-rise rule, 11-byte payload and 5 min reads confirmed).
