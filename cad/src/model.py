"""BinLevel parametric model (build123d), TRL 3, constructable design (BNL-DDR-003).

Run from the repo root:
    python cad/src/model.py            export STEP and STL into cad/step and cad/stl
    python cad/src/model.py --check    run the constructability checks and print the result

Exports:
    binlevel-assembly.step / .stl   sensor unit bolted under a patch of the container lid
    sensor-unit.step / .stl         the BOM parts only (no lid)
    bracket.step / .stl             aluminium bracket plate with its four press-in studs (BOM 2)

Axes and origin: the bottom face of the enclosure (the outside of its cover) is z = 0, Z is up,
X runs along the enclosure length (transducer on -X, ToF window on +X) and Y across it. The
enclosure hangs base up: its deep base is fixed to the bracket plate and its shallow cover, which
carries the two sensors, faces down into the bin. The lid underside is at z = enc_h + plate_t.
The container (an 1,100 L four-wheel communal container, EN 840 class, a typical-size estimate)
is described by PARAMS for the calculations and the concept media, but only a lid patch is part
of the exported assembly.

build_components() returns every component of the buildable design by name, so the build plan
pictures (cad/src/build_plan_media.py), the calculations (docs/04-calcs/sizing.py), the drawing
BNL-DWG-001 (cad/src/sheets.py) and the concept media (cad/src/concept_media.py) all use the same
solids. build_parts() groups them by BOM line. Not for fabrication.
"""
import math
import sys
from pathlib import Path

# Top-level parameters (mm unless noted). Edit these, not the geometry below.
PARAMS = {
    # 1 enclosure: stock IP67 ABS or PC box (outer), wall, cover depth (the split above the bottom).
    #   55 mm tall (was 45) so the ultrasonic driver board fits under the electronics board (DDR-003 P3)
    "enc": (115.0, 65.0, 55.0), "enc_wall": 2.5, "split_z": 15.0,
    #   corner screw towers of a stock box (cover screws go up into the base), centre and diameter
    "tower_xy": (51.0, 26.0), "tower_d": 9.0, "cover_screw_d": 3.5, "cover_screw_len": 28.0,
    # 2 bracket: aluminium (5052 class) plate against the lid underside, four M6 tamper bolts.
    #   2.0 mm aluminium replaces 1.5 mm stainless (BNL-DDR-002). End tabs removed (DDR-003 P1).
    "plate": (150.0, 80.0), "plate_t": 2.0, "plate_mat": "al",
    "bolt_pitch": (130.0, 60.0), "bolt_d": 6.0, "bolt_len": 20.0, "head_d": 10.5, "head_h": 3.3,
    "seal_washer": (18.0, 1.2), "plain_washer": (12.0, 1.6), "nut": (10.0, 6.0),     # (OD or AF, thickness)
    #   box fixing: four M4 x 12 flush-head press-in studs in the plate, through the base floor,
    #   M4 bonded sealing washers and M4 x 30 hex standoffs inside (DDR-003 P1)
    "stud_xy": (40.0, 18.0), "stud_d": 4.0, "stud_len": 12.0, "stud_hole_d": 4.2,
    "bseal": (9.0, 1.5), "standoff_af": 7.0, "standoff_len": 30.0,
    # "tab" is kept only for the concept appearance model (cad/src/product_model.py); the buildable
    # design has no tabs (DDR-003 P1)
    "tab": (60.0, 30.0),
    # 3 ultrasonic transducer (JSN-SR04T class): position on X, body diameter, length, protrusion below the box
    "us_x": -35.0, "us_d": 24.0, "us_len": 24.0, "us_protrude": 14.5, "us_hole_d": 25.0,
    #   printed probe collar bonded inside the cover (flange OD and thickness, tube OD, height)
    "collar": (36.0, 2.0, 30.0, 10.0),
    #   ultrasonic driver board (part of BOM 3) under the electronics board on 4 mm nylon standoffs
    "driver": (41.0, 28.0, 1.6), "driver_x": 4.5, "driver_parts_h": 5.0, "driver_gap": 4.0,
    # 4 ToF sensor (VL53L1X class) behind a window, held in a printed holder bonded inside the cover
    "tof_x": 37.0, "tof_board": (13.0, 18.0, 1.6), "win_d": 11.0, "window": (16.0, 1.5),
    "tof_holder": (20.0, 22.0, 6.0),
    # 5 LoRaWAN module (RAK3172 class) on its breakout board
    "module": (16.0, 15.0, 2.5), "module_bo": (20.0, 18.0, 1.6), "module_xy": (-23.0, 15.0),
    # 6 electronics board: for the prototype a perforated prototyping board standing in for the carrier PCB
    "pcb": (90.0, 50.0, 1.6), "pcb_z": 20.2,
    # 7 Li-SOCl2 C cell (ER26500 class) lying along X in a holder with a strap
    "cell_d": 26.2, "cell_len": 50.0, "cell_xy": (0.0, -8.0), "holder": (58.0, 28.0, 1.5),
    # 8 flexible antenna on the inner +Y wall of the base
    "ant": (70.0, 0.6, 12.0), "ant_z": 44.0,
    # 9 vent: M8 ePTFE pressure-equalizing vent in the cover floor, facing down
    "vent_xy": (0.0, -20.0), "vent_hole_d": 8.2,
    # lid interface (HDPE lid wall) and the container, for the calculations and media context
    "lid_t": 5.0, "lid_patch": (220.0, 140.0),
    "cont_outer": (1370.0, 1070.0), "cont_body": (1300.0, 1000.0), "cont_wall": 8.0,
    "cont_floor_z": 220.0, "cont_rim_z": 1300.0,
    # sensor position in the lid, measured from the container center line (x, y)
    "mount_xy": (0.0, 0.0),
}


