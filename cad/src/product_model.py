"""BinLevel product appearance model (build123d), TRL 3, constructable design (BNL-DDR-003).

Finished-product look for photoreal renders of the design as it would be built: a light grey
IP67 box 115 x 65 x 55 mm with rounded corners, its deep base fixed under a flat aluminium
bracket plate (no end tabs) by four M4 press-in studs, bonded sealing washers and hex standoffs,
and its shallow cover facing down with the gasket at the parting line, four cover screws in
counterbores, the sealed ultrasonic probe in its printed collar, the ToF window disc in its
printed holder and the M8 ePTFE vent in the cover floor; a device label with a QR code and a
teal band on the side (a note under BOM line 1); tamper-resistant button-head M6 x 20 bolts with
sealing washers, plain washers and nyloc nuts. Inside: the 90 x 50 mm prototyping board on the
standoffs with the LoRaWAN module and sensor breakouts on header pins, the buffer capacitor, the
strapped C cell in its holder, the ultrasonic driver board hung underneath on nylon standoffs,
and the flexible antenna on the inner wall. Context is the upper part of a simple street bin with
its hinged lid opened 45 degrees, so the sensor face shows. APPEARANCE MODEL ONLY: no tolerances,
no fabrication detail. CONCEPT, NOT FOR FABRICATION.

Every part except the label, the context and a few cosmetic details is the solid from
build_components() in model.py, so every main dimension and interface is the model's own. The
appearance additions are: rounded vertical corners on the box and the plate (the plate's 3 mm
radius is on making sketch BNL-DWG-101), a face ring on the probe, the module drawn as breakout,
shield can and header pins, and the device label. The unit is built in the model.py frame
(enclosure bottom at z = 0, Z up, transducer on -X, ToF window on +X, lid underside at
z = enc_h + plate_t) and then turned with the lid about the lid hinge (a line parallel to Y,
HINGE below) by LID_OPEN degrees. All sizes and relative positions are unchanged. The bin is a
compact street-bin context (BIN_* below), not the 1,100 L container that PARAMS describes for the
calculations. See docs/REVIEW.md, sessions 2026-09-26 and 2026-10-02.

    from product_model import product_parts
    for p in product_parts(): print(p["name"], p["group"], p["material"])
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build123d import (Axis, Box, Cylinder, Plane, Pos, RectangleRounded, RegularPolygon, Rot,
                       extrude, fillet, loft)
from model import PARAMS, build_components, derived

TITLE = "BinLevel: fill-level sensor for communal and street bins"

RENDER_VIEWS = [
    {"name": "hero", "groups": ["shell", "internal", "context"], "explode": False, "el": 14, "az": -32,
     "note": "Product render from the front right, slightly above (about 14 deg elevation); the sensor "
             "under the lid of a street bin, lid opened to show the ultrasonic probe, ToF window and vent"},
    {"name": "exploded", "groups": ["shell", "internal", "accessory"], "explode": True, "el": 22, "az": -58,
     "note": "Exploded view from the front right and above (about 22 deg elevation), along the unit's "
             "axis as mounted on the opened lid: bolts, bracket plate with studs, nuts, enclosure base, "
             "sealing washers and standoffs, prototyping board with cell, module and breakouts, driver "
             "board, gasket, cover with probe collar, ToF holder and window, vent and ultrasonic probe"},
    {"name": "detail", "groups": ["shell", "internal"], "explode": False, "el": 10, "az": -24,
     "note": "Detail from the front right, slightly above (about 10 deg elevation): the sensor alone at the "
             "lid-open angle; ultrasonic probe at left, ToF window at right, vent in the cover, label on the side"},
]

_D0 = derived(PARAMS)

# Render layout: the lid and the unit turn together about the hinge line (parallel to Y)
LID_OPEN = 45.0                 # deg, +X edge of the lid lifts
LID_X = (-125.0, 125.0)         # lid plan extent, X (closed)
LID_Y = 290.0                   # lid plan extent, Y
HINGE = (-135.0, _D0["lid_under"] - 1.0)   # hinge line X and Z (closed-lid frame), just under the lid
BIN_TOP = (234.0, 274.0)        # bin body outer plan at the rim
BIN_BOT = (222.0, 262.0)        # bin body outer plan at the cut
BIN_H = 85.0                    # height of the bin section shown, below the rim
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
C_PERF = "#2F6B3A"
C_PCB_TOF = "#1E3A8A"
C_PCB_DRV = "#1D4ED8"
C_CHIP = "#111827"
C_CAN = "#C9CDD2"
C_CELL = "#56606B"
C_ANT = "#B7791F"
C_STRAP = "#23272D"
C_WHITE = "#F1EFEA"
C_PRINT = "#2E3238"
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


def _outer_corner_edges(s, hx, hy, tol=0.05):
    """Vertical edges at the outer corners (|x| = hx, |y| = hy) of a box-like solid."""
    out = []
    for e in s.edges().filter_by(Axis.Z):
        c = e.center()
        if abs(abs(c.X) - hx) < tol and abs(abs(c.Y) - hy) < tol:
            out.append(e)
    return out


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


def product_parts(P=PARAMS):
    D = derived(P)
    C = build_components(P)
    ew, ed, eh = P["enc"]
    w, zs = P["enc_wall"], P["split_z"]
    pt, lt = P["plate_t"], P["lid_t"]
    lid_under = D["lid_under"]
    ltop = D["bolt_top"]
    bpx, bpy = P["bolt_pitch"][0] / 2, P["bolt_pitch"][1] / 2
    bolt_xy = [(sx * bpx, sy * bpy) for sx in (-1, 1) for sy in (-1, 1)]
    out = []

    def add(name, shape, color, material, bom, group, explode, turn=True):
        s = _open(shape) if turn else shape
        e = _open_vec(explode) if turn else explode
        out.append({"name": name, "shape": s, "color": color, "material": material,
                    "bom": bom, "group": group, "explode": tuple(round(float(v), 3) for v in e)})

    def comp(key, name, color, material, group, explode, shape=None):
        add(name, shape if shape is not None else C[key].shape, color, material, C[key].bom, group, explode)

    # ---- enclosure (BOM 1): base fixed to the plate, cover facing down with the sensors
    R = 6.0
    base = _fillet_try(C["base"].shape, _outer_corner_edges(C["base"].shape, ew / 2, ed / 2), [R, 4.0, 3.0])
    cover = _fillet_try(C["cover"].shape, _outer_corner_edges(C["cover"].shape, ew / 2, ed / 2), [R, 4.0, 3.0])
    comp("base", "Enclosure base", C_ENC_BODY, "plastic", "shell", (0, 0, 62), base)
    comp("cover", "Enclosure cover", C_ENC, "plastic", "shell", (0, 0, -42), cover)
    comp("gasket", "Cover gasket", C_GASKET, "rubber", "shell", (0, 0, -18))
    comp("cover_screws", "Cover screws (4)", C_STEEL, "metal", "shell", (0, 0, -78))

    # ---- device label with a QR code and a teal band on the -Y face of the base (note under BOM 1)
    ly = -ed / 2
    lz = (zs + eh) / 2
    lab = Pos(-14.0, ly - 0.15, lz) * Box(58.0, 0.3, 17.0)
    lab = _fillet_try(lab, lab.edges().filter_by(Axis.Y), [1.5, 1.0])
    add("Device label", lab, C_LABEL, "paper", 1, "shell", (0, -10, 62))
    band = Pos(-14.0, ly - 0.35, lz + 6.5) * Box(58.0, 0.12, 4.0)
    add("Label band (teal)", band, C_ACCENT, "painted", 1, "shell", (0, -10, 62))
    qr = None
    bits = "1110111010101111010111011"
    for k, b in enumerate(bits):
        if b == "1":
            cx, cz = -37.0 + (k % 5) * 2.0, lz + 2.0 - (k // 5) * 2.0
            q = Pos(cx, ly - 0.35, cz) * Box(1.8, 0.12, 1.8)
            qr = q if qr is None else qr + q
    add("Label QR code", qr, C_BLACK, "paper", 1, "shell", (0, -10, 62))
    mark = Pos(-4.0, ly - 0.35, lz - 0.5) * Box(30.0, 0.12, 2.0) + Pos(-9.0, ly - 0.35, lz - 4.5) * Box(20.0, 0.12, 1.4)
    add("Label print", mark, C_DARK, "paper", 1, "shell", (0, -10, 62))

    # ---- bracket plate (BOM 2) with its press-in studs (BOM 10); bolts, washers and nuts (BOM 2)
    pw_, pd_ = P["plate"]
    plate = _fillet_try(C["plate"].shape, _outer_corner_edges(C["plate"].shape, pw_ / 2, pd_ / 2), [3.0, 2.0])
    comp("plate", "Aluminium bracket plate", C_ALU, "metal", "shell", (0, 0, 100), plate)
    comp("studs", "M4 press-in studs (4)", C_STEEL, "metal", "shell", (0, 0, 100))
    comp("seal_washers", "Bolt sealing washers (4)", C_STEEL, "metal", "shell", (0, 0, 128))
    heads = None
    for (x, y) in bolt_xy:
        hz0 = ltop + P["seal_washer"][1]
        h = Pos(x, y, hz0 + P["head_h"] / 2) * Cylinder(P["head_d"] / 2, P["head_h"])
        h = _fillet_try(h, _top_edges(h), [2.2, 1.6, 1.0])
        h -= Pos(x, y, hz0 + P["head_h"] - 0.9) * extrude(RegularPolygon(2.0, 6), amount=2.0)
        h += Pos(x, y, hz0 + P["head_h"] - 1.0) * Cylinder(0.55, 1.4)
        h += Pos(x, y, hz0 - P["bolt_len"] / 2) * Cylinder(P["bolt_d"] / 2, P["bolt_len"])
        heads = h if heads is None else heads + h
    add("Tamper bolts (4)", heads, C_STEEL, "metal", 2, "shell", (0, 0, 145))
    comp("nuts", "Plain washers and nyloc nuts (4)", C_STEEL, "metal", "shell", (0, 0, 82))

    # ---- box fixings inside the base (BOM 10)
    comp("bseals", "Bonded sealing washers (4)", C_GASKET, "rubber", "internal", (0, 0, 44))
    comp("standoffs", "M4 x 30 hex standoffs (4)", C_ALU, "metal", "internal", (0, 0, 30))
    comp("board_screws", "Board screws (4)", C_STEEL, "metal", "internal", (0, 0, -2))

    # ---- electronics board (BOM 6) and what sits on it
    comp("board", "Prototyping board", C_PERF, "plastic", "internal", (0, 0, 12))
    pt_ = D["pcb_top"]
    mx, my = P["module_xy"]
    bl, bw_, bt = P["module_bo"]
    mbo = Pos(mx, my, pt_ + 3 + bt / 2) * Box(bl, bw_, bt)
    add("LoRaWAN module breakout", mbo, C_PCB, "plastic", 5, "internal", (0, 0, 20))
    mw, md, mh = P["module"]
    mz = pt_ + 3 + bt
    add("LoRaWAN module board", Pos(mx, my, mz + 0.4) * Box(mw, md, 0.8), C_CHIP, "plastic", 5, "internal", (0, 0, 20))
    can = Pos(mx - 1.0, my, mz + 0.8 + (mh - 0.8) / 2) * Box(mw - 3.0, md - 2.0, mh - 0.8)
    add("LoRaWAN module shield", can, C_CAN, "metal", 5, "internal", (0, 0, 20))
    pins = None
    for s_ in (-1, 1):
        pn = Pos(mx + s_ * (bl / 2 - 1.5), my, pt_ + 1.5) * Box(2.5, bw_ - 2, 3.0)
        pins = pn if pins is None else pins + pn
    add("Module header pins", pins, C_BLACK, "plastic", 5, "internal", (0, 0, 20))
    comp("sensors_bo", "Accelerometer and temperature breakouts", C_PCB_TOF, "plastic", "internal", (0, 0, 20))
    comp("power_bo", "Regulator, load switch and fuse", C_PCB_TOF, "plastic", "internal", (0, 0, 20))
    cap = _fillet_try(C["cap"].shape, _top_edges(C["cap"].shape), [0.6, 0.3])
    comp("cap", "Buffer capacitor", C_CAN, "metal", "internal", (0, 0, 20), cap)
    comp("holder", "Cell holder", C_DARK, "plastic", "internal", (0, 0, 26))
    comp("cell", "Li-SOCl2 C cell", C_CELL, "painted", "internal", (0, 0, 34))
    comp("strap", "Cell retaining strap", C_STRAP, "fabric", "internal", (0, 0, 34))

    # ---- ultrasonic driver board (BOM 3) hung under the board on nylon standoffs (BOM 10)
    comp("driver", "Ultrasonic driver board", C_PCB_DRV, "plastic", "internal", (0, 0, -6))
    comp("driver_standoffs", "Driver nylon standoffs (4)", C_WHITE, "plastic", "internal", (0, 0, 3))

    # ---- flexible antenna (BOM 8) on the inner +Y wall of the base
    comp("antenna", "Flexible antenna", C_ANT, "plastic", "internal", (0, 34, 62))
    a = P["ant"]
    ay = ed / 2 - w - a[1] - 0.1
    trace = Pos(-8.0, ay, P["ant_z"]) * Box(44.0, 0.2, 1.2) + Pos(18.0, ay, P["ant_z"] + 3.0) * Box(20.0, 0.2, 1.2)
    add("Antenna trace", trace, "#8C5A17", "metal", 8, "internal", (0, 34, 62))

    # ---- in the cover: probe collar, ToF holder, window, ToF breakout, vent (BOM 3, 4, 9, 11)
    comp("collar", "Probe collar (printed ASA)", C_PRINT, "plastic", "internal", (0, 0, -24))
    comp("tof_holder", "ToF holder (printed ASA)", C_PRINT, "plastic", "internal", (0, 0, -24))
    comp("window", "ToF window disc", C_WINDOW, "clear", "shell", (0, 0, -32))
    comp("tof", "ToF breakout", C_PCB_TOF, "plastic", "internal", (0, 0, -14))
    comp("vent", "ePTFE pressure vent", C_DARK, "plastic", "shell", (0, 0, -64))

    # ---- ultrasonic probe (BOM 3), with a face ring for realism
    ux, ud = P["us_x"], P["us_d"]
    probe = C["probe"].shape
    probe = _fillet_try(probe, _bottom_edges(probe), [1.5, 1.0, 0.5])
    probe -= Pos(ux, 0, -P["us_protrude"]) * (Cylinder(ud / 2 - 2.2, 0.8) - Cylinder(ud / 2 - 3.2, 1.0))
    comp("probe", "Ultrasonic probe (sealed)", C_BLACK, "plastic", "shell", (0, 0, -100), probe)

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
