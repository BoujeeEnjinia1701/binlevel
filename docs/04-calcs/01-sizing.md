---
doc_id: BNL-CAL-001
title: BinLevel sizing calculations
project: BinLevel
doc_type: Calculation
version: "0.3"
status: Draft
date: '2026-09-30'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: First issue for TRL 3 (measurement geometry, accuracy, energy, supply, airtime and payload, link budget, timing, lid temperature, mass, shock, cost)
- version: "0.2"
  date: '2026-09-25'
  author: Amish Chadha
  change: Recommendations accepted by Amish (DDR-002); 2 mm aluminium bracket, R6 to 70 °C, gated rate-of-rise rule, 2 h interval at SF12 only
- version: "0.3"
  date: '2026-09-30'
  author: Amish Chadha
  change: Design for construction (BNL-DDR-003); 55 mm box, no tabs, studs and standoffs, M6 x 20 bolts; geometry, mass, size, fixing and cost re-run; new check J3
---

# BinLevel sizing calculations

On paper, BinLevel meets ten of its sixteen requirements (six by calculation and four by design), has two at risk, misses two and leaves two that only a test can settle. The two misses are R5 (the stock enclosure is IP67, not IP69K) and R10 in steel containers (an antenna inside a steel container loses the link beyond about 0.35 km; the choice of remedy is still open). The two at risk are accuracy on real waste (R2) and the climate range (R6: a dark lid reaches about 67 °C against the new 70 °C limit, and the transducer's rating is unconfirmed). Version 0.2 applies the recommendations Amish accepted on 2026-09-25 (BNL-DDR-002): a 2 mm aluminium bracket brings the unit from about 435 g to 334 g, so R16 is now met; R6's upper limit rises from 60 to 70 °C; the 15 K rate-of-rise heat trigger counts only above 50 °C, which removes the false alarm when sun breaks through cloud, so R9 is now met on paper; and the routine interval stretches to 2 h at SF12 only. Version 0.3 re-runs the geometry, mass, size, fixing and cost checks for the constructable design of BNL-DDR-003 (a 55 mm tall box held on four studs and standoffs, no tabs, shorter bolts and the parts added for construction): the unit is now about 350 g and 71.5 mm below the lid, still inside R16, parts cost $59.00 against $60, and no requirement changes status. Battery life is not a constraint: a C cell lasts about 16 years in the worst radio case. The calculations changed four details of the TRL 2 concept: the payload shrinks from 12 to 11 bytes so that it fits the slowest US915 data rate, the carrier gains a nanopower regulator because a fresh cell exceeds the module's 3.6 V limit, the temperature is read every 5 min so that the heat alert arrives within 15 min, and the cell is strapped rather than held by clips alone. Every number in this note is printed by `docs/04-calcs/sizing.py`; the tag in brackets, for example [C3], is the line of that script's output that carries it.

> **Safety:** These are first-principles estimates for a paper proof of concept. The temperature alert is a maintenance aid and not fire detection. Nothing here replaces checks of the lithium cell's fusing and retention, or safe working practice around bins and collection vehicles. See BNL-PRC-001, Safety.

## Scope and method

The note checks every requirement in BNL-REQ-001 v0.5 against the design in BNL-PRC-001 v0.5 and the parametric model `cad/src/model.py`. The script imports the model's `PARAMS`, `derived()` and part solids, so the container depth, sensor positions, bracket volume and envelope used here are the ones in the STEP files and in drawing BNL-DWG-001. The script also reads `bom/bom.csv` and `budget_usd` in `project.yaml`. Run it from the repo root with `python docs/04-calcs/sizing.py`.

The design case is an 1,100 L four-wheel communal container (DDR-001, D1) with the sensor at the center of an HDPE lid, ranging every 15 min, reporting hourly (2 h at SF12 only, DDR-002) and on alerts (D6), on a LoRaWAN network with a TwinKit or public gateway (D4, D5).

## Assumptions

*Table 1. Main assumptions.*

| Area | Assumption | Basis |
| --- | --- | --- |
| Container | Body 1,300 x 1,000 mm outside, 8 mm wall, inner floor 228 mm and rim 1,300 mm above ground; lid wall 5 mm HDPE | Typical EN 840 1,100 L size (estimate), as in the model |
| Sensing | Ultrasonic blind zone 0.25 m and range to 4 m; effective beam half-angle 15°; ToF used to 0.4 m with a 27° field of view and ±20 mm error including the window | JSN-SR04T-class figures are estimates to confirm; the VL53L1X field of view and 4 m maximum are from the [ST product page](https://www.st.com/en/imaging-and-photonics-solutions/vl53l1x.html) |
| Accuracy | Air temperature known to ±5 K from the on-board sensor; echo detection jitter of half a wavelength; 1 µs timer | Assumed |
| Module | RAK3172: 2.0 to 3.6 V supply, 1.69 µA sleep, -20 to 85 °C (the -T variant -40 to 85 °C) | [RAK3172 datasheet](https://docs.rakwireless.com/product-categories/wisduo/rak3172-module/datasheet/) |
| Currents | Transmit 45 mA at +14 dBm (the datasheet gives only 87 mA at +20 dBm); receive 6 mA for at least 0.1 s or 8 symbols per window; 0.5 s of processing at 3 mA per uplink; sleep 6.0 µA in all (Section C) | Assumed, to be measured |
| Ranging cycle | MCU 3 mA for 0.5 s; ultrasonic module 10 mA for 0.4 s (power-up and five pings 60 ms apart); ToF 20 mA for 0.1 s | Assumed typical module figures |
| Traffic | Two extra uplinks a day for alerts and tip events | Assumed |
| Cell | Li-SOCl2 C (ER26500 class) 8.5 Ah or AA (ER14505 class) 2.6 Ah nominal; 60 % usable for pulses, cold and end-of-life voltage; self-discharge 1 % of nominal a year; 3.67 V open circuit | Typical bobbin-cell data |
| Radio | 11-byte payload plus 13 bytes of LoRaWAN overhead; 125 kHz; coding rate 4/5; 8-symbol preamble; low data rate optimization at SF11 and SF12; US915 slowest rate (DR0, SF10) carries at most 11 bytes of application payload and a 400 ms dwell limit ([TTN](https://www.thethingsnetwork.org/docs/lorawan/regional-limitations-of-rf-use/) for the dwell limit; the 11-byte figure is from the LoRaWAN Regional Parameters and was not re-fetched this session) | LoRaWAN defaults, as in FND-CAL-001 |
| Link | +14 dBm; 0 dBi node antenna with 0.5 dB loss; 2 dBi gateway antenna with 2 dB feeder loss, 30 m high; node 1.3 m high; 6 dB noise figure; Okumura-Hata urban model at 868 MHz; container penalty 10 dB (HDPE, antenna under the lid), 30 dB (steel, antenna inside), 3 dB (steel, external lid antenna); 10 dB fade margin | Screening values; container penalties are assumptions to be measured |
| Lid heat | 40 °C ambient; 900 W/m² sun (100 W/m² under cloud); absorptance 0.9 (dark lid) or 0.5 (light lid); 25 W/m²K above and 5 W/m²K below the lid; unit heat capacity 400 J/K coupled to the lid at 0.75 W/K | Handbook ranges; assumed coupling |
| Shock | 20 g peak when the container strikes the lifter stop; HDPE shear strength 20 MPa; 18 mm washers; M6 stress area 20.1 mm² at 210 MPa | Assumed; the 20 g figure needs measurement |
| Mass | ABS 1.05, stainless 7.9, aluminium 2.68 and FR-4 1.85 g/cm³ applied to model volumes, with ASA 1.07 and PMMA 1.19 g/cm³ for the printed mounts and window; bracket 2.0 mm 5052-class aluminium (DDR-002), no tabs (DDR-003); bought-in parts 174 g (Section I) | Assumed part masses |

## A. Measurement geometry (R1)

- **Depth.** The lid underside is 1,072 mm above the inner floor, and the transducer face sits 1,000 mm above it (1,011 mm before the box grew 10 mm taller under BNL-DDR-003) [A1].
- **Blind zone.** At the adopted 80 % threshold (D6) the waste surface is 200 mm below the face, inside the 250 mm ultrasonic blind zone, so the ultrasonic sensor alone reads fill only up to 75.0 % [A2]. This confirms decision D2.
- **Coverage.** The ToF sensor, used to 400 mm, covers fill from 60.0 % to 100 %, which leaves a 150 mm overlap band where both sensors read and can be compared [A3]. Together they cover the 0 to 1.00 m needed, inside the R1 target of 0.03 to 1.5 m [A4].
- **Beam.** A 15° beam spreads to 0.54 m across at the floor, which averages over uneven waste; the ToF footprint at 0.4 m is 192 mm across [A5]. Mounted at the lid center, the transducer is 492 mm from the nearest wall, so the beam clears the walls down to the floor for half-angles up to 26.2° [A6]. An off-center mount would see echoes from the walls sooner.

## B. Instrument accuracy (R2)

- **Speed of sound.** Over the revised R6 range of -20 to 70 °C the speed of sound runs from 318.9 to 371.3 m/s; without compensation the distance error would be -7.1 % to +8.2 % [B1]. The on-board temperature reading removes most of it.
- **Error budget.** With a 5 K error between the sensor and the air column, the residual is 0.85 %, or 8.5 mm at full depth; echo jitter adds 4.3 mm and the timer 0.17 mm [B2]. The ultrasonic instrument error is 9.5 mm and the ToF error 20 mm, against a ±100 mm allowance (±10 % of depth), so the instruments use 10 % and 20 % of it [B3].
- **Conclusion.** R2 is decided by the waste surface (bags, cardboard, voids and slopes), not by the sensors. No calculation settles it, so R2 stays at risk.

## C. Energy and battery life (R4)

*Table 2. Sleep current [C1].*

| Item | Current |
| --- | --- |
| Module in stop mode (datasheet 1.69 µA, rounded up) | 2.0 µA |
| Accelerometer in wake-on-motion mode (LIS2DH12 class) | 2.0 µA |
| Temperature sensor in shutdown | 0.5 µA |
| Nanopower regulator, load switch and divider leakage | 0.5 µA |
| Buffer capacitor leakage | 1.0 µA |
| **Total** | **6.0 µA** |

- **Daily use.** Sleep takes 0.144 mAh a day; each ranging cycle takes 7.50 mAs, or 0.200 mAh a day at 96 cycles; temperature reads every 5 min add 0.0012 mAh a day [C1]. An uplink takes 3.32 µAh at SF9 and 19.82 µAh at SF12; with two alerts a day the uplinks use 0.086 mAh (SF9, hourly) or 0.278 mAh (SF12, 2-hourly) a day [C2].

*Table 3. Daily charge and life on 60 % of nominal capacity [C3].*

| Case | C cell (8.5 Ah) | AA cell (2.6 Ah) |
| --- | --- | --- |
| SF9, hourly | 0.664 mAh/day; 21.0 years | 0.503 mAh/day; 8.5 years |
| SF12, every 2 h | 0.856 mAh/day; 16.3 years | 0.694 mAh/day; 6.2 years |

- **R4 is met.** The worst case averages 35.7 µA including self-discharge and gives 16.3 years on a C cell and 6.2 years on an AA cell, against 5 years minimum and a 10-year design target [C4]. The TRL 2 estimates (about 23 and 18 years) were optimistic by the extra sleep current and the alert traffic, but the conclusion stands: seals and plastics, not the cell, set the service life. The AA cell meets the 5-year minimum but not the 10-year target, which supports decision D3.

## D. Supply voltage, pulses and heating (R6, R4)

- **Regulator.** A fresh Li-SOCl2 cell rests at 3.67 V, 70 mV above the RAK3172's 3.6 V maximum [D1]. The carrier therefore needs a nanopower 3.3 V regulator (quiescent current well under 1 µA, included in Table 2). This is a change from TRL 2, added to BOM item 6 at no change in its indicative price.
- **Pulse load.** Buffering a whole SF12 uplink (45 mA for 1.48 s) in a capacitor with 0.5 V droop would need 0.133 F [D2], and a supercapacitor of that size leaks several microamperes. The design lets the cell carry the pulse, specifies a cell rated for at least 100 mA pulses, and adds a 1,000 µF low-leakage buffer to cover the voltage delay of a passivated cell. Cold-start voltage delay at -20 °C remains to be tested.
- **Heating is not an option.** A 20 mW heater to keep the ToF window above the dew point would use 133 mAh a day, 156 times the whole budget [D3]. Condensation must be handled by venting, a hydrophobic window and the ultrasonic sensor's tolerance to it.

## E. Airtime, payload and radio rules (R10, R3)

*Table 4. Time on air for an 11-byte uplink (24 bytes on air) at 125 kHz, with two alerts a day [E1].*

| SF | Per uplink | Hourly (s/day) | Every 2 h (s/day) | EU868 1 % off-time |
| --- | --- | --- | --- | --- |
| 7 | 62 ms | 1.6 | 0.9 | 6 s |
| 8 | 113 ms | 2.9 | 1.6 | 11 s |
| 9 | 206 ms | 5.4 | 2.9 | 20 s |
| 10 | 371 ms | 9.6 | 5.2 | 37 s |
| 11 | 823 ms | 21.4 | 11.5 | 82 s |
| 12 | 1,483 ms | 38.6 | 20.8 | 147 s |

- **Payload size.** The TRL 2 concept used 12 bytes. The slowest US915 rate (DR0, SF10) carries at most 11 bytes of application payload, so a 12-byte payload could not be sent from a US915 sensor at the edge of coverage. The payload is cut to 11 bytes, which fits [E2]; the airtimes are unchanged from TRL 2 because the symbol count does not change. At SF10 an uplink takes 371 ms, inside the 400 ms US915 dwell limit [E3].
- **Fair use.** Hourly reporting at SF12 would use 38.6 s a day, over TTN's 30 s, while SF11 hourly uses only 21.4 s. The routine interval therefore stays at 1 h up to SF11 and stretches to 2 h at SF12 only (DDR-002; D6 had stretched it at SF11 as well), which keeps SF12 at 20.8 s [E4]. Battery life is unchanged, because SF12 at 2 h remains the worst case in Section C.
- **Payload layout.** A candidate 11-byte layout, for the decoder shared with FieldNode (D5): 1 byte version and flags (alert, tip, lid, low battery, sensor used), 1 byte fill in 0.5 % steps, 2 bytes distance in millimeters, 1 byte temperature in degrees Celsius (signed), 1 byte lid-open count, 1 byte tip count, 1 byte battery voltage in 10 mV steps above 2.0 V, 2 bytes minutes since the last emptying and 1 byte spare. This is a sketch for review, not firmware.

## F. Link budget (R10)

*Table 5. Link margin at 1 km and range with a 10 dB fade margin [F1, F2].*

| Case | SF9 (143.0 dB budget) | SF12 (150.5 dB budget) |
| --- | --- | --- |
| HDPE container, antenna under the lid (10 dB) | 6.5 dB; 0.80 km | 14.0 dB; 1.30 km |
| Steel container, antenna inside (30 dB) | -13.5 dB; 0.22 km | -6.0 dB; 0.35 km |
| Steel container, external lid antenna (3 dB) | 13.5 dB; 1.26 km | 21.0 dB; 2.06 km |

- Urban path loss at 1 km is 126.5 dB; gateway sensitivity is -129.5 dBm at SF9 and -137.0 dBm at SF12 [F1].
- **Plastic containers** work to about 0.8 km at SF9 and 1.3 km at SF12 with a 10 dB fade margin. A pilot should place gateways within about 1 km of the containers, or accept SF12 and the 2 h interval.
- **Steel containers with the internal antenna do not meet R10:** even at SF12 the range is only about 0.35 km. An external lid antenna restores 1.3 to 2.1 km (open item O1 in DDR-001).

## G. Timing (R3, R9)

- **Fill alert.** In the worst case the surface crosses 80 % just after a reading: 15 min to the next reading, up to 147 s of EU868 off-time after a previous SF12 uplink, and 1.5 s of airtime give 17.5 min, inside R3's 20 min [G1].
- **Heat alert.** Read only with the 15 min ranging, a heat alert could take 17.5 min, which misses R9's 15 min. Reading the temperature every 5 min (0.0012 mAh a day [C1]) brings it to 7.5 min [G2]. This is a change from TRL 2.

## H. Temperature under the lid (R6, R9)

- **Hot lids.** In 900 W/m² sun at 40 °C ambient a dark lid reaches about 67 °C and a light lid about 55 °C [H1]. The unit is bolted to the lid underside and runs close to lid temperature, so on dark lids in hot climates it exceeded R6's former 60 °C limit. R6's upper limit is now 70 °C (DDR-002), which covers this with 3 K of margin. The module (to 85 °C) and cell tolerate it; the ultrasonic module's rating must be confirmed, so R6 stays at risk.
- **Cold.** The standard RAK3172 is rated to -20 °C, exactly R6's lower limit; the RAK3172-T (-40 to 85 °C) is named for cold sites (DDR-002).
- **False heat alarms.** The lid's time constant is 5.0 min and the unit's 8.9 min. When 800 W/m² sun breaks through cloud, a dark lid rises 24 K and the unit 15.4 K within 15 min [H2], just over the 15 K rate-of-rise trigger (D7). With the original rule the rate trigger could fire on a sunny afternoon with no fire.
- **Gated rate rule (DDR-002).** The 15 K rise now counts only when the unit is already above 50 °C; the 70 °C absolute alert is kept. Under cloud the unit sits at about 43 °C, below the gate, so the sun step does not trigger, and the steady dark lid (about 67 °C) stays below 70 °C [H3]. In the worst case above the gate, a unit already at 50 °C that then sees full sun rises 10.9 K in 15 min, below the 15 K trigger [H4]. R9 is met on paper; the thermal model is a screening estimate and must be checked by measurement. The alert remains a maintenance aid, not fire detection.

## I. Mass and size (R16)

- **Mass.** Enclosure 94 g (base and cover, 55 mm tall), bracket plate 63 g (2.0 mm 5052-class aluminium, no tabs), electronics board 13 g, printed collar and ToF holder with the window 5 g, and bought-in parts 174 g (now including the box fixings, 22 g, and the shorter bolts, 36 g) give 350 g, inside R16's 400 g [I1]. **R16 is met.** Version 0.2 gave 334 g with the 45 mm box and tabs; version 0.1 used a 1.5 mm stainless bracket (unit 435 g). A 2.0 mm stainless plate would make the unit 473 g [I2].
- **Size.** Below the lid the unit measures 150 x 80 x 71.5 mm (61.5 mm before the box grew 10 mm taller), inside the 160 x 90 x 100 mm limit [I3].
- **Corrosion.** The bolts stay stainless. Stainless bolts through wet aluminium can corrode the aluminium around the holes; an anodized plate or insulating washers should be considered (review suggestion, not applied).

## J. Shock and fixing (R7)

- A 20 g shock on the 0.35 kg unit gives 69 N. One washer pulling through the 5 mm HDPE lid needs about 5,655 N and one M6 bolt carries about 4,221 N [J1], so the fixing has a large margin on strength. Loosening under repeated shocks, and IK08 impact, need a test.
- The 50 g cell needs 10 N of retention at 20 g [J2]; the holder is specified with a strap rather than spring clips alone.
- **Box fixing (new in v0.3).** The box and everything in it, about 250 g, hang on the four M4 studs: 49 N at 20 g, or 12 N per stud. The base floor would need about 2,100 N per stud to pull through under a 9 mm sealing washer (ABS shear strength 30 MPa, assumed), and a press-in stud's push-out rating in 2 mm aluminium is taken as about 900 N (to confirm from the maker's data) [J3]. Strength is not the limit; loosening needs a test.

## K. Cost (R14)

- All eleven BOM lines are priced; the parts total is $59.00 against `budget_usd` of $60, within budget by $1.00 [K1]. Lines 10 (box fixings) and 11 (printed mounts and window) were added for construction (BNL-DDR-003). The $1.00 margin is an open decision in the design decisions register. No new budget was recommended, so costs are stated against the one figure.
- An external lid antenna for steel containers (about $8, open item O1) would take the total to $67.00, over budget [K2].

## L. Results against every requirement

*Table 6. Requirement status at TRL 3.*

| ID | Requirement | Target | Value (tag) | Status |
| --- | --- | --- | --- | --- |
| R1 | Range | 0.03 to 1.5 m below the face | 0 to 1.00 m needed; ultrasonic 0.25 to 4 m, ToF to 0.4 m (A2 to A4) | Met (datasheet ranges to confirm) |
| R2 | Accuracy on real waste | ±10 % of depth for 90 % of readings | Instrument 9.5 mm (ultrasonic), 20 mm (ToF) of 100 mm; surface unknown (B3) | At risk |
| R3 | Reporting and alert timing | Uplink at least every 2 h; alert within 20 min | 1 h (2 h at SF12); 17.5 min (G1) | Met |
| R4 | Battery life | 5 years at SF12; 10-year target | 16.3 years (C cell) (C4) | Met |
| R5 | Sealing | IP67 minimum; IP69K where pressure washed | Stock IP67 enclosure | Not met (IP69K) |
| R6 | Climate range | -20 to +70 °C inside the container (was +60 °C) | Dark lid about 67 °C (H1); standard module at its -20 °C limit, RAK3172-T for cold sites; transducer rating unconfirmed | At risk |
| R7 | Lifting, tipping and lid slams | No loosening; IK08 | 69 N against 4,221 N per bolt (J1); 12 N per stud (J3) | Not verifiable at TRL 3 |
| R8 | Emptying and lid events | Tip event with the next uplink | Accelerometer wake-on-motion | Met by design |
| R9 | Heat warning | Alert within 15 min above 70 °C, or on a 15 K rise in 15 min counted only above 50 °C | 7.5 min with 5 min reads (G2); sun step starts at about 43 °C, below the gate (H3); 10.9 K above the gate (H4) | Met on paper (to be measured) |
| R10 | Open LoRaWAN within radio rules | Class A; EU868, US915, IN865; duty cycle and 30 s/day | 20.8 s/day at SF12 (E4); 11 bytes fits US915 DR0 (E2); steel container 0.35 km (F2) | Not met (steel containers); met for HDPE |
| R11 | Privacy | No camera or microphone; limited payload | BOM and 11-byte layout (E) | Met by design |
| R12 | Installation | 10 min or less, four bolts, no cables | Four through-bolts on a 130 x 60 mm pattern | Not verifiable at TRL 3 |
| R13 | Tamper resistance | Inside the lid; tamper-resistant fasteners | Button-head tamper bolts from above | Met by design |
| R14 | Cost | $60 or less | $59.00 (K1) | Met |
| R15 | Open and interoperable | Documented payload; open decoder | Candidate layout in Section E; decoder shared with FieldNode (D5) | Met by design |
| R16 | Mass and size | 400 g or less; within 160 x 90 x 100 mm below the lid | 350 g (I1); 150 x 80 x 71.5 mm (I3) | Met |

Summary: met 10 (R1, R3, R4, R9, R14, R16 by calculation; R8, R11, R13, R15 by design); at risk 2 (R2, R6); not met 2 (R5, R10 in steel containers); not verifiable at TRL 3, 2 (R7, R12). Version 0.1 had met 8, at risk 3 and not met 3.

## Checks against the TRL 2 figures

| TRL 2 claim | TRL 3 value | Change made |
| --- | --- | --- |
| Daily use about 0.61 to 0.76 mAh; life about 23 to 18 years (C) | 0.664 to 0.856 mAh; 21.0 to 16.3 years | Precis and README updated |
| AA cell about 10 to 7 years | 8.5 to 6.2 years | Precis updated |
| 12-byte payload | 11 bytes, so it fits US915 DR0 | Precis, requirements and media updated |
| Uplink airtime about 5 s/day (SF9) and 18 s/day (SF12) | 5.4 and 20.8 s/day with two alerts | Precis updated |
| Mass about 250 g; R16 met | 435 g with stainless (v0.1); 334 g with the aluminium bracket (v0.2); 350 g constructable (v0.3); R16 met | Requirements, precis and README updated |
| 150 x 80 x 63 mm below the lid | 150 x 80 x 61.5 mm (v0.2); 71.5 mm with the 55 mm box (v0.3) | Requirements and precis updated |
| Temperature inside a dark lid up to about 60 °C | About 67 °C on a 40 °C day | Problem statement and requirements note updated |
| 80 % fill about 0.21 m below the lid | 0.20 m below the transducer face | Precis updated |
| Parts cost about $55 | $55.00 (v0.2); $59.00 with the parts added for construction (v0.3) | BOM, precis and README updated |