def derived(p=PARAMS):
    """Dimensions the calc note and drawings quote, computed from PARAMS."""
    ew, ed, eh = p["enc"]
    pw, pd = p["plate"]
    w = p["enc_wall"]
    lid_under = eh + p["plate_t"]
    face = -p["us_protrude"]                                   # transducer face, local z
    floor_inner = p["cont_floor_z"] + p["cont_wall"]
    depth_lid = p["cont_rim_z"] - floor_inner                   # lid underside to inner floor
    face_to_floor = depth_lid - (lid_under - face)              # transducer face to inner floor
    inner = (p["cont_body"][0] - 2 * p["cont_wall"], p["cont_body"][1] - 2 * p["cont_wall"])
    mx, my = p["mount_xy"]
    wall_clear = min(inner[0] / 2 - abs(mx + p["us_x"]), inner[1] / 2 - abs(my))
    base_floor = eh - w                                         # inside face of the base floor
    standoff_top = base_floor - p["bseal"][1]
    standoff_bot = standoff_top - p["standoff_len"]
    pcb_top = standoff_bot
    pcb_bot = pcb_top - p["pcb"][2]
    return {
        "lid_under": lid_under,
        "below_lid": lid_under - face,                          # overall height below the lid
        "footprint": (max(pw, ew), max(pd, ed)),
        "face_to_floor": face_to_floor,
        "depth_lid": depth_lid,
        "inner": inner,
        "inner_volume_l": inner[0] * inner[1] * depth_lid / 1e6,
        "wall_clear": wall_clear,
        "base_floor": base_floor,
        "cover_floor": w,                                       # inside face of the cover floor
        "standoff_top": standoff_top, "standoff_bot": standoff_bot,
        "pcb_top": pcb_top, "pcb_bot": pcb_bot,
        "cell_z": pcb_top + p["holder"][2] + p["cell_d"] / 2,
        "driver_top": pcb_bot - p["driver_gap"],
        "bolt_top": lid_under + p["lid_t"],                     # top of the lid, under the sealing washer
    }


class Comp:
    """One component: name, solid, BOM line and how it is made."""

    def __init__(self, name, shape, bom, how):
        self.name, self.shape, self.bom, self.how = name, shape, bom, how


def _fuse(shapes):
    out = None
    for s in shapes:
        out = s if out is None else out + s
    return out


def _corners(x, y):
    return [(sx * x, sy * y) for sx in (-1, 1) for sy in (-1, 1)]


def _hexprism(af, h, x, y, z0):
    from build123d import Pos, RegularPolygon, extrude
    return Pos(x, y, z0) * extrude(RegularPolygon(af / math.sqrt(3), 6), amount=h)


