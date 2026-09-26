---
doc_id: BNL-PRC-001
title: BinLevel design precis
project: BinLevel
doc_type: Design precis
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
  change: Concept for TRL 2 with components, first-order numbers, safety and open questions
---

# BinLevel design precis

## Summary

BinLevel is a small sealed box bolted under the lid of a communal or public bin. Every 15 minutes it measures the distance down to the waste with a sealed ultrasonic transducer, backed by a time-of-flight (ToF) sensor for the top of the bin, and turns it into a fill percentage. It sends the level, temperature, tilt events and battery state by LoRaWAN every 1 to 2 hours, or at once when the bin passes a set level. A primary lithium cell runs it for about 10 years or more (estimate). Parts cost is about $55 (indicative), within the $60 budget. It carries no camera and no microphone.

![Figure 1. BinLevel under the lid of an 1,100 L communal container, shown in section, with a 1.75 m person for scale. Concept, not for fabrication.](../media/hero.png)

## How it works

1. **Measure.** The microcontroller wakes every 15 minutes, switches on the ultrasonic transducer and takes five pings, then reads the ToF sensor. It keeps the median ultrasonic distance and uses the ToF reading when the surface is closer than the ultrasonic blind zone (about 0.25 m, estimate).
2. **Interpret.** Distance is converted to fill percentage against the empty depth stored at installation. A fill above the threshold (default 80 %, proposed) or an abnormal temperature triggers an immediate uplink.
3. **Sense events.** A low-power accelerometer wakes the controller when the bin is tipped (emptying confirmed) or when the lid is opened (usage count), so the service gets proof of collection without a driver app.
4. **Report.** A LoRaWAN Class A uplink of about 12 bytes carries fill %, raw distance, temperature, event counters and battery voltage. Any LoRaWAN network server can receive it: the lab's TwinKit gateway, The Things Network or a city network.
5. **Plan.** The server passes levels to a route planner, which schedules the bins that are full or will be full before the next round (Figure 2).

![Figure 2. Data flow from waste surface to route plan. Values are estimates. Fill level only; no images or audio.](../media/flow.png)

## Main components

Numbers match the exploded view (Figure 3) and `bom/bom.csv`.

| No. | Component | Role |
| --- | --- | --- |
| 1 | Enclosure, IP67 ABS or PC, about 115 x 65 x 45 mm | Protects electronics; holes for transducer and ToF window |
| 2 | Stainless bracket and four tamper-resistant bolts | Fixes the unit under the lid; bolts pass through the lid |
| 3 | Sealed 40 kHz ultrasonic transducer (JSN-SR04T class) with driver | Main range sensor, about 0.25 to 1.5 m (estimate) |
| 4 | Near-range ToF sensor (VL53L1X class) behind a window | Top of bin and overfill, about 0.03 to 0.4 m (estimate) |
| 5 | LoRaWAN module, STM32WL class | Controller and radio in one module, as in FieldNode |
| 6 | Carrier PCB with accelerometer, temperature sensor, load switch and buffer capacitor | Joins the parts; powers sensors only while measuring |
| 7 | Li-SOCl2 primary cell, C size, 3.6 V, about 8.5 Ah nominal, with holder and fuse | Multi-year energy store |
| 8 | Flexible 868/915 MHz antenna | Radio antenna inside the enclosure (external option for steel bins) |
| 9 | Gaskets, vent membrane and transducer seal | Keeps water and condensation out |

![Figure 3. Exploded view with BOM numbers. Concept, not for fabrication.](../media/exploded.png)

![Figure 4. Cutaway of the sensor unit showing the cell, carrier PCB, module, transducer and ToF sensor. Concept, not for fabrication.](../media/cutaway.png)

## First-order numbers

All values are estimates for TRL 2, to be checked at TRL 3.

### Energy budget

Assumptions: sleep current 4 µA for the whole unit (module in its lowest retention mode plus accelerometer in wake-on-motion mode); each ranging cycle powers the sensors for 0.25 s at 30 mA; each uplink transmits at 14 dBm at about 45 mA, plus two receive windows of 0.1 s at 6 mA and 0.5 s of processing at 3 mA; cell self-discharge about 1 % per year; usable capacity 60 % of nominal to allow for pulse loads, cold and end-of-life voltage.

Table 1. Daily charge use (estimates).

| Item | SF9, hourly uplink | SF12, uplink every 2 h |
| --- | --- | --- |
| Sleep (4 µA x 24 h) | 0.10 mAh | 0.10 mAh |
| Ranging (96 cycles) | 0.20 mAh | 0.20 mAh |
| Uplinks | 0.08 mAh (24 x 0.21 s airtime) | 0.23 mAh (12 x 1.48 s airtime) |
| Self-discharge (C cell) | 0.23 mAh | 0.23 mAh |
| **Total** | **about 0.61 mAh per day** | **about 0.76 mAh per day** |
| Life on C cell (about 5.1 Ah usable) | about 23 years | about 18 years |
| Life on AA cell (about 1.6 Ah usable) | about 10 years | about 7 years |

