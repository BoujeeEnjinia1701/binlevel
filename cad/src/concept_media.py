"""BinLevel concept massing model and media (TRL 2).

Run from the repo root:  python cad/src/concept_media.py
Proportions and main parts only; not for fabrication.

Coordinates in mm, Z up. The sensor unit is modeled at a local origin (bottom face of the
enclosure at z = 0) and then placed under the lid of an 1100 L four-wheel communal container
(EN 840 class, typical outer size about 1370 x 1070 x 1340 mm, an estimate), which stands on a
pavement slab beside a 1.75 m person. The container is shown in section in the hero so the
sensor under the lid can be seen. The container, waste, pavement and person are context only.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".kit"))
from build123d import Box, Cone, Cylinder, Sphere, Pos, Rot
from concept import Part, render_all, human_figure

# ---------------- sensor unit (local coordinates) ----------------
EW, ED, EH, WALL = 115.0, 65.0, 45.0, 2.5      # enclosure outer size and wall (stock IP67 box class)
PLATE_T = 3.0

# 1 Enclosure: hollow box with holes in the bottom for the transducer and the ToF window
enc = Pos(0, 0, EH / 2) * Box(EW, ED, EH) - Pos(0, 0, EH / 2) * Box(EW - 2 * WALL, ED - 2 * WALL, EH - 2 * WALL)
enc = enc - Pos(-35, 0, 0) * Cylinder(12.5, 10) - Pos(35, 0, 0) * Cylinder(5.5, 10)

# 2 Stainless bracket: plate against the lid underside, end tabs, four tamper-resistant bolts through the lid
plate = Pos(0, 0, EH + PLATE_T / 2) * Box(150, 80, PLATE_T)
tabs = Pos(-(EW / 2 + 1.5), 0, EH - 12) * Box(3, 60, 30) + Pos(EW / 2 + 1.5, 0, EH - 12) * Box(3, 60, 30)
bolts = None
for bx in (-65, 65):
    for by in (-30, 30):
        b = Pos(bx, by, EH + PLATE_T + 20) * Cylinder(3, 40) + Pos(bx, by, EH + PLATE_T + 40 + 2) * Cylinder(6.5, 4)
        bolts = b if bolts is None else bolts + b
bracket = plate + tabs + bolts

# 3 Sealed ultrasonic transducer, JSN-SR04T class, through the bottom face
transducer = Pos(-35, 0, -2.5) * Cylinder(12, 24)

# 4 Near-range time-of-flight sensor behind a small window
tof = Pos(35, 0, 7.8) * Box(13, 18, 3) + Pos(35, 0, 1.25) * Cylinder(5, 2.5)

# 6 Carrier PCB (accelerometer, temperature sensor, load switch, buffer capacitor)
pcb = Pos(0, 0, 10.2) * Box(105, 55, 1.6)

# 5 LoRaWAN module, STM32WL class, on the PCB
module = Pos(-38, 14, 11.0 + 1.25 + 0.2) * Box(16, 15, 2.5)

# 7 Li-SOCl2 C cell (26 mm x 50 mm) in a holder, lying along X
cell = Pos(8, -6, 13.0 + 13.1) * Rot(0, 90, 0) * Cylinder(13.1, 50)

# 8 Flexible antenna on the inner side wall (+Y)
antenna = Pos(0, ED / 2 - WALL - 0.4, 28) * Box(70, 0.6, 12)

# 9 Gasket at the cover split line, standing 0.5 mm proud for visibility
gasket = Pos(0, 0, 15) * (Box(EW + 1, ED + 1, 2) - Box(EW - 5, ED - 5, 3))

local = [
    ("Enclosure, IP67 ABS or PC", enc, "#F3F4F6", 1, (0, 0, 150)),
    ("Stainless bracket and tamper bolts", bracket, "#94A3B8", 2, (0, 0, 250)),
    ("Ultrasonic transducer, sealed", transducer, "#0F766E", 3, (0, 0, -60)),
    ("Near-range ToF sensor", tof, "#7C3AED", 4, (0, 0, -45)),
    ("LoRaWAN module, STM32WL class", module, "#2563EB", 5, (0, 0, 30)),
    ("Carrier PCB with accelerometer", pcb, "#16A34A", 6, (0, 0, 0)),
    ("Li-SOCl2 C cell and holder", cell, "#C2410C", 7, (0, 0, 60)),
    ("Flexible antenna", antenna, "#111827", 8, (0, -230, 150)),
    ("Gaskets and vent", gasket, "#D4A017", 9, (0, 0, 100)),
]

# ---------------- context: 1100 L container on a pavement ----------------
BW, BD = 1300.0, 1000.0            # body outer footprint
Z_BODY0, Z_RIM = 220.0, 1300.0     # body bottom and rim top
T = 8.0
body = Pos(0, 0, (Z_BODY0 + Z_RIM) / 2) * Box(BW, BD, Z_RIM - Z_BODY0)
body = body - Pos(0, 0, (Z_BODY0 + T + Z_RIM) / 2 + 1) * Box(BW - 2 * T, BD - 2 * T, Z_RIM - Z_BODY0 - T + 2)
rim = Pos(0, 0, Z_RIM - 15) * (Box(1370, 1070, 30) - Box(BW - 2 * T, BD - 2 * T, 40))
LID_Z0 = Z_RIM
lid = Pos(0, 0, LID_Z0 + 20) * Box(1380, 1080, 40)
wheels = None
for wx in (-520, 520):
    for wy in (-380, 380):
        w = (Pos(wx, wy, 100) * Rot(90, 0, 0) * Cylinder(100, 50)
             + Pos(wx, wy, 195) * Box(90, 90, 50))
        wheels = w if wheels is None else wheels + w
container = body + rim + lid + wheels

waste = Pos(0, 0, (Z_BODY0 + T + 760) / 2) * Box(BW - 2 * T - 2, BD - 2 * T - 2, 760 - Z_BODY0 - T)
for (sx, sy, r) in ((-380, 150, 190), (-50, 250, 170), (300, 120, 200), (420, 330, 150), (80, 60, 150)):
    waste = waste + Pos(sx, sy, 760) * Sphere(r)

pavement = Pos(550, 0, -60) * Box(2900, 1700, 120)
curb = Pos(550, 925, -60) * Box(2900, 150, 120)
road = Pos(550, 1250, -135) * Box(2900, 500, 30)
ground = pavement + curb + road

# Section: keep the +Y half (the camera looks from -Y), so the sensor under the lid shows
cutter = Pos(0, 3000, 0) * Box(6000, 6000, 6000)
container_cut = container & cutter
waste_cut = waste & cutter

# Sensor position: under the lid, front face just behind the section plane
SX, SY = -150.0, ED / 2 + 8
SZ = LID_Z0 - (EH + PLATE_T)
# The kit's cutaway cutter is centered on z = 0, so the sensor stays at the origin and the
# context scene is shifted by the inverse offset instead.
unplace = Pos(-SX, -SY, -SZ)

parts = [Part(n, s, c, b, e) for (n, s, c, b, e) in local]
person = human_figure(1750, x=1370 / 2 + 750, y=-450, z=0)
context = [
    Part("1100 L container, shown in section", unplace * container_cut, "#5F6B73"),
    Part("waste at about 55 % fill", unplace * waste_cut, "#8B8578"),
    Part("pavement", unplace * ground, "#D6D3CE"),
    Part("1.75 m person", unplace * person.shape, person.color),
]
# Illustrative sound cone from the transducer to the waste surface (about 10 degrees half-angle), hero only
BEAM_L = (SZ - 14.5) - 790.0
beam = Pos(-35, 0, -14.5 - BEAM_L / 2) * Cone(BEAM_L * 0.176, 11, BEAM_L)
context.append(Part("teal cone: ultrasonic beam (illustrative)", beam, "#5EEAD4"))

render_all(
    parts, project="BinLevel", title="Lid-mounted fill-level sensor concept", dwg_no="BNL-DWG-010",
    key_figures=["Ultrasonic 0.25 to 1.5 m, ToF 0.03 to 0.4 m (estimates)",
                 "Reading every 15 min; uplink every 1 to 2 h, or at once on 80 % fill",
                 "LoRaWAN Class A; fill, temperature, tilt, battery only",
                 "Li-SOCl2 C cell: about 10+ years (estimate)",
                 "About 250 g and about $55 in parts (indicative)"],
    scale_figure=False, context=context,
    flow={"title": "data flow (estimates; fill level only, no images or audio)", "unit": "",
          "stages": [("Waste surface", "0.03 to 1.5 m below lid"), ("Ranging", "echo and ToF, every 15 min"),
                     ("On-node fill %", "median of 5 pings"), ("LoRaWAN uplink", "1 to 2 h, or on 80 %"),
                     ("Gateway and server", "TwinKit or TTN"), ("Route plan", "serve full bins first")]},
)
