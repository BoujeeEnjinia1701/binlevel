"""BinLevel product appearance model (build123d), TRL 3.

Finished-product look for photoreal renders: a light grey IP67 enclosure with rounded corners,
a gasketed parting line between cover and body, four cover screws, the sealed ultrasonic probe
with its seal ring, the ToF window with its seal and spacer, an ePTFE vent, a device label with a
QR code and a teal band; the aluminium bracket with its end tabs, tamper-resistant button-head
bolts, sealing washers and nyloc nuts; inside, the carrier board with its small parts, the
LoRaWAN module, the ToF breakout, the strapped C cell in its holder and the flexible antenna.
Context is the upper part of a simple street bin with its hinged lid opened 45 degrees, so the
sensor face shows. APPEARANCE MODEL ONLY: no tolerances, no fabrication detail.
CONCEPT, NOT FOR FABRICATION.

Every main dimension and interface comes from PARAMS and derived() in model.py. The unit is
built in the model.py frame (enclosure bottom at z = 0, Z up, transducer on -X, ToF window on +X,
lid underside at z = enc_h + plate_t) and then turned with the lid about the lid hinge (a line
parallel to Y, HINGE below) by LID_OPEN degrees. All sizes and relative positions are unchanged.
The bin is a compact street-bin context (BIN_* below), not the 1,100 L container that PARAMS
describes for the calculations. See docs/REVIEW.md, session 2026-09-26.

    from product_model import product_parts
    for p in product_parts(): print(p["name"], p["group"], p["material"])
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build123d import (Axis, Box, Cylinder, Plane, Pos, RectangleRounded, RegularPolygon, Rot,
                       Vector, extrude, fillet, loft)
from model import PARAMS, derived

TITLE = "BinLevel: fill-level sensor for communal and street bins"

RENDER_VIEWS = [
    {"name": "hero", "groups": ["shell", "internal", "context"], "explode": False, "el": 14, "az": -32,
     "note": "Product render from the front right, slightly above (about 14 deg elevation); the sensor "
             "under the lid of a street bin, lid opened to show the ultrasonic probe and ToF window"},
    {"name": "exploded", "groups": ["shell", "internal", "accessory"], "explode": True, "el": 22, "az": -58,
     "note": "Exploded view from the front right and above (about 22 deg elevation), along the unit's "
             "axis as mounted on the opened lid: bolts and bracket, enclosure body, antenna, cell and "
             "holder, LoRaWAN module, carrier board, ToF sensor, gasket, cover, window and ultrasonic probe"},
    {"name": "detail", "groups": ["shell", "internal"], "explode": False, "el": 10, "az": -24,
     "note": "Detail from the front right, slightly above (about 10 deg elevation): the sensor alone at the "
             "lid-open angle; ultrasonic probe at left, ToF window at right, label and vent on the side"},
]

# Render layout: the lid and the unit turn together about the hinge line (parallel to Y)
LID_OPEN = 45.0                 # deg, +X edge of the lid lifts
LID_X = (-125.0, 125.0)         # lid plan extent, X (closed)
LID_Y = 290.0                   # lid plan extent, Y
HINGE = (-135.0, 46.0)          # hinge line X and Z (closed-lid frame)
BIN_TOP = (234.0, 274.0)        # bin body outer plan at the rim
BIN_BOT = (222.0, 262.0)        # bin body outer plan at the cut
BIN_H = 85.0                   # height of the bin section shown, below the rim
BIN_WALL = 4.0

# Colours (restrained product palette; kit accent)
C_ENC = "#E3E6E9"
C_ENC_BODY = "#D5D9DE"
C_GASKET = "#2B2F36"
C_BLACK = "#1C1F24"
C_DARK = "#3A3F47"
C_ACCENT = "#0F766E"
C_ALU = "#C3C8CE"
C_STEEL = "#AEB4BB"
C_LABEL = "#F4F4F1"
C_WINDOW = "#DCEBF5"
C_PCB = "#14532D"
C_PCB_TOF = "#1E3A8A"
C_CHIP = "#111827"
C_CAN = "#C9CDD2"
C_CELL = "#56606B"
C_ANT = "#B7791F"
C_STRAP = "#23272D"
C_WHITE = "#F1EFEA"
C_BIN = "#5B646C"
C_LID = "#4A5259"


def _fillet_try(shape, edges, radii):
    """Fillet `edges` with the first radius that gives a valid solid; else return the input."""
    edges = list(edges)
    if not edges:
        return shape
    for r in radii:
        try:
            out = fillet(edges, r)
            if out.is_valid and out.volume > 0:
                return out
        except Exception:
            pass
    return shape


def _prism(L, W, r, z0, h, x=0.0, y=0.0):
    """Rounded-rectangle prism in plan, from z0 up by h."""
    r = max(min(r, min(L, W) / 2 - 0.01), 0.01)
    return Pos(x, y, z0) * extrude(RectangleRounded(L, W, r), amount=h)


def _top_edges(s):
    return s.faces().sort_by(Axis.Z)[-1].edges()


def _bottom_edges(s):
    return s.faces().sort_by(Axis.Z)[0].edges()


def _ycyl(r, length, x, y, z):
    """Cylinder along Y centred at (x, y, z)."""
    return Pos(x, y, z) * Rot(90, 0, 0) * Cylinder(r, length)


def _open(shape):
    """Turn a closed-lid-frame shape with the lid about the hinge line."""
    hx, hz = HINGE
    return Pos(hx, 0, hz) * Rot(0, -LID_OPEN, 0) * Pos(-hx, 0, -hz) * shape


def _open_vec(v):
    """Turn an explode offset given in the unit frame (Z = away from the bin) with the lid."""
    a = math.radians(-LID_OPEN)
    x, y, z = v
    return (x * math.cos(a) + z * math.sin(a), y, -x * math.sin(a) + z * math.cos(a))


# ------------------------------------------------------------------ enclosure (BOM 1, 9)
def _enclosure(P):
    ew, ed, eh = P["enc"]
    w, zs = P["enc_wall"], P["split_z"]
    R = 6.0
    body = _prism(ew, ed, R, 0.0, eh)
    body = _fillet_try(body, _bottom_edges(body), [3.0, 2.0, 1.0])
    body = _fillet_try(body, _top_edges(body), [1.5, 1.0])
    body -= _prism(ew - 2 * w, ed - 2 * w, R - w, w, eh - 2 * w)
    # parting-line groove where the gasket shows
    gw, gd = 1.2, 0.8
    body -= _prism(ew + 2, ed + 2, R + 1, zs - gw / 2, gw) - _prism(ew - 2 * gd, ed - 2 * gd, R - gd, zs - gw, 2 * gw)
    cover = body & Pos(0, 0, zs / 2) * Box(ew + 10, ed + 10, zs)
    upper = body & Pos(0, 0, zs + (eh - zs) / 2 + 1) * Box(ew + 10, ed + 10, eh - zs + 2)
    # sensor apertures exactly as model.py
    cover -= Pos(P["us_x"], 0, 0) * Cylinder(P["us_hole_d"] / 2, 10)
    cover -= Pos(P["tof_x"], 0, 0) * Cylinder(P["win_d"] / 2, 10)
    # cover screw bosses (corner), counterbores on the outer face
    screws = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * 50.5, sy * 25.5
            cover += Pos(x, y, w + (zs - w) / 2) * Cylinder(3.5, zs - w)
            upper += Pos(x, y, zs + (eh - w - zs) / 2) * Cylinder(3.5, eh - w - zs)
            cover -= Pos(x, y, 0.75) * Cylinder(3.1, 1.6)
            cover -= Pos(x, y, zs / 2) * Cylinder(1.6, zs + 1)
            screws.append((x, y))
    # vent boss hole on the -Y face (upper body)
    upper -= _ycyl(4.0, 10, 38.0, -ed / 2, 30.0)
    return cover, upper, screws


def product_parts(P=PARAMS):
    D = derived(P)
    ew, ed, eh = P["enc"]
    w, zs = P["enc_wall"], P["split_z"]
    pt, lt = P["plate_t"], P["lid_t"]
    lid_under = D["lid_under"]
    out = []

    def add(name, shape, color, material, bom, group, explode, turn=True):
        s = _open(shape) if turn else shape
        e = _open_vec(explode) if turn else explode
        out.append({"name": name, "shape": s, "color": color, "material": material,
                    "bom": bom, "group": group, "explode": tuple(round(float(v), 3) for v in e)})

    # ---- enclosure
    cover, upper, screws = _enclosure(P)
    add("Enclosure body", upper, C_ENC_BODY, "plastic", 1, "shell", (0, 0, 46))
    add("Enclosure cover", cover, C_ENC, "plastic", 1, "shell", (0, 0, -37))
    gasket = _prism(ew - 1.0, ed - 1.0, 5.5, zs - 0.55, 1.1) - _prism(ew - 5, ed - 5, 3.5, zs - 1, 2.2)
    add("Cover gasket", gasket, C_GASKET, "rubber", 9, "shell", (0, 0, -16))
    for i, (x, y) in enumerate(screws):
        s = Pos(x, y, 0.75 + 0.35) * Cylinder(2.8, 1.5)
        s = _fillet_try(s, _bottom_edges(s), [0.5, 0.3])
        s -= Pos(x, y, 0.3) * Box(3.0, 0.7, 1.4)
        s -= Pos(x, y, 0.3) * Box(0.7, 3.0, 1.4)
        s += Pos(x, y, 1.85 + 6.0) * Cylinder(1.4, 12.0)
        add(f"Cover screw {i + 1}", s, C_STEEL, "metal", 1, "shell", (0, 0, -67))

    # ---- label with a QR code and teal band on the -Y face; ePTFE vent
    ly = -ed / 2
    lab = Pos(-14.0, ly - 0.15, 30.0) * Box(58.0, 0.3, 17.0)
    lab = _fillet_try(lab, lab.edges().filter_by(Axis.Y), [1.5, 1.0])
    add("Device label", lab, C_LABEL, "paper", None, "shell", (0, -10, 46))
    band = Pos(-14.0, ly - 0.35, 36.5) * Box(58.0, 0.12, 4.0)
    add("Label band (teal)", band, C_ACCENT, "painted", None, "shell", (0, -10, 46))
    qr = None
    bits = "1110111010101111010111011"
    for k, b in enumerate(bits):
        if b == "1":
            cx, cz = -37.0 + (k % 5) * 2.0, 32.0 - (k // 5) * 2.0
            q = Pos(cx, ly - 0.35, cz) * Box(1.8, 0.12, 1.8)
            qr = q if qr is None else qr + q
    add("Label QR code", qr, C_BLACK, "paper", None, "shell", (0, -10, 46))
    mark = Pos(-4.0, ly - 0.35, 29.5) * Box(30.0, 0.12, 2.0) + Pos(-9.0, ly - 0.35, 25.5) * Box(20.0, 0.12, 1.4)
    add("Label print", mark, C_DARK, "paper", None, "shell", (0, -10, 46))
    vent = _ycyl(6.0, 4.5, 38.0, ly - 2.25, 30.0)
    vent = _fillet_try(vent, vent.faces().sort_by(Axis.Y)[0].edges(), [1.2, 0.8])
    vent += Pos(38.0, ly - 0.6, 30.0) * Rot(90, 0, 0) * extrude(RegularPolygon(7.4, 6), amount=0.6, both=True)
    for dz in (-2.4, 0.0, 2.4):
        vent -= Pos(38.0, ly - 3.7, 30.0 + dz) * Box(8.0, 2.0, 0.9)
    vent += _ycyl(3.8, 8.0, 38.0, ly + 3.0, 30.0)
    add("ePTFE pressure vent", vent, C_DARK, "plastic", 9, "shell", (0, -18, 46))

    # ---- ultrasonic probe (BOM 3) with seal ring and inner lock ring
    ux, ud = P["us_x"], P["us_d"]
    probe = Pos(ux, 0, P["us_len"] / 2 - P["us_protrude"]) * Cylinder(ud / 2, P["us_len"])
    probe = _fillet_try(probe, _bottom_edges(probe), [1.5, 1.0, 0.5])
    probe -= Pos(ux, 0, -P["us_protrude"]) * (Cylinder(ud / 2 - 2.2, 0.8) - Cylinder(ud / 2 - 3.2, 1.0))
    add("Ultrasonic probe (sealed)", probe, C_BLACK, "plastic", 3, "shell", (0, 0, -83))
    seal = Pos(ux, 0, -0.6) * (Cylinder(15.5, 1.2) - Cylinder(ud / 2, 2.0))
    seal = _fillet_try(seal, _bottom_edges(seal), [0.5, 0.3])
    add("Probe seal ring", seal, C_GASKET, "rubber", 9, "shell", (0, 0, -56))
    lock = Pos(ux, 0, w + 1.5) * (Cylinder(15.0, 3.0) - Cylinder(ud / 2, 4.0))
    add("Probe lock ring", lock, C_DARK, "plastic", 3, "internal", (0, 0, -24))
    cable = Pos(ux + 6.0, 4.0, 9.4 - 0.5) * Box(10.0, 3.0, 1.0)
    add("Probe lead", cable, C_BLACK, "rubber", 3, "internal", (0, 0, 5))

    # ---- ToF sensor (BOM 4): window, seal, spacer, breakout and chip
    tx = P["tof_x"]
    win = Pos(tx, 0, 0.3 + 1.1) * Cylinder(P["win_d"] / 2 - 0.05, 2.2)
    add("ToF window", win, C_WINDOW, "clear", 4, "shell", (0, 0, -53))
    wseal = Pos(tx, 0, -0.4) * (Cylinder(8.0, 0.8) - Cylinder(P["win_d"] / 2 - 0.6, 1.2))
    wseal = _fillet_try(wseal, _bottom_edges(wseal), [0.3, 0.2])
    add("Window seal ring", wseal, C_GASKET, "rubber", 9, "shell", (0, 0, -59))
    spacer = Pos(tx, 0, (2.5 + 6.7) / 2) * (Cylinder(4.5, 6.7 - 2.5) - Cylinder(3.0, 6.0))
    add("ToF spacer", spacer, C_BLACK, "plastic", 4, "internal", (0, 0, -24))
    tb = P["tof_board"]
    tpcb = Pos(tx, 0, 7.8 + tb[2] / 2 - 0.5) * Box(tb[0], tb[1], 1.0)
    for sy in (-1, 1):
        tpcb -= Pos(tx, sy * 6.8, 8.8) * Cylinder(1.1, 2.0)
    add("ToF breakout board", tpcb, C_PCB_TOF, "plastic", 4, "internal", (0, 0, -16))
    chip = Pos(tx, 0, 8.3 - 0.8) * Box(4.9, 2.5, 1.6)
    add("ToF sensor chip", chip, C_CHIP, "plastic", 4, "internal", (0, 0, -16))

    # ---- carrier PCB (BOM 6) and parts
    pl, pw, pth = P["pcb"]
    pz0 = P["pcb_z"] - pth / 2
    pz1 = pz0 + pth
    pcb = _prism(pl, pw, 2.0, pz0, pth)
    for sx in (-1, 1):
        for sy in (-1, 1):
            pcb -= Pos(sx * 50.5, sy * 25.5, P["pcb_z"]) * Cylinder(4.2, pth + 2)
    add("Carrier PCB", pcb, C_PCB, "plastic", 6, "internal", (0, 0, 8))
    comps = Pos(-12.0, 16.0, pz1 + 0.5) * Box(2.0, 2.0, 1.0)          # accelerometer
    comps += Pos(40.0, -18.0, pz1 + 0.6) * Box(3.0, 3.0, 1.2)         # LDO
    comps += Pos(-22.0, -20.0, pz1 + 0.6) * Box(4.0, 2.0, 1.2)        # load switch
    comps += Pos(20.0, 18.0, pz1 + 0.5) * Box(2.0, 1.2, 1.0)          # temperature sensor
    add("Carrier PCB ICs", comps, C_CHIP, "plastic", 6, "internal", (0, 0, 8))
    cap = Pos(42.0, 16.0, pz1 + 5.0) * Cylinder(4.0, 10.0)
    cap = _fillet_try(cap, _top_edges(cap), [0.6, 0.3])
    add("Buffer capacitor", cap, C_CAN, "metal", 6, "internal", (0, 0, 8))
    conn = Pos(-47.0, -8.0, pz1 + 2.0) * Box(4.5, 10.0, 4.0) + Pos(47.0, -8.0, pz1 + 2.0) * Box(4.5, 8.0, 4.0)
    add("Board connectors", conn, C_WHITE, "plastic", 6, "internal", (0, 0, 8))

    # ---- LoRaWAN module (BOM 5): shield can on a small board, u.FL
    mx, my = P["module_xy"]
    mw, md, mh = P["module"]
    mz = pz1 + 0.2
    mod = Pos(mx, my, mz + 0.4) * Box(mw, md, 0.8)
    add("LoRaWAN module board", mod, C_CHIP, "plastic", 5, "internal", (0, 0, 13))
    can = Pos(mx - 1.0, my, mz + 0.8 + (mh - 0.8) / 2) * Box(mw - 3.0, md - 2.0, mh - 0.8)
    add("LoRaWAN module shield", can, C_CAN, "metal", 5, "internal", (0, 0, 13))
    ufl = Pos(mx + mw / 2 - 1.5, my + 4.0, mz + 1.4) * Cylinder(1.0, 1.2)
    add("u.FL connector", ufl, C_STEEL, "metal", 5, "internal", (0, 0, 13))

    # ---- C cell (BOM 7): wrap, caps, holder and strap
    cx, cy = P["cell_xy"]
    r = P["cell_d"] / 2
    cz = pz1 + 2 + r
    L = P["cell_len"]
    wrap = Pos(cx, cy, cz) * Rot(0, 90, 0) * Cylinder(r, L - 1.4)
    wrap = _fillet_try(wrap, wrap.edges(), [0.6, 0.3])
    add("Li-SOCl2 C cell", wrap, C_CELL, "painted", 7, "internal", (0, 0, 22))
    caps = Pos(cx + L / 2 - 0.35, cy, cz) * Rot(0, 90, 0) * Cylinder(r - 0.8, 0.7)
    caps += Pos(cx - L / 2 + 0.35, cy, cz) * Rot(0, 90, 0) * Cylinder(r - 0.8, 0.7)
    caps += Pos(cx + L / 2 + 0.6, cy, cz) * Rot(0, 90, 0) * Cylinder(3.0, 1.2)
    add("Cell terminals", caps, C_STEEL, "metal", 7, "internal", (0, 0, 22))
    hold = Pos(cx, cy, pz1 + 4.5) * Box(L + 6.0, P["cell_d"] - 4.0, 9.0)
    hold -= Pos(cx, cy, cz) * Rot(0, 90, 0) * Cylinder(r + 0.3, L + 20)
    hold += Pos(cx + L / 2 + 2.25, cy, pz1 + 9.0) * Box(1.5, 12.0, 18.0)
    hold += Pos(cx - L / 2 - 2.25, cy, pz1 + 9.0) * Box(1.5, 12.0, 18.0)
    hold = _fillet_try(hold, hold.edges().filter_by(Axis.Z), [0.8, 0.5])
    add("Cell holder", hold, C_DARK, "plastic", 7, "internal", (0, 0, 18))
    strap = Pos(cx, cy, cz) * Rot(0, 90, 0) * (Cylinder(r + 0.8, 8.0) - Cylinder(r + 0.05, 9.0))
    strap &= Pos(cx, cy, cz + 3) * Box(10, 40, 2 * r + 6)
    add("Cell retaining strap", strap, C_STRAP, "fabric", 7, "internal", (0, 0, 27))

    # ---- flexible antenna (BOM 8) on the inner +Y wall
    a = P["ant"]
    ay = ed / 2 - w - a[1] / 2 - 0.1
    ant = Pos(0, ay, P["ant_z"]) * Box(*a)
    add("Flexible antenna", ant, C_ANT, "plastic", 8, "internal", (0, 32, 32))
    trace = Pos(-8.0, ay - 0.4, P["ant_z"]) * Box(44.0, 0.2, 1.2)
    trace += Pos(18.0, ay - 0.4, P["ant_z"] + 3.0) * Box(20.0, 0.2, 1.2)
    add("Antenna trace", trace, "#8C5A17", "metal", 8, "internal", (0, 32, 32))

    # ---- aluminium bracket (BOM 2): plate with end tabs
    pw_, pd_ = P["plate"]
    tw, th = P["tab"]
    plate = _prism(pw_, pd_, 6.0, eh, pt)
    bpx, bpy = P["bolt_pitch"][0] / 2, P["bolt_pitch"][1] / 2
    bolt_xy = [(sx * bpx, sy * bpy) for sx in (-1, 1) for sy in (-1, 1)]
    for (x, y) in bolt_xy:
        plate -= Pos(x, y, eh + pt / 2) * Cylinder(P["bolt_d"] / 2 + 0.3, pt + 2)
    for sx in (-1, 1):
        tab = Pos(sx * (ew / 2 + pt / 2), 0, eh - th / 2) * Box(pt, tw, th)
        tab = _fillet_try(tab, tab.edges().filter_by(Axis.X).group_by(Axis.Z)[0], [5.0, 3.0])
        plate += tab
    add("Aluminium bracket", plate, C_ALU, "metal", 2, "shell", (0, 0, 86))

    # ---- tamper bolts, sealing washers, nyloc nuts (BOM 2)
    ltop = lid_under + lt
    for i, (x, y) in enumerate(bolt_xy):
        wz = 1.2
        wsh = Pos(x, y, ltop + wz / 2) * (Cylinder(9.0, wz) - Cylinder(P["bolt_d"] / 2 + 0.2, wz + 1))
        add(f"Sealing washer {i + 1}", wsh, C_STEEL, "metal", 2, "shell", (0, 0, 120))
        hz0 = ltop + wz
        head = Pos(x, y, hz0 + P["head_h"] / 2) * Cylinder(P["head_d"] / 2, P["head_h"])
        head = _fillet_try(head, _top_edges(head), [2.2, 1.6, 1.0])
        head -= Pos(x, y, hz0 + P["head_h"] - 0.9) * extrude(RegularPolygon(2.0, 6), amount=2.0)
        head += Pos(x, y, hz0 + P["head_h"] - 1.0) * Cylinder(0.55, 1.4)
        shank_bot = eh + pt + lt - P["bolt_len"] / 2 + 12 - (P["bolt_len"] - 12) / 2
        head += Pos(x, y, (shank_bot + hz0) / 2) * Cylinder(P["bolt_d"] / 2, hz0 - shank_bot)
        add(f"Tamper bolt {i + 1}", head, C_STEEL, "metal", 2, "shell", (0, 0, 136))
        nut = Pos(x, y, eh - 6.0) * extrude(RegularPolygon(5.77, 6), amount=6.0)
        nut -= Pos(x, y, eh - 3.0) * Cylinder(P["bolt_d"] / 2 - 0.2, 8.0)
        nut = _fillet_try(nut, _bottom_edges(nut), [0.5, 0.3])
        nut += Pos(x, y, eh - 7.0) * (Cylinder(4.6, 2.0) - Cylinder(P["bolt_d"] / 2 - 0.2, 3.0))
        add(f"Nyloc nut {i + 1}", nut, C_STEEL, "metal", 2, "shell", (0, 0, 70))

    # ------------------------------------------------------------ context (not in the BOM)
    lx0, lx1 = LID_X
    lcx, llen = (lx0 + lx1) / 2, lx1 - lx0
    lid = _prism(llen, LID_Y, 14.0, lid_under, lt, x=lcx)
    skirt = _prism(llen, LID_Y, 14.0, lid_under - 13.0, 13.0, x=lcx) - \
        _prism(llen - 8, LID_Y - 8, 10.0, lid_under - 14.0, 15.0, x=lcx)
    lid += skirt
    lid += _prism(llen - 24, LID_Y - 24, 8.0, ltop, 3.0, x=lcx) - _prism(llen - 36, LID_Y - 36, 4.0, ltop - 1, 5.0, x=lcx)
    for ry in (-80.0, 0.0, 80.0):
        lid += Pos(lcx + 6, ry, ltop + 1.25) * Box(llen - 60, 4.0, 2.5)
    lip = Pos(lx1 + 7.0, 0, lid_under - 3.0) * Box(18.0, 120.0, 10.0)
    lip = _fillet_try(lip, lip.edges().filter_by(Axis.Z), [4.0, 2.0])
    lid += lip
    hx, hz = HINGE
    for ky in (-75.0, 75.0):
        lid += _ycyl(7.0, 40.0, hx, ky, hz)
        lid += Pos((hx + lx0) / 2 + 2, ky, hz + 1.5) * Box(lx0 - hx + 6, 40.0, 9.0)
    for (x, y) in bolt_xy:
        lid -= Pos(x, y, lid_under + lt / 2) * Cylinder(P["bolt_d"] / 2 + 0.5, lt + 2)
    lid -= _ycyl(2.6, LID_Y, hx, 0, hz)
    lid = _open(lid)
    for ky in (-115.0, -35.0, 35.0, 115.0):      # clearance for the bin-side hinge knuckles
        lid -= Pos(hx + 8.0, ky, hz - 6.0) * Box(40.0, 42.0, 30.0)
    add("Bin lid (HDPE)", lid, C_LID, "plastic", None, "context", (0, 0, 0), turn=False)

    bx0, by0 = BIN_TOP
    bx1, by1 = BIN_BOT
    rim_z = lid_under
    z_cut = rim_z - BIN_H
    bcx = (lx0 + lx1) / 2
    outer = loft([Plane.XY.offset(z_cut) * Pos(bcx, 0) * RectangleRounded(bx1, by1, 16.0),
                  Plane.XY.offset(rim_z) * Pos(bcx, 0) * RectangleRounded(bx0, by0, 18.0)])
    t = BIN_WALL
    inner = loft([Plane.XY.offset(z_cut + t) * Pos(bcx, 0) * RectangleRounded(bx1 - 2 * t, by1 - 2 * t, 12.0),
                  Plane.XY.offset(rim_z + 1) * Pos(bcx, 0) * RectangleRounded(bx0 - 2 * t, by0 - 2 * t, 14.0)])
    body = outer - inner
    body += _prism(bx0 + 8, by0 + 8, 20.0, rim_z - 10.0, 10.0, x=bcx) - _prism(bx0 - 2 * t, by0 - 2 * t, 14.0, rim_z - 11, 12, x=bcx)
    for ky in (-115.0, -35.0, 35.0, 115.0):
        kn = _ycyl(7.0, 40.0, hx, ky, hz)
        kn += Pos((hx + bcx - bx0 / 2) / 2, ky, hz - 6.0) * Box(bcx - bx0 / 2 - hx + 4, 40.0, 12.0)
        body += kn
    body -= _ycyl(2.6, LID_Y + 20, hx, 0, hz)
    add("Street bin body (HDPE)", body, C_BIN, "plastic", None, "context", (0, 0, 0), turn=False)
    pin = _ycyl(2.5, LID_Y - 8, hx, 0, hz)
    add("Hinge pin", pin, C_STEEL, "metal", None, "context", (0, 0, 0), turn=False)
    return out


if __name__ == "__main__":
    for p in product_parts():
        s = p["shape"]
        print(f"{p['name']:28s} {p['group']:9s} {p['material']:8s} valid={s.is_valid} vol={s.volume / 1000:8.2f} cm3")