def build_components(p=PARAMS):
    """Every component of the buildable design, by name, in assembly coordinates."""
    from build123d import Box, Cylinder, Pos, Rot
    D = derived(p)
    ew, ed, eh = p["enc"]
    w, zs = p["enc_wall"], p["split_z"]
    pw, pd = p["plate"]
    pt = p["plate_t"]
    tx, ty = p["tower_xy"]
    tr = p["tower_d"] / 2
    sx, sy = p["stud_xy"]
    C = {}

    def add(key, name, shape, bom, how):
        C[key] = Comp(name, shape, bom, how)

    # ---------------- enclosure: base (fixed to the bracket) and cover (carries the sensors)
    shell = lambda z0, z1: Pos(0, 0, (z0 + z1) / 2) * Box(ew, ed, z1 - z0)      # noqa: E731
    inside = lambda z0, z1: Pos(0, 0, (z0 + z1) / 2) * Box(ew - 2 * w, ed - 2 * w, z1 - z0)  # noqa: E731
    gz = (zs, zs + 1.0)                                       # gasket groove in the base rim
    groove = Pos(0, 0, zs + 0.5) * (Box(ew - 2 * w + 3.0, ed - 2 * w + 3.0, 1.0) - Box(ew - 2 * w + 1.0, ed - 2 * w + 1.0, 2.0))
    base = shell(zs, eh) - inside(zs - 1, eh - w) - groove
    cover = shell(0, zs) - inside(w, zs + 1)
    for x, y in _corners(tx, ty):
        base += Pos(x, y, (zs + eh - w) / 2) * Cylinder(tr, eh - w - zs)
        base -= Pos(x, y, zs + 9) * Cylinder(p["cover_screw_d"] / 2, 18.01)
        cover += Pos(x, y, (w + zs) / 2) * Cylinder(tr, zs - w)
        cover -= Pos(x, y, zs / 2) * Cylinder(p["cover_screw_d"] / 2 + 0.2, zs + 2)
        cover -= Pos(x, y, 1.5) * Cylinder(3.5, 3.0)            # counterbore for the screw head
    for x, y in _corners(sx, sy):
        base -= Pos(x, y, eh - w / 2) * Cylinder(2.25, w + 2)   # 4.5 mm holes for the studs
    cover -= Pos(p["us_x"], 0, w / 2) * Cylinder(p["us_hole_d"] / 2, w + 2)
    cover -= Pos(p["tof_x"], 0, w / 2) * Cylinder(p["win_d"] / 2, w + 2)
    vx, vy = p["vent_xy"]
    cover -= Pos(vx, vy, w / 2) * Cylinder(p["vent_hole_d"] / 2, w + 2)
    add("base", "Enclosure base (drilled for the studs)", base, 1, "bought, drilled")
    add("cover", "Enclosure cover (drilled for the sensors and vent)", cover, 1, "bought, drilled")
    gasket = Pos(0, 0, zs + 0.5) * (Box(ew - 2 * w + 2.8, ed - 2 * w + 2.8, 1.0) - Box(ew - 2 * w + 1.2, ed - 2 * w + 1.2, 1.0))
    add("gasket", "Cover gasket (in the base rim groove)", gasket, 1, "bought with the box")
    cs = []
    for x, y in _corners(tx, ty):
        cs.append(Pos(x, y, 0.5 + 1.25) * Cylinder(3.25, 2.5))
        cs.append(Pos(x, y, 3.0 + p["cover_screw_len"] / 2) * Cylinder(p["cover_screw_d"] / 2, p["cover_screw_len"]))
    add("cover_screws", "Cover screws (4, with the box)", _fuse(cs), 1, "bought with the box")

    # ---------------- bracket plate, studs and the M6 tamper bolts
    plate = Pos(0, 0, eh + pt / 2) * Box(pw, pd, pt)
    bpx, bpy = p["bolt_pitch"][0] / 2, p["bolt_pitch"][1] / 2
    for x, y in _corners(bpx, bpy):
        plate -= Pos(x, y, eh + pt / 2) * Cylinder(3.3, pt + 2)
    for x, y in _corners(sx, sy):
        plate -= Pos(x, y, eh + pt / 2) * Cylinder(p["stud_hole_d"] / 2, pt + 2)
    add("plate", "Bracket plate", plate, 2, "made: cut, drilled, studs pressed in")
    studs = _fuse([Pos(x, y, eh + pt - p["stud_len"] / 2) * Cylinder(p["stud_d"] / 2, p["stud_len"])
                   + Pos(x, y, eh + pt / 2) * Cylinder(p["stud_hole_d"] / 2, pt) for x, y in _corners(sx, sy)])
    add("studs", "M4 flush-head press-in studs (4)", studs, 10, "bought, pressed into the plate")
    lt = p["lid_t"]
    top = D["bolt_top"]
    swd, swt = p["seal_washer"]
    bolts, swash, nuts = [], [], []
    for x, y in _corners(bpx, bpy):
        swash.append(Pos(x, y, top + swt / 2) * (Cylinder(swd / 2, swt) - Cylinder(p["bolt_d"] / 2, swt + 1)))
        hz0 = top + swt
        b = Pos(x, y, hz0 + p["head_h"] / 2) * Cylinder(p["head_d"] / 2, p["head_h"])
        b += Pos(x, y, hz0 - p["bolt_len"] / 2) * Cylinder(p["bolt_d"] / 2, p["bolt_len"])
        bolts.append(b)
        pwd, pwt = p["plain_washer"]
        z = eh - pwt
        n = Pos(x, y, z + pwt / 2) * (Cylinder(pwd / 2, pwt) - Cylinder(p["bolt_d"] / 2, pwt + 1))
        naf, nt = p["nut"]
        n += _hexprism(naf, nt, x, y, z - nt) - Pos(x, y, z - nt / 2) * Cylinder(p["bolt_d"] / 2, nt + 1)
        nuts.append(n)
    add("bolts", "M6 x 20 tamper-resistant button-head bolts (4)", _fuse(bolts), 2, "bought")
    add("seal_washers", "18 mm sealing washers under the bolt heads (4)", _fuse(swash), 2, "bought")
    add("nuts", "M6 washers and nyloc nuts (4)", _fuse(nuts), 2, "bought")

    # ---------------- inside the base: sealing washers, standoffs, electronics board
    bf = D["base_floor"]
    bsd, bst = p["bseal"]
    bs, so = [], []
    for x, y in _corners(sx, sy):
        bs.append(Pos(x, y, bf - bst / 2) * (Cylinder(bsd / 2, bst) - Cylinder(p["stud_d"] / 2, bst + 1)))
        s = _hexprism(p["standoff_af"], p["standoff_len"], x, y, D["standoff_bot"])
        s -= Pos(x, y, D["standoff_top"] - 6) * Cylinder(p["stud_d"] / 2, 12.01)   # female thread for the stud
        s -= Pos(x, y, D["standoff_bot"] + 4) * Cylinder(p["stud_d"] / 2, 8.01)    # female thread for the board screw
        so.append(s)
    add("bseals", "M4 bonded sealing washers (4)", _fuse(bs), 10, "bought")
    add("standoffs", "M4 x 30 hex standoffs (4)", _fuse(so), 10, "bought")
    pl, pwid, pth = p["pcb"]
    pz = D["pcb_bot"] + pth / 2
    board = Pos(0, 0, pz) * Box(pl, pwid, pth)
    for x, y in _corners(sx, sy):
        board -= Pos(x, y, pz) * Cylinder(2.15, pth + 2)
    cx, cy = p["cell_xy"]
    hl, hw, hh = p["holder"]
    r = p["cell_d"] / 2
    for ssx in (-1, 1):                                       # two slots for the cell strap
        board -= Pos(cx, cy + ssx * (r + 0.5), pz) * Box(12.0, 3.0, pth + 2)
    for x, y in _corners(17.5, 11.0):                          # driver standoff holes
        board -= Pos(p["driver_x"] + x, y, pz) * Cylinder(1.6, pth + 2)
    add("board", "Electronics board (prototyping board)", board, 6, "made: cut and drilled perforated board")
    bscr = []
    for x, y in _corners(sx, sy):
        bscr.append(Pos(x, y, D["pcb_bot"] - 1.4) * Cylinder(3.5, 2.8))
        bscr.append(Pos(x, y, D["pcb_bot"] + 4) * Cylinder(p["stud_d"] / 2, 8.0))
    add("board_screws", "M4 x 8 pan-head screws (4)", _fuse(bscr), 10, "bought")

    # cell, holder and strap on the board's top side
    pt_ = D["pcb_top"]
    holder = Pos(cx, cy, pt_ + hh / 2) * Box(hl, hw, hh)
    for s_ in (-1, 1):
        holder += Pos(cx + s_ * (hl / 2 - 2), cy, pt_ + hh + 11) * Box(4.0, 20.0, 22.0)
    cz = D["cell_z"]
    cell = Pos(cx, cy, cz) * Rot(0, 90, 0) * Cylinder(r, p["cell_len"])
    strap = Pos(cx, cy, cz) * Rot(0, 90, 0) * (Cylinder(r + 1.0, 10) - Cylinder(r, 11))
    strap -= Pos(cx, cy, cz - 50) * Box(20, 60, 100.0)          # keep the upper half of the loop
    zb = D["pcb_bot"] - 1.0
    strap += _fuse([Pos(cx, cy + s_ * (r + 0.5), (zb + cz) / 2) * Box(10, 1.0, cz - zb) for s_ in (-1, 1)])
    strap += Pos(cx, cy, zb + 0.5) * Box(10, 2 * r + 2.0, 1.0)  # under the board
    for s_ in (-1, 1):                                          # strap slots in the holder base
        holder -= Pos(cx, cy + s_ * (r + 0.5), pt_ + hh / 2) * Box(12.0, 3.0, hh + 1)
    add("holder", "Cell holder", holder, 7, "bought")
    add("cell", "Li-SOCl2 C cell", cell, 7, "bought")
    add("strap", "Cell strap", strap, 7, "bought")

    # breakouts on the top side
    mx, my = p["module_xy"]
    bl, bw_, bt = p["module_bo"]
    mod = Pos(mx, my, pt_ + 3 + bt / 2) * Box(bl, bw_, bt)                   # on 3 mm header pins
    mod += Pos(mx, my, pt_ + 3 + bt + p["module"][2] / 2) * Box(*p["module"])
    pins = _fuse([Pos(mx + s_ * (bl / 2 - 1.5), my, pt_ + 1.5) * Box(2.5, bw_ - 2, 3.0) for s_ in (-1, 1)])
    add("module", "LoRaWAN module on its breakout", mod + pins, 5, "bought")
    sens = Pos(-1.0, 15.0, pt_ + 3 + 0.8) * Box(14.0, 14.0, 1.6) + _fuse([Pos(-1.0 + s_ * 5.5, 15.0, pt_ + 1.5) * Box(2.5, 12, 3.0) for s_ in (-1, 1)])
    power = Pos(13.0, 15.0, pt_ + 3 + 0.8) * Box(10.0, 14.0, 1.6) + _fuse([Pos(13.0 + s_ * 3.5, 15.0, pt_ + 1.5) * Box(2.5, 12, 3.0) for s_ in (-1, 1)])
    cap = Pos(26.0, 15.0, pt_ + 6.5) * Cylinder(5.0, 13.0)
    add("sensors_bo", "Accelerometer and temperature breakouts", sens, 6, "bought")
    add("power_bo", "Regulator, load switch and fuse", power, 6, "bought")
    add("cap", "1,000 uF buffer capacitor", cap, 6, "bought")
    # ultrasonic driver board hung under the electronics board
    dl, dw, dt = p["driver"]
    dtop = D["driver_top"]
    dx = p["driver_x"]
    drv = Pos(dx, 0, dtop - dt / 2) * Box(dl, dw, dt)
    drv += Pos(dx, 0, dtop - dt - p["driver_parts_h"] / 2) * Box(dl - 8, dw - 8, p["driver_parts_h"])
    for x, y in _corners(17.5, 11.0):
        drv -= Pos(dx + x, y, dtop - dt / 2) * Cylinder(1.6, dt + 2)
    add("driver", "Ultrasonic driver board", drv, 3, "bought with the transducer")
    dso = []
    for x, y in _corners(17.5, 11.0):
        dso.append(Pos(dx + x, y, (dtop + D["pcb_bot"]) / 2) * Cylinder(2.5, p["driver_gap"]))
    add("driver_standoffs", "M3 x 4 nylon standoffs (4)", _fuse(dso), 10, "bought")
    a = p["ant"]
    antenna = Pos(0, ed / 2 - w - a[1] / 2, p["ant_z"]) * Box(*a)
    add("antenna", "Flexible antenna (inner wall)", antenna, 8, "bought")

    # ---------------- in the cover: transducer, collar, ToF holder, window, ToF board, vent
    ux = p["us_x"]
    probe = Pos(ux, 0, p["us_len"] / 2 - p["us_protrude"]) * Cylinder(p["us_d"] / 2, p["us_len"])
    add("probe", "Ultrasonic transducer probe", probe, 3, "bought")
    fod, ft, tod, ch = p["collar"]
    collar = Pos(ux, 0, w + ft / 2) * Cylinder(fod / 2, ft) + Pos(ux, 0, w + ch / 2) * Cylinder(tod / 2, ch)
    collar -= Pos(ux, 0, w + ch / 2) * Cylinder(p["us_d"] / 2, ch + 1)
    collar -= Pos(ux, -(p["us_d"] / 2 + tod / 2) / 2, w + 6) * Rot(90, 0, 0) * Cylinder(1.25, (tod - p["us_d"]) / 2 + 1)  # M3 grub screw hole
    add("collar", "Probe collar (printed)", collar, 11, "made: 3D printed ASA")
    tx_ = p["tof_x"]
    hx, hy, hz = p["tof_holder"]
    wd, wt = p["window"]
    tb = p["tof_board"]
    th = Pos(tx_, 0, w + hz / 2) * Box(hx, hy, hz)
    th -= Pos(tx_, 0, w + hz / 2) * Cylinder(p["win_d"] / 2, hz + 1)              # light path
    th -= Pos(tx_, 0, w + wt / 2) * Cylinder(wd / 2 + 0.25, wt)                  # window recess
    th -= Pos(tx_, 0, w + hz - 1.0) * Box(tb[0] + 0.5, tb[1] + 0.5, 2.01)        # board pocket, 2 mm deep
    add("tof_holder", "ToF holder (printed)", th, 11, "made: 3D printed ASA")
    window = Pos(tx_, 0, w + wt / 2) * Cylinder(wd / 2, wt)
    add("window", "Window disc", window, 11, "made: cut from PMMA or bought glass")
    tz0 = w + hz - 2.0
    tof = Pos(tx_, 0, tz0 + tb[2] / 2) * Box(*tb) + Pos(tx_, 0, tz0 - 0.75) * Box(4.9, 2.5, 1.5)
    add("tof", "ToF breakout (VL53L1X class)", tof, 4, "bought")
    vent = Pos(vx, vy, -2.5) * Cylinder(6.0, 5.0) + Pos(vx, vy, w / 2) * Cylinder(p["vent_hole_d"] / 2 - 0.1, w)
    vent += _hexprism(13.0, 3.0, vx, vy, w) - Pos(vx, vy, w + 1.5) * Cylinder(p["vent_hole_d"] / 2 - 0.1, 3.01)
    vent += Pos(vx, vy, w + 1.5) * Cylinder(p["vent_hole_d"] / 2 - 0.1, 3.0)
    add("vent", "M8 vent with its nut", vent, 9, "bought")
    return C


