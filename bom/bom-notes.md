# BOM notes

- Item numbers match the callouts in `media/exploded.png` and the parts in `cad/src/model.py`.
- Prices are indicative single-unit or small-batch prices in USD for a prototype. Each line names a supplier or supplier type; prices were not re-quoted from a named supplier at TRL 3.
- Total parts cost per sensor is $55.00, within the $60 budget in `project.yaml` (BNL-CAL-001, section K). The optional external lid antenna for steel containers (about $8, open item O1 in BNL-DDR-001) would take it to $63.00, over budget, and is not included.
- TRL 3 changes: item 6 now includes a nanopower 3.3 V regulator (a fresh cell is 3.67 V, above the module's 3.6 V limit) and a 1,000 uF low-leakage buffer; item 7 has a retaining strap; item 5 is named as the RAK3172 (RAK3172-T for cold sites); item 2 was 1.5 mm stainless at TRL 3 v0.1. None changed the indicative prices.
- Mass: item 2 is now a 2 mm 5052-class aluminium bracket (about 83 g), decided by Amish on 2026-09-25 (BNL-DDR-002). The unit is about 334 g, inside the 400 g limit of R16; the earlier 1.5 mm stainless bracket (183 g) made it about 435 g. The indicative price of item 2 is unchanged at $5.00 (aluminium plate costs about the same as thin stainless for one small part). The bolts stay stainless.
- Not included: the LoRaWAN gateway (shared across many bins; see the lab's TwinKit project, or use a public network such as The Things Network), network server hosting, and installation labor.
- Item 7 is a primary (non-rechargeable) lithium cell. Do not charge it. Recycle spent cells through a battery collection point.
