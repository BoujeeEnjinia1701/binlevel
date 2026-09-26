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