def lid_patch(p=PARAMS):
    """A patch of the HDPE lid with the four bolt holes: the site interface, not a BOM part."""
    from build123d import Box, Cylinder, Pos
    ew, ed, eh = p["enc"]
    lw, ld = p["lid_patch"]
    z = eh + p["plate_t"] + p["lid_t"] / 2
    lid = Pos(0, 0, z) * Box(lw, ld, p["lid_t"])
    for bx in (-p["bolt_pitch"][0] / 2, p["bolt_pitch"][0] / 2):
        for by in (-p["bolt_pitch"][1] / 2, p["bolt_pitch"][1] / 2):
            lid = lid - Pos(bx, by, z) * Cylinder(p["bolt_d"] / 2 + 0.5, p["lid_t"] + 2)
    return lid


BOM_NAMES = {1: "Enclosure, IP67 ABS or PC", 2: "Aluminium bracket plate and tamper bolts", 3: "Ultrasonic transducer and driver",
             4: "Near-range ToF sensor", 5: "LoRaWAN module on breakout", 6: "Electronics board and small parts",
             7: "Li-SOCl2 C cell, holder and strap", 8: "Flexible antenna", 9: "Gaskets and vent",
             10: "Box fixings: studs, standoffs, seals, screws", 11: "Printed sensor mounts and window"}


