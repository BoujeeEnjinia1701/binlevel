"""BinLevel parametric model (build123d), TRL 3, massing-plus level of detail.

Run from the repo root:  python cad/src/model.py
Exports STEP and STL into cad/step and cad/stl:
    binlevel-assembly.step / .stl   sensor unit bolted under a patch of the container lid
    sensor-unit.step / .stl         the nine BOM parts only (no lid)
    bracket.step / .stl             stainless bracket plate with end tabs (BOM item 2, bolts excluded)

Axes and origin: the bottom face of the enclosure is z = 0, Z is up, X runs along the
enclosure length (transducer on -X, ToF window on +X) and Y across it. The lid underside is
at z = enc_h + plate_t. The container (an 1,100 L four-wheel communal container, EN 840 class,
a typical-size estimate) is described by PARAMS for the calculations and the concept media,
but only a lid patch is part of the exported assembly.

Main dimensions and interfaces only: enclosure envelope, sensor apertures, bracket and bolt
pattern through the lid, cell and board positions. Not fabrication detail; not for
fabrication. The same PARAMS feed docs/04-calcs/sizing.py (BNL-CAL-001), the drawing
BNL-DWG-001 (cad/src/sheets.py) and the concept media (cad/src/concept_media.py).
"""
import math
from pathlib import Path

# Top-level parameters (mm unless noted). Edit these, not the geometry below.
PARAMS = {
    # 1 enclosure: stock IP67 ABS or PC box (outer), wall, cover split height above the bottom
    "enc": (115.0, 65.0, 45.0), "enc_wall": 2.5, "split_z": 15.0,
    # 2 bracket: stainless plate against the lid underside, two end tabs, four M6 bolts
    "plate": (150.0, 80.0), "plate_t": 1.5, "tab": (60.0, 30.0),
    "bolt_pitch": (130.0, 60.0), "bolt_d": 6.0, "bolt_len": 40.0, "head_d": 10.5, "head_h": 3.3,
    # 3 ultrasonic transducer (JSN-SR04T class): position on X, body diameter, protrusion below the box
    "us_x": -35.0, "us_d": 24.0, "us_len": 24.0, "us_protrude": 14.5, "us_hole_d": 25.0,
    # 4 ToF sensor (VL53L1X class) behind a window
    "tof_x": 35.0, "tof_board": (13.0, 18.0, 3.0), "win_d": 11.0,
    # 5 LoRaWAN module (RAK3172 class, 15 x 15.5 x 2.5 mm)
    "module": (16.0, 15.0, 2.5), "module_xy": (-38.0, 14.0),
    # 6 carrier PCB
    "pcb": (105.0, 55.0, 1.6), "pcb_z": 10.2,
    # 7 Li-SOCl2 C cell (ER26500 class) lying along X
    "cell_d": 26.2, "cell_len": 50.0, "cell_xy": (8.0, -6.0),
    # 8 flexible antenna on the inner +Y wall
    "ant": (70.0, 0.6, 12.0), "ant_z": 28.0,
    # lid interface (HDPE lid wall) and the container, for the calculations and media context
    "lid_t": 5.0, "lid_patch": (220.0, 140.0),
    "cont_outer": (1370.0, 1070.0), "cont_body": (1300.0, 1000.0), "cont_wall": 8.0,
    "cont_floor_z": 220.0, "cont_rim_z": 1300.0,
    # sensor position in the lid, measured from the container center line (x, y)
    "mount_xy": (0.0, 0.0),
}


def derived(p=PARAMS):
    """Dimensions the calc note and drawing quote, computed from PARAMS."""
    ew, ed, eh = p["enc"]
    pw, pd = p["plate"]
    lid_under = eh + p["plate_t"]
    face = -p["us_protrude"]                                   # transducer face, local z
    floor_inner = p["cont_floor_z"] + p["cont_wall"]
    depth_lid = p["cont_rim_z"] - floor_inner                   # lid underside to inner floor
    face_to_floor = depth_lid - (lid_under - face)              # transducer face to inner floor
    inner = (p["cont_body"][0] - 2 * p["cont_wall"], p["cont_body"][1] - 2 * p["cont_wall"])
    mx, my = p["mount_xy"]
    wall_clear = min(inner[0] / 2 - abs(mx + p["us_x"]), inner[1] / 2 - abs(my))
    return {
        "lid_under": lid_under,
        "below_lid": lid_under - face,                          # overall height below the lid
        "footprint": (max(pw, ew), max(pd, ed)),
        "face_to_floor": face_to_floor,
        "depth_lid": depth_lid,
        "inner": inner,
        "inner_volume_l": inner[0] * inner[1] * depth_lid / 1e6,
        "wall_clear": wall_clear,
        "tab_gap": ew,                                          # tabs clamp the enclosure ends
    }


