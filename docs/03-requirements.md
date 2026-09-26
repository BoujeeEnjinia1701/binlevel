---
doc_id: BNL-REQ-001
title: BinLevel requirements
project: BinLevel
doc_type: Requirements
version: "0.2"
status: Draft
date: '2026-09-25'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: Initial scaffold
- version: "0.2"
  date: '2026-09-25'
  author: Amish Chadha
  change: First measurable requirements for TRL 2, with status against the concept
---

# BinLevel requirements

These are first-pass requirements for the concept. Targets are proposals awaiting Amish and co-design partners, and will be checked by calculation at TRL 3. Status reflects the TRL 2 concept estimates in the design precis (BNL-PRC-001). Three requirements are not met or are at risk (R2, R5 and R10); see the notes under Table 1.

Table 1. Requirements.

| ID | Requirement | Target | Verification (TRL 3 or later) | Concept status |
| --- | --- | --- | --- | --- |
| R1 | Measure distance from lid to waste surface over the full depth of the target container | 0.03 to 1.5 m below the sensor face | Datasheet review; later bench test in a container | Met by design with two sensors (ultrasonic 0.25 to 1.5 m, ToF 0.03 to 0.4 m, estimates) |
| R2 | Report fill level accurately on real mixed waste | Within ±10 % of container depth for 90 % of readings | Field comparison against manual dip readings | **At risk**: bags, cardboard and uneven surfaces scatter the echo; unverified |
| R3 | Report often enough to plan routes, and quickly when full | Routine uplink at least every 2 h; threshold alert within 20 min of crossing the set fill level (default 80 %) | Timing calculation; firmware configuration | Met by design: ranging every 15 min |
| R4 | Run for years on one battery | 5 years or more in the worst radio case (SF12); 10 years design target | Power budget calculation | Met on paper: about 18 years (SF12, C cell) estimate; enclosure and seals, not the cell, limit life |
| R5 | Survive rain, condensation and washing | IP67 minimum; IP69K target where containers are pressure washed | Enclosure datasheet; later spray test | **Not met for IP69K**: stock IP67 box proposed |
| R6 | Operate across the climate range | -20 to +60 °C inside the container | Datasheet review | Met on paper for cell and radio; transducer and ToF window condensation unverified |
| R7 | Survive lifting, tipping and lid slams | Repeated shocks of the emptying cycle without loosening; target IK08 impact on the enclosure | Design review; later drop and shake test | Unverified; bracket with four through-bolts proposed |
| R8 | Detect and report emptying and lid events | Tip event from the accelerometer reported with the next uplink | Firmware logic review | Met by design |
| R9 | Warn of abnormal heat in the bin | Alert uplink within 15 min when temperature exceeds 70 °C or rises more than 15 K in 15 min | Firmware logic review | Met by design; maintenance aid only, not a fire detector |
| R10 | Connect over open LoRaWAN within radio rules | LoRaWAN 1.0.x Class A; EU868, US915 and IN865 plans; within duty cycle and TTN's 30 s per day fair use | Airtime calculation; later range test | **At risk in steel containers**: internal antenna shielded; external antenna option needed |
| R11 | Protect privacy | No camera or microphone; payload limited to fill, distance, temperature, tilt, events and battery | Design review of BOM and payload | Met by design |
| R12 | Install without wiring or tools beyond a drill | Fit to a lid in 10 min or less with four bolts or rivets; no cables | Timed trial at TRL 4 | Met by design (estimate) |
| R13 | Resist casual tampering and theft | Mounted inside the lid; tamper-resistant fasteners | Design review | Met by design |
| R14 | Low cost and buildable | Parts cost $60 or less per sensor at prototype quantities; no custom tooling | Priced BOM | Met: about $55 (indicative) |
| R15 | Open and interoperable | Documented payload format and open decoder; works with any LoRaWAN network server | Documentation review | Met by design |
| R16 | Light and compact | 400 g or less; no larger than 160 x 90 x 100 mm below the lid, including bracket | Massing model, then weighing | Met: about 250 g, 150 x 80 x 63 mm below the lid (estimates) |

Notes on requirements not met or at risk:

- **R2 at risk.** Ultrasonic echoes from bags, boxes and bulky items are uneven, and the waste surface is rarely flat. The mitigation is to take the median of several pings and to combine the two sensors, but accuracy on real waste is unknown until measured.
- **R5 not met for IP69K.** A low-cost stock enclosure is typically rated IP67. Where containers are washed with hot pressure water, a sealed potted design or an IP69K enclosure is needed, which raises cost.
- **R10 at risk.** An antenna inside a steel container and under a steel lid will lose much of its signal. Plastic (HDPE) containers are fine. Steel containers need an antenna fitted to the outside of the lid or rim.

## Assumptions

- Target container: 1,100 L four-wheel communal container, internal depth about 1.07 m (estimate from the massing model).
- Fill level is reported as a percentage of the distance from the sensor face to the container floor, measured at installation.
- Worst radio case is spreading factor 12 at 125 kHz with a 12-byte payload (about 1.5 s airtime per uplink, estimate); typical urban case is SF9 (about 0.21 s).
- Temperatures inside a closed dark lid may reach about 60 °C in summer (estimate, to be measured).