def build_parts(p=PARAMS):
    """Return ([(bom_no, name, shape)] grouped by BOM line, bracket plate with studs)."""
    C = build_components(p)
    groups = {}
    for c in C.values():
        groups.setdefault(c.bom, []).append(c.shape)
    parts = [(b, BOM_NAMES[b], _fuse(groups[b])) for b in sorted(groups)]
    return parts, C["plate"].shape + C["studs"].shape


def container(p=PARAMS):
    """Context: the 1,100 L container body, rim, lid and wheels, container floor center at the origin
    of the container frame (x = y = 0, ground z = 0). Used by the concept media only."""
    from build123d import Box, Cylinder, Pos, Rot
    bw, bd = p["cont_body"]
    t = p["cont_wall"]
    z0, zr = p["cont_floor_z"], p["cont_rim_z"]
    body = Pos(0, 0, (z0 + zr) / 2) * Box(bw, bd, zr - z0)
    body = body - Pos(0, 0, (z0 + t + zr) / 2 + 1) * Box(bw - 2 * t, bd - 2 * t, zr - z0 - t + 2)
    ow, od = p["cont_outer"]
    rim = Pos(0, 0, zr - 15) * (Box(ow, od, 30) - Box(bw - 2 * t, bd - 2 * t, 40))
    lid = Pos(0, 0, zr + 20) * Box(ow + 10, od + 10, 40)
    wheels = None
    for wx in (-520, 520):
        for wy in (-380, 380):
            wh = Pos(wx, wy, 100) * Rot(90, 0, 0) * Cylinder(100, 50) + Pos(wx, wy, 195) * Box(90, 90, 50)
            wheels = wh if wheels is None else wheels + wh
    return body + rim + lid + wheels


