# Review note: BinLevel

## Session 2026-09-25: /populate to a strong TRL 2

### What was done

- `docs/01-problem.md` (BNL-PRB-001 v0.2): problem, why it matters (cited), users and context, target containers, operating environment, constraints (including privacy and LoRaWAN airtime rules), out of scope, prior work with sources, open questions; co-design checklist kept.
- `docs/03-requirements.md` (BNL-REQ-001 v0.2): 16 measurable requirements (R1 to R16) with targets, verification and concept status; assumptions.
- `docs/02-concept.md` (BNL-PRC-001 v0.2): how it works, numbered components, energy budget, radio airtime, measurement geometry, mass and cost, proposed design choices, safety, open questions.
- `cad/src/concept_media.py`: massing model of the lid-mounted sensor unit (nine BOM parts) with an 1,100 L communal container shown in section, waste, pavement, an illustrative ultrasonic beam and a 1.75 m person as context. The sensor is modeled at the origin and the context is shifted, because the kit's cutaway cutter is centered on z = 0.
- `media/`: `hero.png`, `concept-blueprint.png`, `.pdf` and `.svg`, `cutaway.png`, `exploded.png` with BOM callouts, `flow.png` (data flow, estimates), `model.glb` and `viewer.html`. Temporary `media/_views*` folders removed.
- `bom/bom.csv`: nine lines numbered to match the exploded view, with indicative USD prices; `bom/bom-notes.md` updated.
- `README.md`: hero image and links line; Concept rationale, Burning platform, Where it could be used (by industry, by country or region), What sparked the idea expanded with cited figures; Problem, Concept and Key components updated; Safety section added.
- `docs/pdf/`: branded PDFs of the three controlled documents.

### Key results (estimates, to be checked at TRL 3)

| Quantity | Estimate | Requirement |
| --- | --- | --- |
| Range coverage | Ultrasonic 0.25 to 1.5 m plus ToF 0.03 to 0.4 m | R1 met by design |
| Reading and report interval | Ranging every 15 min; uplink every 1 h (SF9) or 2 h (SF11 to SF12); alert at once on threshold | R3 met |
| Daily charge use | about 0.61 mAh (SF9) to 0.76 mAh (SF12) | |
| Battery life, C cell | about 23 years (SF9) to 18 years (SF12); seals limit life, so 10 years is the design target | R4 met on paper |
| Battery life, AA cell option | about 10 years (SF9) to 7 years (SF12) | R4 minimum met |
| Uplink airtime | about 5 s per day (SF9 hourly); about 18 s per day (SF12, 2-hourly); TTN limit 30 s | R10 met on airtime |
| Mass and size | about 250 g; 150 x 80 x 63 mm below the lid | R16 met |
| Parts cost | about $55 per sensor, gateway excluded | R14 met, within $60 budget |

Requirements not met or at risk:

- **R2 (accuracy on real waste) at risk:** uneven surfaces, bags and cardboard scatter the echo; no data yet.
- **R5 (IP69K for pressure washing) not met:** the stock enclosure is IP67.
- **R10 (radio) at risk in steel containers:** an internal antenna under a steel lid will be heavily shielded; an external antenna is needed.
- **R6 and R7 unverified:** transducer and ToF window condensation, and shock from tipping, are not yet assessed.

### Proposed, awaiting Amish

Update 2026-09-25: items 1 to 7 are "Decided by Amish, 2026-09-25: go with recommendation" (BNL-DDR-001, BNL-DDR-002). Items 8 and 9 had no recommendation and remain "Proposed, awaiting Amish".

