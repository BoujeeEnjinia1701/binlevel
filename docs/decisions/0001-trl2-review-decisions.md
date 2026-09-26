---
doc_id: BNL-DDR-001
title: BinLevel TRL 2 review decisions
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
  change: Record the TRL 2 review recommendations adopted for TRL 3 work and the items that remain open
---

# 0001: TRL 2 review decisions

- **Date:** 2026-09-25
- **Status:** proposed. The recommendations in items D1 to D10 are adopted for TRL 3 work pending Amish's review; items O1 and O2 remain "Proposed, awaiting Amish".

## Context

The TRL 2 review note (`docs/REVIEW.md`, session 2026-09-25, /populate) listed nine items as "Proposed, awaiting Amish", and the design precis BNL-PRC-001 v0.2 listed six key design choices, each with a rationale. On 2026-09-25 Amish asked for this batch of repos to be taken through the usual process with the instruction "you know the drill, nothing gets past TRL 3". He has not reviewed this repo's items one by one. Every item that carried a recommendation is therefore adopted as recommended for TRL 3 work, open for his review. Items without a recommendation stay open, and no choice is made for them.

## Options considered

The options for each item are those listed in `docs/REVIEW.md` (session 2026-09-25, /populate) and in BNL-PRC-001 v0.2, Key design choices.

## Decision

*Table 1. Items adopted for TRL 3 work.*

| # | Item | Recommendation adopted | Status |
| --- | --- | --- | --- |
| D1 | First target container | (a) 660 to 1,100 L four-wheel communal containers (EN 840 class); street litter bins follow with the same electronics and a smaller bracket | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D2 | Sensing method | (a) Ultrasonic plus near-range ToF, because the 80 % threshold lies inside the ultrasonic blind zone | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D3 | Cell size | (a) C-size Li-SOCl2 for margin in cold climates and a 10-year service interval; AA revisited for litter bins | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D4 | Radio | (a) LoRaWAN on an STM32WL-class module shared with FieldNode | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D5 | Relationship to FieldNode and TwinKit | Reuse FieldNode's radio module family, payload conventions and decoder, not its enclosure, panel or cell; TwinKit as the reference gateway and data layer | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D6 | Default fill threshold and reporting interval | 80 % and 1 h (2 h at SF11 to SF12) | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D7 | Temperature alert | 70 °C or a rise of 15 K in 15 min, as a maintenance aid only | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D8 | Mounting (precis choice 2) | Under the lid, with four tamper-resistant through-bolts | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D9 | Enclosure (precis choice 5) | Stock IP67 enclosure at TRL 2 to 3; potted or IP69K design later | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |
| D10 | Budget, pitch and problem | No change was recommended: `budget_usd` stays $60 and the pitch and problem lines stay as written | Adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review |

*Table 2. Items that remain open.*

| # | Item | Options | Status |
| --- | --- | --- | --- |
| O1 | Steel containers | (a) External lid antenna as an optional variant (about $8, which takes the parts cost to $63, over the $60 budget); (b) exclude steel containers from the first pilot. No recommendation was made. | Proposed, awaiting Amish |
| O2 | First partner and region for co-design and a pilot | No preference stated and no recommendation made. The region also sets the radio plan (EU868, US915 or IN865). | Proposed, awaiting Amish |

## Consequences

- BNL-PRB-001, BNL-PRC-001 and BNL-REQ-001 move to version 0.3. The target container, sensing method, cell, radio, thresholds and mounting are no longer described as proposed; they are the design basis for TRL 3, open for Amish's review.
- No requirement target was relaxed or redefined by these decisions. R3 and R9 now carry the adopted defaults (D6, D7) as the design values.
- The sizing note BNL-CAL-001 checks the design against every requirement. It adds four findings that need Amish's review (see `docs/REVIEW.md`, session 2026-09-25, TRL 3): the unit is about 435 g against the 400 g limit of R16; hot dark lids reach about 67 °C, above the 60 °C of R6; the 15 K rate-of-rise trigger in D7 is at risk of false alarms on sunny days; and the payload is cut from 12 to 11 bytes so that it fits the US915 slowest data rate.
- The recommended budget is unchanged, so no budget figure awaits Amish.