def assembly(p=PARAMS, with_lid=True):
    from build123d import Compound
    C = build_components(p)
    shapes = [c.shape for c in C.values()] + ([lid_patch(p)] if with_lid else [])
    return Compound(children=shapes)


# ---------------------------------------------------------------- constructability checks
# Pairs that must touch (a face of one on a face of the other), with what holds them.
CONTACTS = [
    ("plate", "base", "base top face flat on the plate underside"),
    ("plate", "studs", "studs pressed into the plate, heads flush"),
    ("studs", "standoffs", "standoffs threaded onto the studs"),
    ("bseals", "base", "sealing washers on the inside of the base floor"),
    ("bseals", "standoffs", "standoffs clamp the sealing washers"),
    ("standoffs", "board", "board on the standoff ends"),
    ("board_screws", "board", "screw heads under the board"),
    ("board_screws", "standoffs", "screws into the standoffs"),
    ("holder", "board", "cell holder on the board"),
    ("cell", "holder", "cell in its holder"),
    ("strap", "cell", "strap over the cell"),
    ("module", "board", "module breakout on its header pins"),
    ("sensors_bo", "board", "sensor breakouts on header pins"),
    ("power_bo", "board", "power parts on header pins"),
    ("cap", "board", "capacitor on the board"),
    ("driver_standoffs", "board", "driver standoffs under the board"),
    ("driver_standoffs", "driver", "driver board on its standoffs"),
    ("antenna", "base", "antenna stuck to the inner wall"),
    ("gasket", "base", "gasket in the rim groove"),
    ("gasket", "cover", "cover rim on the gasket"),
    ("cover", "base", "cover rim against the base rim"),
    ("cover_screws", "cover", "cover screws through the cover towers"),
    ("collar", "cover", "collar bonded to the cover floor"),
    ("collar", "probe", "collar grips the probe"),
    ("tof_holder", "cover", "ToF holder bonded to the cover floor"),
    ("window", "cover", "window disc on the cover floor over the hole"),
    ("window", "tof_holder", "window disc in the holder recess"),
    ("tof", "tof_holder", "ToF board in the holder pocket"),
    ("vent", "cover", "vent through the cover floor"),
    ("bolts", "seal_washers", "bolt heads on the sealing washers"),
    ("nuts", "plate", "washers and nuts under the plate"),
    ("bolts", "nuts", "nuts on the bolts"),
]
# Gaps that a sealant fills: (a, b, largest gap allowed, why).
SEALED = [
    ("probe", "cover", 1.0, "probe through the 25 mm hole, 0.5 mm gap filled with neutral-cure silicone"),
]
# Minimum gaps (mm) between parts that must not touch.
CLEARANCES = [
    ("nuts", "base", 1.0, "room beside the box for the M6 nuts"),
    ("probe", "board", 3.0, "transducer clear of the board"),
    ("collar", "driver", 1.0, "collar clear of the driver board"),
    ("tof_holder", "driver", 1.0, "ToF holder clear of the driver board"),
    ("tof", "board", 3.0, "ToF board clear of the electronics board"),
    ("cell", "base", 2.0, "cell clear of the base floor"),
    ("cell", "standoffs", 3.0, "cell clear of the standoffs"),
    ("holder", "standoffs", 3.0, "holder clear of the standoffs"),
    ("board", "base", 0.5, "board clear of the base walls and towers"),
    ("board", "cover_screws", 0.5, "board clear of the cover screws"),
    ("cap", "standoffs", 1.0, "capacitor clear of the standoffs"),
    ("module", "holder", 1.0, "module breakout clear of the cell holder"),
    ("sensors_bo", "strap", 1.0, "sensor breakouts clear of the strap"),
    ("cell", "module", 1.0, "cell clear of the module breakout"),
    ("module", "antenna", 3.0, "module clear of the antenna"),
    ("cell", "antenna", 3.0, "cell clear of the antenna"),
    ("vent", "driver", 3.0, "vent nut clear of the driver board"),
    ("collar", "cover_screws", 1.0, "collar clear of the cover screws"),
    ("tof_holder", "cover_screws", 1.0, "ToF holder clear of the cover screws"),
    ("tof_holder", "board_screws", 1.0, "ToF holder clear of the board screw heads"),
    ("driver", "board_screws", 1.0, "driver board clear of the board screw heads"),
    ("probe", "driver", 2.0, "transducer clear of the driver board"),
]