1. **First target container.** Options: (a) 660 to 1,100 L four-wheel communal containers; (b) street litter bins of 50 to 240 L; (c) both from the start. Recommendation: (a), because each container serves many households and a lift is costly; (b) follows with the same electronics and a smaller bracket.
2. **Sensing method.** Options: (a) ultrasonic plus near-range ToF (about $5 more); (b) ultrasonic only, with any reading inside the blind zone reported as "full or blocked"; (c) ToF only (cheapest and smallest, but sensitive to a fouled window). Recommendation: (a), because the default 80 % threshold on an 1,100 L container lies inside the ultrasonic blind zone.
3. **Cell size.** Options: (a) C-size Li-SOCl2 (about $9, about 18 years worst case); (b) AA-size (about $4, about 7 years worst case). Recommendation: (a) for margin in cold climates and a 10-year service interval; revisit (b) for litter bins.
4. **Radio.** Options: (a) LoRaWAN on an STM32WL-class module shared with FieldNode; (b) NB-IoT (no gateway, but a SIM subscription per bin); (c) both variants. Recommendation: (a).
5. **Relationship to FieldNode and TwinKit.** Proposed: reuse FieldNode's radio module family, payload conventions and decoder, but not its enclosure, panel or cell; use TwinKit as the reference gateway and data layer. Both repos should be checked for consistency when their READMEs settle.
6. **Default fill threshold and reporting interval:** 80 % and 1 h (2 h at SF11 to SF12).
7. **Temperature alert:** 70 °C or a rise of 15 K in 15 min, as a maintenance aid only.
8. **Steel containers:** external lid antenna as an optional variant, or exclude steel containers from the first pilot.
9. **First partner and region for co-design and a pilot.**

No change to `project.yaml`: the pitch and problem remain accurate, and the parts cost is within `budget_usd` ($60).

### Safety concerns

- Primary lithium (Li-SOCl2) cell: must never be charged; fused; can vent toxic, corrosive gas or ignite if crushed, shorted or overheated; must be recycled, not binned.
- Sharp objects, needles and biological waste inside bins during installation and service; sharp edges on drilled lids.
- Bin fires: the unit adds a lithium cell to a fire-prone location, and its temperature alert must not be presented as fire detection.
- Work near collection trucks' lifting gear.

### Problems and notes

- The kit's `cutaway_parts` builds its cutter centered on z = 0, so parts far above the origin were not cut. The model keeps the sensor at the origin and shifts the context instead. Worth fixing in the kit (suggestion only).
- The hero note line is generated by the kit and reads "Grey: ... teal cone: ultrasonic beam (illustrative) for scale"; the beam is not a scale reference. Cosmetic.
- WebSearch was unavailable; every cited figure was checked by fetching the source page. No independent (non-vendor) study of collection savings from fill sensors was verified, so vendor savings figures appear only as labeled vendor claims in the problem statement, not in the burning platform.
- The legacy `cad/src/model.py` placeholder is untouched (TRL 3 work).

### Recommended next step

Review this note and the media, then decide items 1 to 3. If approved, run `/advance-trl3` to check the energy budget against named part datasheets, the link budget through plastic and steel lids, and the blind-zone geometry, and to produce the parametric model and drawing sheet.

## Session 2026-09-25: TRL 3

### What was done

- `docs/decisions/0001-trl2-review-decisions.md` (BNL-DDR-001 v0.1): ten items (D1 to D10) adopted as recommended for TRL 3 under Amish's 2026-09-25 instruction, open for his review; two items (O1, O2) remain "Proposed, awaiting Amish".
- `docs/04-calcs/01-sizing.md` (BNL-CAL-001 v0.1) and `docs/04-calcs/sizing.py`: measurement geometry, instrument accuracy, energy and battery life, supply voltage and pulses, airtime and payload, link budget, timing, lid temperature, mass, shock and cost, with a results table for R1 to R16. The script imports the model and reads the BOM and budget; every quoted number carries a tag from its output.
- `cad/src/model.py`: parametric build123d model of the nine BOM parts and a lid patch, with `PARAMS` and `derived()`. Exports `cad/step/` and `cad/stl/` for `binlevel-assembly`, `sensor-unit` and `bracket`.
- `cad/src/sheets.py` and `cad/drawings/BNL-DWG-001.svg`, `.pdf` and `.png`: general arrangement at Rev P1, 1:2, marked "CONCEPT, NOT FOR FABRICATION" and "PRELIMINARY, NOT FOR FABRICATION". The concept blueprint keeps BNL-DWG-010, so DWG-001 was free.
- `bom/bom.csv` and `bom/bom-notes.md`: all nine lines priced with a supplier or supplier type; total $55.00 against the $60 budget.
- `cad/src/concept_media.py` now builds from `model.py`; all media refreshed (hero, blueprint, cutaway, exploded, flow, GLB viewer), checked by eye, and temporary `media/_views*` folders removed.
- BNL-PRB-001, BNL-PRC-001 and BNL-REQ-001 moved to v0.3; `README.md` and `project.yaml` (trl: 3, trl_target: 3, evidence list) updated; PDFs rebuilt in `docs/pdf/`.

