# BOM notes

- Item numbers match the callouts in `media/exploded.png` and the parts in `cad/src/model.py`.
- Prices are indicative single-unit or small-batch prices in USD for a prototype. Each line names a supplier or supplier type; prices were not re-quoted from a named supplier at TRL 3.
- Total parts cost per sensor is $55.00, within the $60 budget in `project.yaml` (BNL-CAL-001, section K). The optional external lid antenna for steel containers (about $8, open item O1 in BNL-DDR-001) would take it to $63.00, over budget, and is not included.
- TRL 3 changes: item 6 now includes a nanopower 3.3 V regulator (a fresh cell is 3.67 V, above the module's 3.6 V limit) and a 1,000 uF low-leakage buffer; item 7 has a retaining strap; item 5 is named as the RAK3172 (RAK3172-T for cold sites); item 2 is 1.5 mm stainless. None changed the indicative prices.
- Mass: the 1.5 mm stainless bracket (183 g) makes the unit about 435 g, above the 400 g limit of R16. A 2 mm aluminium bracket (about 83 g) is proposed, awaiting Amish.
- Not included: the LoRaWAN gateway (shared across many bins; see the lab's TwinKit project, or use a public network such as The Things Network), network server hosting, and installation labor.
- Item 7 is a primary (non-rechargeable) lithium cell. Do not charge it. Recycle spent cells through a battery collection point.