def build_parts(p=PARAMS):
    """Return [(bom_no, name, shape)] for the nine BOM parts, in local coordinates."""
    from build123d import Box, Cylinder, Pos, Rot
    ew, ed, eh = p["enc"]
    w = p["enc_wall"]
    pw, pd = p["plate"]
    pt = p["plate_t"]
    tw, th = p["tab"]

    enc = Pos(0, 0, eh / 2) * Box(ew, ed, eh) - Pos(0, 0, eh / 2) * Box(ew - 2 * w, ed - 2 * w, eh - 2 * w)
    enc = enc - Pos(p["us_x"], 0, 0) * Cylinder(p["us_hole_d"] / 2, 10) - Pos(p["tof_x"], 0, 0) * Cylinder(p["win_d"] / 2, 10)

    plate = Pos(0, 0, eh + pt / 2) * Box(pw, pd, pt)
    for bx in (-p["bolt_pitch"][0] / 2, p["bolt_pitch"][0] / 2):
        for by in (-p["bolt_pitch"][1] / 2, p["bolt_pitch"][1] / 2):
            plate = plate - Pos(bx, by, eh + pt / 2) * Cylinder(p["bolt_d"] / 2 + 0.3, pt + 2)
    tabs = (Pos(-(ew / 2 + pt / 2), 0, eh - th / 2) * Box(pt, tw, th)
            + Pos(ew / 2 + pt / 2, 0, eh - th / 2) * Box(pt, tw, th))
    bracket_plate = plate + tabs
    bolts = None
    top = eh + pt
    for bx in (-p["bolt_pitch"][0] / 2, p["bolt_pitch"][0] / 2):
        for by in (-p["bolt_pitch"][1] / 2, p["bolt_pitch"][1] / 2):
            # button head on the lid top (tamper-resistant), shank down through lid and plate, nut below
            b = (Pos(bx, by, top + p["lid_t"] - p["bolt_len"] / 2 + 12) * Cylinder(p["bolt_d"] / 2, p["bolt_len"] - 12)
                 + Pos(bx, by, top + p["lid_t"] + p["head_h"] / 2) * Cylinder(p["head_d"] / 2, p["head_h"])
                 + Pos(bx, by, top - 2.5) * Cylinder(5.5, 5))
            bolts = b if bolts is None else bolts + b
    bracket = bracket_plate + bolts

    transducer = Pos(p["us_x"], 0, p["us_len"] / 2 - p["us_protrude"]) * Cylinder(p["us_d"] / 2, p["us_len"])
    tb = p["tof_board"]
    tof = Pos(p["tof_x"], 0, 7.8) * Box(*tb) + Pos(p["tof_x"], 0, 1.25) * Cylinder(p["win_d"] / 2 - 0.5, 2.5)
    pcb = Pos(0, 0, p["pcb_z"]) * Box(*p["pcb"])
    mx, my = p["module_xy"]
    module = Pos(mx, my, p["pcb_z"] + p["pcb"][2] / 2 + p["module"][2] / 2 + 0.2) * Box(*p["module"])
    cx, cy = p["cell_xy"]
    r = p["cell_d"] / 2
    cell = Pos(cx, cy, p["pcb_z"] + p["pcb"][2] / 2 + 2 + r) * Rot(0, 90, 0) * Cylinder(r, p["cell_len"])
    a = p["ant"]
    antenna = Pos(0, ed / 2 - w - a[1] / 2 - 0.1, p["ant_z"]) * Box(*a)
    gasket = Pos(0, 0, p["split_z"]) * (Box(ew + 1, ed + 1, 2) - Box(ew - 5, ed - 5, 3))
    return [
        (1, "Enclosure, IP67 ABS or PC", enc),
        (2, "Stainless bracket and tamper bolts", bracket),
        (3, "Ultrasonic transducer, sealed", transducer),
        (4, "Near-range ToF sensor", tof),
        (5, "LoRaWAN module, STM32WL class", module),
        (6, "Carrier PCB with accelerometer", pcb),
        (7, "Li-SOCl2 C cell and holder", cell),
        (8, "Flexible antenna", antenna),
        (9, "Gaskets and vent", gasket),
    ], bracket_plate


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
    parts, _ = build_parts(p)
    shapes = [s for _, _, s in parts] + ([lid_patch(p)] if with_lid else [])
    return Compound(children=shapes)


if __name__ == "__main__":
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
        export_stl(shape, str(out / "stl" / f"{name}.stl"))
    D = derived()
    bb = items["sensor-unit"].bounding_box()
    print(f"exported {', '.join(items)} to cad/step and cad/stl")
    print(f"sensor unit bounding box {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm (incl. bolts above the lid)")
    print(f"below the lid: {D['footprint'][0]:.0f} x {D['footprint'][1]:.0f} x {D['below_lid']:.1f} mm; "
          f"transducer face to floor {D['face_to_floor']:.1f} mm")