### Requirements at TRL 3 (BNL-CAL-001, Table 6)

| Status | Requirements | Key value |
| --- | --- | --- |
| **Not met** | R5 sealing | Stock IP67 box; IP69K not reached |
| **Not met** | R10 radio, steel containers | Internal antenna: about 0.35 km at SF12 with 10 dB fade margin; HDPE containers 0.8 km (SF9) to 1.3 km (SF12) |
| **Not met** | R16 mass | About 435 g against 400 g (1.5 mm stainless bracket 183 g); size met at 150 x 80 x 61 mm |
| At risk | R2 accuracy on waste | Instrument error 9.6 mm (ultrasonic), 20 mm (ToF) of 101 mm; waste surface unknown |
| At risk | R6 climate range | Dark lid about 67 °C on a 40 °C day; standard module rated only to -20 °C |
| At risk | R9 heat alert | Latency 7.5 min with 5 min reads, but sun through cloud raises the unit 15.4 K in 15 min |
| Not verifiable at TRL 3 | R7 shock, R12 install time | 85 N at 20 g against about 4,200 N per bolt |
| Met | R1, R3, R4, R14 (calculation); R8, R11, R13, R15 (design) | Alert 17.5 min; 16.3 years on a C cell at SF12; $55.00 |

Key numbers: worst-case draw 35.7 µA including self-discharge; 1.48 s per SF12 uplink and 20.8 s per day; transducer face 1.01 m above the floor and 80 % fill 0.20 m below it.