def check(p=PARAMS, verbose=True):
    """Constructability checks with build123d. Returns (passed, failed, lines)."""
    C = build_components(p)
    lines, ok, bad = [], 0, 0
    keys = list(C)
    # 1 no two parts overlap (volume of intersection under 0.5 mm3, for coincident faces)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            ba, bb = C[a].shape.bounding_box(), C[b].shape.bounding_box()
            if (ba.min.X > bb.max.X or bb.min.X > ba.max.X or ba.min.Y > bb.max.Y or bb.min.Y > ba.max.Y
                    or ba.min.Z > bb.max.Z or bb.min.Z > ba.max.Z):
                continue
            try:
                v = (C[a].shape & C[b].shape).volume
            except Exception:
                v = 0.0
            if v > 0.5:
                bad += 1
                lines.append(f"FAIL overlap {a} / {b}: {v:.1f} mm3")
            else:
                ok += 1
    lines.append(f"overlap pairs checked: {ok} clear")
    # 2 contacts
    for a, b, why in CONTACTS:
        d = C[a].shape.distance_to(C[b].shape)
        if d < 0.05:
            ok += 1
            lines.append(f"ok   touch {a} / {b} ({why})")
        else:
            bad += 1
            lines.append(f"FAIL touch {a} / {b}: gap {d:.2f} mm ({why})")
    for a, b, gmax, why in SEALED:
        d = C[a].shape.distance_to(C[b].shape)
        if d <= gmax:
            ok += 1
            lines.append(f"ok   sealed gap {a} / {b} {d:.2f} mm <= {gmax} ({why})")
        else:
            bad += 1
            lines.append(f"FAIL sealed gap {a} / {b} {d:.2f} mm > {gmax} ({why})")
    # 3 clearances
    for a, b, gmin, why in CLEARANCES:
        d = C[a].shape.distance_to(C[b].shape)
        if d >= gmin:
            ok += 1
            lines.append(f"ok   gap {a} / {b} {d:.1f} mm >= {gmin} ({why})")
        else:
            bad += 1
            lines.append(f"FAIL gap {a} / {b} {d:.1f} mm < {gmin} ({why})")
    # 4 nothing floats: every part touches at least one other
    for k in keys:
        if not any(C[k].shape.distance_to(C[o].shape) < 0.05 for o in keys if o != k):
            bad += 1
            lines.append(f"FAIL {k} touches nothing")
        else:
            ok += 1
    # 5 envelope
    D = derived(p)
    if D["below_lid"] <= 100 and D["footprint"][0] <= 160 and D["footprint"][1] <= 90:
        ok += 1
        lines.append(f"ok   envelope below the lid {D['footprint'][0]:.0f} x {D['footprint'][1]:.0f} x {D['below_lid']:.1f} mm (R16)")
    else:
        bad += 1
        lines.append("FAIL envelope over R16")
    if verbose:
        print("\n".join(lines))
        print(f"\nconstructability checks: {ok} passed, {bad} failed")
    return ok, bad, lines


if __name__ == "__main__":
    if "--check" in sys.argv:
        _, nbad, _ = check()
        sys.exit(1 if nbad else 0)
    from build123d import Compound, export_step, export_stl
    out = Path(__file__).resolve().parents[1]
    (out / "step").mkdir(exist_ok=True)
    (out / "stl").mkdir(exist_ok=True)
    parts, bracket_plate = build_parts()
    items = {
        "binlevel-assembly": assembly(),
        "sensor-unit": Compound(children=[s for _, _, s in parts]),
        "bracket": bracket_plate,
    }
    for name, shape in items.items():
        export_step(shape, str(out / "step" / f"{name}.step"))
        export_stl(shape, str(out / "stl" / f"{name}.stl"), tolerance=0.05, angular_tolerance=0.3)
    D = derived()
    bb = items["sensor-unit"].bounding_box()
    print(f"exported {', '.join(items)} to cad/step and cad/stl")
    print(f"sensor unit bounding box {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm (incl. bolts above the lid)")
    print(f"below the lid: {D['footprint'][0]:.0f} x {D['footprint'][1]:.0f} x {D['below_lid']:.1f} mm; "
          f"transducer face to floor {D['face_to_floor']:.1f} mm")
