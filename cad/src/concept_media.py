"""BinLevel concept media (TRL 3), generated from the parametric model.

Run from the repo root:  python cad/src/concept_media.py
Takes the BOM parts from cad/src/model.py (PARAMS) and adds an 1,100 L four-wheel
communal container (EN 840 class, typical size, an estimate), waste, pavement and a 1.75 m
person as context. Parts are colored and numbered to match bom/bom.csv. Figures on the sheet
come from docs/04-calcs/sizing.py (BNL-CAL-001). Not for fabrication.

Coordinates in mm, Z up. The sensor unit is at its local origin (bottom face of the enclosure
at z = 0) and the context scene is shifted by the inverse of the sensor position, because the
kit's cutaway cutter is centered near the origin.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / ".kit"), str(ROOT / "cad" / "src")]
from build123d import Box, Cone, Sphere, Pos  # noqa: E402
from concept import Part, render_all, human_figure  # noqa: E402
from model import PARAMS as P, build_parts, container, derived  # noqa: E402

D = derived(P)
EW, ED, EH = P["enc"]
COLORS = {1: "#F3F4F6", 2: "#94A3B8", 3: "#0F766E", 4: "#7C3AED", 5: "#2563EB", 6: "#16A34A",
          7: "#C2410C", 8: "#111827", 9: "#D4A017", 10: "#475569", 11: "#B45309"}
EXPLODE = {1: (0, 0, 0), 2: (0, 0, 260), 3: (0, 0, -90), 4: (0, 0, -70), 5: (0, 0, 90), 6: (0, 0, 60),
           7: (0, 0, 130), 8: (0, -200, 200), 9: (0, 0, -130), 10: (0, 0, 190), 11: (0, 0, -40)}
bom_parts, _ = build_parts(P)
local = [(n, s, COLORS[b], b, EXPLODE[b]) for b, n, s in bom_parts]

# ---------------- context: 1100 L container on a pavement ----------------
BW, BD = P["cont_body"]
Z_BODY0, Z_RIM, T = P["cont_floor_z"], P["cont_rim_z"], P["cont_wall"]
LID_Z0 = Z_RIM
container = container(P)

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
SX, SY = P["mount_xy"][0], P["mount_xy"][1] + ED / 2 + 8   # lid center, just behind the section plane
SZ = LID_Z0 - D["lid_under"]
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
# Illustrative sound cone from the transducer to the waste surface (15 degrees half-angle, as assumed in BNL-CAL-001), hero only
FACE = -P["us_protrude"]
BEAM_L = (SZ + FACE) - 790.0
beam = Pos(P["us_x"], 0, FACE - BEAM_L / 2) * Cone(BEAM_L * 0.268, P["us_d"] / 2 - 1, BEAM_L)
context.append(Part("teal cone: ultrasonic beam, illustrative", beam, "#5EEAD4"))

render_all(
    parts, project="BinLevel", title="Lid-mounted fill-level sensor concept", dwg_no="BNL-DWG-010",
    key_figures=["Ultrasonic from 0.25 m, ToF to 0.4 m; 80 % fill is 0.20 m below the face",
                 "Reading every 15 min; uplink every 1 h (2 h at SF12), or at once on 80 %",
                 "LoRaWAN Class A, 11-byte payload; fill, temperature, tilt, battery only",
                 "Li-SOCl2 C cell: 16 years worst case (SF12) on paper; 10-year design life",
                 "About 350 g and $59 in parts (BNL-CAL-001 v0.5)"],
    scale_figure=False, context=context,
    flow={"title": "data flow (estimates; fill level only, no images or audio)", "unit": "",
          "stages": [("Waste surface", "0 to 1.00 m below face"), ("Ranging", "echo + ToF, 15 min"),
                     ("On-node fill %", "median of 5 pings"), ("LoRaWAN uplink", "11 B, 1 h (2 h at SF12) or 80 %"),
                     ("Gateway and server", "TwinKit or TTN"), ("Route plan", "serve full bins first")]},
)