Changes to the TRL 2 concept that follow from the calculations: payload 12 to 11 bytes (US915 DR0 limit); nanopower regulator on the carrier (fresh cell 3.67 V against the module's 3.6 V maximum); temperature read every 5 min so the heat alert meets 15 min; cell strapped in its holder; bracket modeled at 1.5 mm, the thinnest in the TRL 2 range. TRL 2 life and mass estimates were optimistic (18 years and 250 g became 16.3 years and 435 g).

### Decisions recorded (BNL-DDR-001)

Decided by Amish, 2026-09-25: go with recommendation (previously adopted for TRL 3, open for his review): D1 660 to 1,100 L communal containers first; D2 ultrasonic plus ToF; D3 C-size Li-SOCl2 cell; D4 LoRaWAN on an STM32WL-class module; D5 reuse FieldNode's radio family, payload conventions and decoder, with TwinKit as reference gateway; D6 80 % threshold and 1 h interval (2 h at SF11 and SF12); D7 heat alert at 70 °C or 15 K in 15 min, maintenance aid only; D8 lid underside mounting; D9 stock IP67 enclosure; D10 no change to budget, pitch or problem (none was recommended).

### Still awaiting Amish

Update 2026-09-25: items 3 to 7 are "Decided by Amish, 2026-09-25: go with recommendation" (BNL-DDR-002). O1 and O2 remain "Proposed, awaiting Amish".

1. **O1, steel containers.** (a) External lid antenna variant (about $8, total $63.00, over budget) or (b) exclude steel containers from the first pilot. No recommendation was made.
2. **O2, first partner and region** for co-design and a pilot; also sets the radio plan. No preference stated.
3. **New, R16 mass.** Options: (a) 2 mm aluminium bracket, unit about 334 g; (b) relax R16 to 450 g and keep stainless; (c) perforated stainless bracket. Recommendation: (a). Decided by Amish, 2026-09-25: go with recommendation; applied.
4. **New, R6 upper limit.** Recommendation: raise to 70 °C to match dark lids in hot sun, and name the RAK3172-T for cold sites. Decided by Amish, 2026-09-25: go with recommendation; applied.
5. **New, R9 rate-of-rise rule.** Recommendation: count the 15 K rise only when the temperature is already above 50 °C, keeping the 70 °C absolute alert. Decided by Amish, 2026-09-25: go with recommendation; applied.
6. **New, payload of 11 bytes and 5 min temperature reads.** Applied to the design basis because R10 (US915) and R9 (15 min) require them. Decided by Amish, 2026-09-25: go with recommendation.
7. Suggestion only: SF11 hourly uses 21.4 s a day, inside TTN's 30 s, so the 2 h stretch could apply at SF12 only. Decided by Amish, 2026-09-25: go with recommendation; applied.

### Cross-repo consistency

- FieldNode (FND REVIEW, TRL 3): STM32WL-class module, LoRaWAN, TwinKit first; consistent with D4 and D5. FieldNode's 20-byte payload exceeds the 11-byte US915 DR0 limit found here; FieldNode's own rule stretches the interval from SF10. Noted, FieldNode not edited.
- TwinKit (TWK REVIEW): 8-channel LoRaWAN concentrator; consistent. Its budget question (O1 there) does not affect BinLevel, whose gateway is outside the BOM.

### Safety concerns

- Li-SOCl2 cell: never charge; fused; strapped so it cannot shake loose under the emptying shock; can vent toxic, corrosive gas if crushed, shorted or overheated; recycle, never bin.
- Hot lids: about 67 °C on dark lids in hot sun, still below the cell's rating but hot to touch during service.
- The heat alert may give false alarms (R9) and must never be presented as fire detection.
- Sharp objects and biological waste in bins; deburr drilled lids; keep clear of truck lifting gear.

### Gaps and notes

- No citations were flagged as unchecked in the TRL 2 note. WebFetch confirmed the RAK3172 supply range, sleep current and temperature ratings, the VL53L1X field of view and 4 m maximum, and the TTN note on the US915 400 ms dwell limit. The 11-byte US915 DR0 limit is from the LoRaWAN Regional Parameters and could not be re-fetched this session (the TTN page request was not approved in time). The JSN-SR04T range, beam angle and temperature rating are estimates, not checked against a datasheet.
- The kit's cutaway cuts at the mean Y of the parts; with the sensor at the origin and the container shifted, the section shows the cell, board, module, transducer and antenna, as at TRL 2. The hero note line is generated by the kit and ends "for scale" after the beam cone, which is not a scale reference (cosmetic, kit unchanged).
- Existing material beyond TRL 3: `build-log/README.md` (scaffold) is present, untouched and not extended. `electronics/` and `firmware/` are empty. The payload layout in BNL-CAL-001 is a sketch, not firmware.

### Recommended next step

TRL 4 is on hold by Amish's instruction; this repo stops at TRL 3. Amish's review is needed on D1 to D10, on O1 and O2, and on new items 3 to 6 above. For the record only, TRL 4 would need: a bench build of the sensor unit; a lab test report (TST, `environment: lab`) covering ranging on real waste in a container against dip readings, sleep and uplink current, cold-start at -20 °C, link loss inside HDPE and steel containers, lid temperature in sun, and shake and drop of the fixing; and build log entries. None of this has been started.

## Session 2026-09-25: recommendations accepted

Amish wrote on 2026-09-25: "i accept all your recommendations, go with them across all repos." Every item with a recommendation is now "Decided by Amish, 2026-09-25: go with recommendation", recorded in `docs/decisions/0002-recommendations-accepted.md` (BNL-DDR-002 v0.1). TRL stays at 3.

### Decisions applied and what changed

| Item | Decision | Before | After |
| --- | --- | --- | --- |
| D1 to D10 (BNL-DDR-001) | As recommended | Adopted for TRL 3, open for review | Decided; BNL-DDR-001 to v0.2; no design change |
| R16 mass (new item 3) | (a) 2 mm 5052-class aluminium bracket | 1.5 mm stainless, bracket 183 g, unit 435 g, R16 not met | 2.0 mm aluminium, bracket 83 g, unit 334 g, R16 met; envelope 61.0 to 61.5 mm below the lid; shock load 85 to 66 N |
| R6 upper limit (new item 4) | Raise to 70 °C; RAK3172-T for cold sites | -20 to +60 °C | -20 to +70 °C; dark lid 67 °C now inside the limit (3 K margin); still at risk on the transducer rating |
| R9 rate rule (new item 5) | Count the 15 K rise only above 50 °C; keep 70 °C | Sun step raises the unit 15.4 K, false alarm, at risk | Unit about 43 °C under cloud (below the gate); worst rise above the gate 10.9 K; met on paper |
| Payload and reads (new item 6) | Keep 11 bytes and 5 min reads | Applied, open for review | Decided |
| Interval stretch (suggestion 7) | 2 h at SF12 only | 2 h at SF11 and SF12 | 1 h to SF11 (21.4 s a day), 2 h at SF12 (20.8 s a day); worst-case life unchanged at 16.3 years |
| Budget | No change recommended | $60 | $60; parts $55.00 |

Files changed: `cad/src/model.py` (plate 2.0 mm, `plate_mat` aluminium) with STEP and STL re-exported; `bom/bom.csv` item 2 and `bom/bom-notes.md`; `cad/src/sheets.py` and BNL-DWG-001 at Rev P2; `cad/src/concept_media.py` key figures and all media regenerated; `docs/04-calcs/sizing.py` (R6 range, new H3 and H4, material-aware mass) and BNL-CAL-001 v0.2; BNL-REQ-001, BNL-PRC-001 and BNL-PRB-001 v0.4; README (Concept, Key components, decision links, new "What sparked the idea"); `project.yaml` evidence list (budget, pitch and problem unchanged).

### Requirement status (BNL-CAL-001 v0.2)

| Status | Requirements |
| --- | --- |
| **Not met** | R5 (stock IP67, not IP69K); R10 in steel containers (about 0.35 km at SF12 with the internal antenna) |
| At risk | R2 accuracy on real waste; R6 climate range (3 K margin at 70 °C; transducer rating unconfirmed) |
| Not verifiable at TRL 3 | R7 shock and loosening; R12 installation time |
| Met | R1, R3, R4, R9, R14, R16 by calculation; R8, R11, R13, R15 by design |

### Still awaiting Amish

1. **O1, steel containers:** external lid antenna ($63.00, over budget) or exclude steel containers from the first pilot. No recommendation.
2. **O2, first partner and region** for co-design and a pilot (sets EU868, US915 or IN865). No preference stated.

### Cross-repo actions

- **FieldNode:** its 20-byte payload exceeds the 11-byte US915 DR0 limit, and its interval stretch starts at SF10. Raise with FieldNode so the shared payload conventions and decoder (D5) fit US915 DR0. FieldNode not edited.
- Kit (suggestion only): the cutaway cutter centers on z = 0, and the hero note ends "for scale" after the beam cone. Not edited.

### Other changes this session

- README "What sparked the idea" rewritten: the starting point is now Philadelphia's 2009 BigBelly rollout and the City Controller's July 2010 report (collections averaged about 10 a week against a promised five; about $3,700 per unit), cited to the US EPA and NBC10 Philadelphia. The earlier text about a review of the lab's research areas was removed.
- All PDFs, drawings and media regenerated with the designmolecule.com footer.

### Notes and suggestions

- Stainless bolts through an aluminium plate outdoors invite galvanic corrosion around the holes; an anodized plate or insulating washers should be considered. Not applied.
- The gated rate rule means a fire starting from a cool bin is reported only at 70 °C or once above 50 °C; the alert remains a maintenance aid, never fire detection.

### Safety

Unchanged: the Li-SOCl2 cell must never be charged, shorted or crushed and must be fused, strapped and recycled; bins hold sharps and biological waste; hot dark lids (about 67 °C); keep clear of truck lifting gear; the heat alert is not fire detection.

### TRL 4

TRL 4 remains on hold by Amish's instruction. No build, test, PCB, firmware or purchasing work was started.

## Session 2026-09-26: product appearance model and photoreal renders

Amish chose this repo for the first batch of product renders on 2026-09-26.

### What was done

- `cad/src/product_model.py` (new): `product_parts()`, `TITLE` and `RENDER_VIEWS` (hero, exploded, detail) for the kit's photoreal renderer. It imports PARAMS and derived() from `cad/src/model.py` and keeps every main dimension and interface: enclosure envelope and split height, sensor apertures, bracket plate, tabs and bolt pattern, lid thickness, board, module, cell and antenna positions. It adds:
  - enclosure with rounded corners and filleted edges, a parting-line groove with the cover gasket showing, four cover screws in counterbores and matching bosses;
  - sealed ultrasonic probe with seal ring and inner lock ring; ToF window (clear) with seal ring, spacer, breakout board and sensor chip;
  - ePTFE pressure vent on the side wall; a device label with a QR code, print lines and a teal band (#0F766E);
  - aluminium bracket with filleted tab corners; tamper-resistant button-head bolts with pin-hex sockets, sealing washers and nyloc nuts;
  - carrier board with ICs, buffer capacitor and connectors; LoRaWAN module with shield can and u.FL; C cell with terminals, holder and a fabric retaining strap; flexible antenna with trace;
  - context: the upper part of a simple street bin with its hinged lid opened 45 degrees, so the sensor face shows.
- `README.md`: hero image now `media/render-hero.png`; "Exploded render" link added at the start of the links line. The render files are produced later by the orchestrator.
- Self-check previews (matplotlib, clear parts omitted) were reviewed outside the repo.

### Differences from model.py (Proposed, awaiting Amish)

1. **Render pose.** The unit and lid are turned together by 45 degrees about the lid hinge (a line parallel to Y) so the sensor face is visible; all sizes and relative positions are unchanged. The exploded and detail views show the unit at the same angle. Recommendation: accept for renders only.
2. **Context bin.** The renders show a compact street bin (250 x 290 mm lid, 85 mm of body below the rim) instead of the 1,100 L container that PARAMS describes for the calculations, so the sensor fills more of the frame. Recommendation: accept; the pitch covers communal and street bins, and the concept media keep the 1,100 L container.
3. **Sealing washers.** An 18 mm sealing washer (BOM 2) sits under each bolt head, which raises the heads 1.2 mm above the model.py position. Recommendation: add the washer to model.py at the next CAD update.
4. **Bolt shank.** In model.py the bolt shank runs to z = 58 mm, 2.7 mm above the top of the head (z = 55.3 mm). The appearance model ends the shank at the head. Recommendation: correct model.py.
5. **Nyloc nuts.** Placed directly under the bracket (z = 39 to 45 mm); in model.py the nut (z = 42 to 47 mm) overlaps the 2 mm plate. Recommendation: correct model.py.
6. **Board corners.** The carrier board corners are notched around the cover screw bosses that a stock IP67 box has; model.py shows a full 105 x 55 mm rectangle. Recommendation: keep as an open item for the board outline against the chosen enclosure; no layout work until TRL 4 is released.
7. **Label and cover screws.** The device label (QR code for the device identity) has no BOM line; the four cover screws are counted with the stock enclosure (BOM 1). Recommendation: add the label as a note under BOM 1 if Amish wants it in the design.

### Scope and TRL

This is an appearance model only: no tolerances, no fabrication detail, no PCB layout. `trl` stays 3 and TRL 4 remains on hold. `model.py`, the BOM and the controlled documents were not changed.

## Session 2026-09-27: kit 1.5.0 and image quality

- Kit 1.5.0 synced: STANDARDS v1.5 (sections 12 to 15: product renders, storefront images and image quality, public release, authorship and signing), `.kit/cards.py`, `.kit/image_qc.py`, `.kit/release_gate.py`, issue templates, and the `/render-product` and `/release` commands. `CLAUDE.md` now matches `.kit/CLAUDE.md`.
- Every `media/render-*.png` recaptioned from its original render with the new layout: the title, concept label and repository sit in a band above the render and the view note in a band below it, each line wrapped to the image width, so no text overlaps other text or the render or runs off the image. `media/card.png` and `media/social-preview.png` regenerated with the same rules.
- `python .kit/image_qc.py` and `python .kit/release_gate.py` pass. trl stays 3.
