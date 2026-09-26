---
doc_id: BNL-REQ-001
title: BinLevel requirements
project: BinLevel
doc_type: Requirements
version: "0.4"
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
- version: "0.3"
  date: '2026-09-25'
  author: Amish Chadha
  change: Status checked by calculation (BNL-CAL-001); adopted defaults from BNL-DDR-001 written into R3 and R9; 11-byte payload
- version: "0.4"
  date: '2026-09-25'
  author: Amish Chadha
  change: Recommendations accepted by Amish (DDR-002)
---

# BinLevel requirements

These requirements are the TRL 3 design basis. The design choices behind them were decided by Amish on 2026-09-25 (go with recommendation; BNL-DDR-001 and BNL-DDR-002). Under DDR-002, R6's upper limit is raised from 60 to 70 °C, R9's rate-of-rise rule counts only above 50 °C, and R3's 2 h interval applies at SF12 only; no other target changed. Status is from the sizing note BNL-CAL-001 v0.2, which checks each requirement against the parametric model: two are not met (R5, R10 in steel containers), two are at risk (R2, R6), two can only be settled by test (R7, R12) and ten are met (six by calculation, four by design). See the notes under Table 1.

Table 1. Requirements.

| ID | Requirement | Target | Verification (TRL 3 or later) | Status at TRL 3 (BNL-CAL-001) |
| --- | --- | --- | --- | --- |
| R1 | Measure distance from lid to waste surface over the full depth of the target container | 0.03 to 1.5 m below the sensor face | Calculation and datasheet review; later bench test in a container | Met: 0 to 1.01 m needed; ultrasonic from 0.25 m, ToF to 0.4 m, overlapping between 60 % and 75 % fill (datasheet ranges to confirm) |
| R2 | Report fill level accurately on real mixed waste | Within ±10 % of container depth for 90 % of readings | Error budget; later field comparison against manual dip readings | **At risk**: instrument error about 10 mm (ultrasonic) and 20 mm (ToF) of the ±101 mm allowance; the waste surface is unknown |
| R3 | Report often enough to plan routes, and quickly when full | Routine uplink at least every 2 h (default 1 h, 2 h at SF12 only); threshold alert within 20 min of crossing the set fill level (default 80 %) | Timing calculation | Met: worst-case alert 17.5 min |
| R4 | Run for years on one battery | 5 years or more in the worst radio case (SF12); 10 years design target | Power budget calculation | Met: 16.3 years on a C cell at SF12; enclosure and seals, not the cell, limit life |
| R5 | Survive rain, condensation and washing | IP67 minimum; IP69K target where containers are pressure washed | Enclosure datasheet; later spray test | **Not met for IP69K**: stock IP67 box (DDR-001, D9) |
| R6 | Operate across the climate range | -20 to +70 °C inside the container (raised from +60 °C, DDR-002); RAK3172-T for sites colder than -20 °C | Heat balance and datasheet review | **At risk**: a dark lid reaches about 67 °C on a 40 °C day, 3 K inside the limit; the standard module is rated only down to -20 °C; transducer rating and condensation unverified |
| R7 | Survive lifting, tipping and lid slams | Repeated shocks of the emptying cycle without loosening; target IK08 impact on the enclosure | Load calculation; later drop and shake test | Not verifiable at TRL 3: 85 N at 20 g against about 4,200 N per bolt; loosening and impact need a test |
| R8 | Detect and report emptying and lid events | Tip event from the accelerometer reported with the next uplink | Firmware logic review | Met by design |
| R9 | Warn of abnormal heat in the bin | Alert uplink within 15 min when temperature exceeds 70 °C, or rises more than 15 K in 15 min while above 50 °C (gate added, DDR-002) | Timing calculation and heat balance | Met on paper: alert within 7.5 min with temperature read every 5 min; sun through cloud starts the unit at about 43 °C, below the gate, and above it the worst sun rise is 10.9 K; maintenance aid only, not a fire detector |
| R10 | Connect over open LoRaWAN within radio rules | LoRaWAN 1.0.x Class A; EU868, US915 and IN865 plans; within duty cycle and TTN's 30 s per day fair use | Airtime and link calculation; later range test | **Not met in steel containers** with the internal antenna (about 0.35 km at SF12); met in HDPE containers: 20.8 s per day at SF12, 11-byte payload fits US915 DR0, about 0.8 to 1.3 km range |
| R11 | Protect privacy | No camera or microphone; payload limited to fill, distance, temperature, tilt, events and battery | Design review of BOM and payload | Met by design |
| R12 | Install without wiring or tools beyond a drill | Fit to a lid in 10 min or less with four bolts or rivets; no cables | Timed trial at TRL 4 | Not verifiable at TRL 3: four through-bolts on a 130 x 60 mm pattern, no cables |
| R13 | Resist casual tampering and theft | Mounted inside the lid; tamper-resistant fasteners | Design review | Met by design |
| R14 | Low cost and buildable | Parts cost $60 or less per sensor at prototype quantities; no custom tooling | Priced BOM | Met: $55.00 (indicative); $63.00 with the external antenna option |
| R15 | Open and interoperable | Documented payload format and open decoder; works with any LoRaWAN network server | Documentation review | Met by design: candidate 11-byte layout in BNL-CAL-001 |
| R16 | Light and compact | 400 g or less; no larger than 160 x 90 x 100 mm below the lid, including bracket | Mass calculation from the model, then weighing | Met: about 334 g with a 2 mm aluminium bracket (DDR-002; was 435 g with 1.5 mm stainless); 150 x 80 x 61.5 mm |

Notes on requirements not met or at risk:

- **R2 at risk.** Ultrasonic echoes from bags, boxes and bulky items are uneven, and the waste surface is rarely flat. The mitigation is to take the median of several pings and to combine the two sensors, but accuracy on real waste is unknown until measured.
- **R5 not met for IP69K.** A low-cost stock enclosure is typically rated IP67. Where containers are washed with hot pressure water, a sealed potted design or an IP69K enclosure is needed, which raises cost.
- **R6 at risk.** The upper limit is now 70 °C (DDR-002), above the about 67 °C a dark lid reaches in hot sun, but the margin is only 3 K and the transducer's rating is unconfirmed. The RAK3172-T (-40 to 85 °C) is named for cold sites.
- **R10 not met in steel containers.** An antenna inside a steel container loses about 30 dB (assumed). HDPE containers are fine within about 1 km of a gateway. The external antenna or the exclusion of steel containers is still open, awaiting Amish (DDR-001, O1).

## Assumptions

- Target container: 1,100 L four-wheel communal container (DDR-001, D1), lid underside 1.07 m above the inner floor and transducer face 1.01 m above it (from the parametric model).
- Fill level is reported as a percentage of the distance from the sensor face to the container floor, measured at installation.
- Worst radio case is spreading factor 12 at 125 kHz with an 11-byte payload (1.48 s airtime per uplink); typical urban case is SF9 (0.21 s).
- A dark lid may reach about 67 °C on a 40 °C day in full sun (BNL-CAL-001, section H; to be measured).
