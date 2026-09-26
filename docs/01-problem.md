---
doc_id: BNL-PRB-001
title: BinLevel problem statement
project: BinLevel
doc_type: Problem statement
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
  change: Users, context, constraints, prior work with sources and open questions for TRL 2
- version: "0.3"
  date: '2026-09-25'
  author: Amish Chadha
  change: Target container adopted for TRL 3 (BNL-DDR-001, D1); lid temperature updated from BNL-CAL-001
- version: "0.4"
  date: '2026-09-25'
  author: Amish Chadha
  change: Recommendations accepted by Amish (DDR-002)
---

# BinLevel problem statement

Most municipal waste is still collected on a fixed timetable, so crews drive to bins that are half empty while others overflow between visits. The collection service has no cheap way to know how full each bin is. BinLevel is a low-cost, open, battery-powered fill-level sensor that sits under the lid of a communal or public bin and reports its fill level by LoRaWAN radio, so routes can be planned around bins that need emptying.

## Why it matters

Waste collection is one of the largest services a city runs, and it is growing. The World Bank estimates that 2.56 billion tonnes of municipal waste were produced in 2022 and that this will reach 3.86 billion tonnes by 2050 under business as usual ([World Bank, *What a Waste 3.0*](https://www.worldbank.org/en/publication/what-a-waste)). UNEP puts the global direct cost of waste management in 2020 at about USD 252 billion ([UNEP, *Global Waste Management Outlook 2024*](https://www.unep.org/resources/global-waste-management-outlook-2024)).

Where budgets are thin, collection coverage is low: the World Bank reports collection rates as low as 31 % in Sub-Saharan Africa and 67 % in South Asia, and public spending on waste in most low- and middle-income countries is well below 0.15 % of GDP, against about 0.3 to 0.5 % needed for basic collection ([World Bank](https://www.worldbank.org/en/publication/what-a-waste)). Every truck trip spent on a half-empty bin is a trip not spent on an overflowing one.

## Users and context

| User | Need | Context |
| --- | --- | --- |
| Municipal waste service or contractor (route planner) | Know which bins are near full before the crew leaves the depot | Daily or weekly routes; dispatch office with a laptop |
| Collection crew | Fewer wasted stops; warning of overfull or burning bins | Truck cab, phone or printed route |
| Housing estates, markets, campuses, parks | Keep communal bins from overflowing without paying for extra lifts | Shared 660 to 1,100 L containers or street litter bins |
| Community groups and small towns | A sensor they can build, repair and own, feeding their own map | Often no budget for commercial subscriptions |
| Residents and passers-by | Clean streets; no surveillance | The sensor must be visibly harmless: no camera, no microphone |

**Target containers (decided by Amish, 2026-09-25: go with recommendation; BNL-DDR-001, D1).** The first design case is the four-wheel communal container of the EN 840 class (660 to 1,100 L, plastic or steel, flat or domed lid), with public street litter bins (50 to 240 L) as a second case. The concept model uses an 1,100 L container of typical size (about 1,370 x 1,070 x 1,340 mm outer, an estimate from common catalog dimensions).

**Operating environment.** Outdoors under the lid, shaded but in a closed box that can reach high temperatures in sun (a dark lid reaches about 67 °C on a 40 °C day in full sun, and a light lid about 55 °C; estimates from BNL-CAL-001, section H) and below freezing in winter; condensation, food waste acids, dust and insects; repeated shocks when the bin is lifted and tipped into the truck; and periodic washing, sometimes with hot pressure water.

## Constraints

- Garage-buildable prototype, about $60 USD in parts per sensor (the `budget_usd` in `project.yaml`); the gateway is separate and shared.
- Off-the-shelf modules and a stock enclosure; no custom tooling at TRL 2 to 3.
- Battery only: no wiring to the bin and no solar panel, because lids are opened, slammed and tipped.
- Open radio: LoRaWAN, so it works with any network server, including the lab's TwinKit gateway and The Things Network (TTN).
- Privacy by design: counts and levels only. No images, audio or personal data leave the device, and the device has neither a camera nor a microphone.
- Radio rules: EU868 sub-bands are limited to a 0.1 % to 1 % duty cycle under ETSI EN 300 220, and TTN's fair use policy allows 30 s of uplink airtime per device per day ([TTN](https://www.thethingsnetwork.org/docs/lorawan/duty-cycle/)).

## Out of scope

- Route optimization software itself (BinLevel feeds an existing or open-source planner; the lab's TwinKit project is the proposed data layer).
- Compaction, bin redesign or collection vehicles.
- Waste identification or sorting (that is the WasteWise family).
- Certified fire detection. A temperature alert is a maintenance aid, not a safety system.

## Prior work

- **Commercial ultrasonic bin sensors.** Sensoneo sells single-beam and four-beam ultrasonic bin sensors with replaceable batteries, accelerometers for tilt and pickup detection, a temperature reading and LoRaWAN, Sigfox or NB-IoT radios ([Sensoneo product page](https://www.sensoneo.com/products/ultrasonic-bin-sensor/)). The vendor reports a Prague deployment of more than 3,000 sensors and claims about $156 of savings per bin per year ([Sensoneo](https://sensoneo.com/)); this is a vendor claim, not an independent result.
- **Sensing compactor bins.** Bigbelly sells solar compacting street bins with fullness reporting and claims that its data can reduce collections by 80 % ([Bigbelly](https://bigbelly.com/)); again a vendor claim, and a whole-bin replacement rather than a retrofit.
- **Gap.** Commercial sensors are closed and sold with a subscription. There is no widely used open, documented retrofit sensor that a small town, campus or community group can build for tens of dollars and connect to its own LoRaWAN network. BinLevel aims to fill that gap by using the same principle (ultrasonic ranging, tilt and temperature) with open hardware and a documented payload.

## Open questions

- [ ] Which container types and lid materials dominate in the first partner city? Steel containers block the radio if the antenna sits inside (BNL-CAL-001 gives about 0.35 km of range); the choice between an external antenna and excluding steel containers is open (BNL-DDR-001, O1).
- [x] Is an ultrasonic blind zone of about 0.25 m acceptable, or must the top 20 % of the bin be measured directly? Measured directly: the ToF sensor covers the top 0.4 m (BNL-DDR-001, D2; BNL-CAL-001, section A).
- [ ] How are containers washed (hot pressure water needs IP69K-class sealing)?
- [ ] Who owns the data and the gateway: the city, the contractor or a community group?
- [ ] What fill threshold triggers a collection for each waste stream (general, recycling, organics)?

## User research and co-design

This design is for communities the author is not part of, so requirements come from the people who will use it.

- [ ] Identify a local partner organization (Helpful Engineering network, NGO or university)
- [ ] Run co-design sessions with intended users; record who, where and what was learned
- [ ] Validate load, distance, terrain and cost assumptions in the field
- [ ] Revise requirements (REQ) from findings before freezing the design