The cell is not the limit on life; seals, the transducer membrane and the enclosure plastic under UV and heat are. The design target is therefore stated as 10 years (R4). A smaller AA cell would still meet the 5-year minimum and save about $5; see decision 3.

### Radio airtime

A 12-byte payload takes about 0.21 s at SF9 and about 1.48 s at SF12 (125 kHz, estimate from the LoRa airtime formula). Hourly uplinks use about 5 s per day at SF9, well inside TTN's 30 s daily fair use, but about 36 s per day at SF12, which would exceed it. The firmware therefore stretches the routine interval to 2 hours when the network assigns SF11 or SF12 (about 18 s per day), and keeps threshold alerts immediate.

### Measurement

- Container depth about 1.07 m; 80 % fill is about 0.21 m below the lid. That lies inside the ultrasonic blind zone (about 0.25 m, estimate), which is why the ToF sensor covers the top 0.4 m.
- The 40 kHz ultrasonic wavelength in air is about 8.6 mm, so the resolution is well below the ±10 % (about 0.1 m) accuracy target. Accuracy on real waste is limited by the surface, not by the sensor.
- An ultrasonic beam of about 10 to 15° half-angle (estimate) covers a patch about 0.4 to 0.6 m across at the container floor, which averages over uneven waste.

### Mass and cost

- Mass about 250 g (enclosure 80 g, bracket and bolts 70 g, cell about 50 g, transducer, PCB and module about 50 g; estimates).
- Parts cost about $55 at prototype quantities (indicative prices; see `bom/bom.csv`), inside the $60 budget. The gateway is shared across many bins and not included.

## Key design choices (proposed, awaiting Amish)

1. **Ultrasonic plus ToF, rather than ultrasonic alone or ToF alone.** Ultrasonic tolerates dust and dirt on the face and is the method used by commercial bin sensors ([Sensoneo](https://www.sensoneo.com/products/ultrasonic-bin-sensor/)). Low-cost sealed transducers cannot see the top 0.25 m, where the full threshold lies, so a ToF sensor covers that zone for about $5.
2. **Lid underside mounting.** Keeps the unit out of the waste, out of sight and away from vandals. The cost is that lid opening moves the sensor, which the accelerometer detects and skips.
3. **Primary Li-SOCl2 cell, not rechargeable or solar.** No charging electronics, no panel to break on a tipped bin, and very low self-discharge.
4. **LoRaWAN on an STM32WL-class module.** Shares the radio core and firmware approach proposed for FieldNode, so decoders and gateway set-up are common. NB-IoT would avoid gateways but needs a SIM subscription per bin.
5. **Stock enclosure at TRL 2 to 3.** Keeps the build garage-friendly; a potted or IP69K design is a later option.
6. **Relationship to FieldNode.** BinLevel does not use the FieldNode enclosure, panel or LiFePO4 cell: at about $126 FieldNode costs more than twice the BinLevel budget and would not fit under a lid. It proposes to reuse FieldNode's radio module family, payload conventions and decoder so both sit on the same TwinKit gateway.

Record each decision, once Amish makes it, as a file in [decisions/](decisions/).

## Safety

> **Safety:** The Li-SOCl2 cell is a primary lithium cell with high energy density. Never charge it, short it, crush it or heat it above its rated limit; a damaged cell can vent toxic, corrosive gas or catch fire. Fit a fuse or PTC in series, use a holder that prevents reverse insertion, and dispose of spent cells through a battery recycler, never in the bin itself.

> **Safety:** Bins can hold sharp objects, needles, broken glass and biological waste. Fit and service sensors only on emptied and cleaned containers, wear cut-resistant gloves and eye protection, and keep drill swarf out of the container. Drilling a lid leaves sharp edges; deburr them.

> **Safety:** Bins can catch fire from hot ash or discarded batteries. The temperature alert in R9 is a maintenance aid and must not be relied on as fire detection. The unit itself contains a lithium cell, which adds fuel to a bin fire.

> **Safety:** Keep clear of the lifting mechanism of collection trucks when installing or testing on containers in service.

## Open questions

- [ ] Can a sealed low-cost transducer survive years of condensation and food acids, or is a potted industrial transducer needed?
- [ ] Does the ToF window fog or foul too quickly to be useful? Is a wiper, hydrophobic coating or heater needed?
- [ ] What is the link loss through a steel lid, and where should an external antenna go?
- [ ] Is IP67 enough for the first partner's washing practice?
- [ ] Which route planner and data layer should the pilot use (TwinKit, a city system or an open-source vehicle routing tool)?
- [ ] Should the payload also carry a rolling fill-rate estimate so the planner can predict the full time?
