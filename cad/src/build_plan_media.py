"""BinLevel prototype build plan pictures (BNL-BLD-001, STANDARDS section 18).

Run from the repo root:  python cad/src/build_plan_media.py [overview|sheets|layouts|joints|steps|wiring ...]
With no argument it draws everything. Every picture is drawn from cad/src/model.py
(build_components), so the pictures and the model never disagree:
    docs/05-build-plan/overview.png        every component pulled apart, numbered in build order
    cad/drawings/BNL-DWG-101 to 106        making sketches for the made and drilled components
    docs/05-build-plan/plate-holes.png     hole positions in the bracket plate
    docs/05-build-plan/cover-holes.png     hole positions in the enclosure cover
    docs/05-build-plan/joint-NN.png        close-ups of the joints that need explaining
    docs/05-build-plan/step-NN.png         one picture per assembly step
    docs/05-build-plan/wiring.png          block-level wiring with wire sizes (matplotlib)
A single picture can be drawn with, for example, "steps 4" or "joints 2" to keep memory low.
Uses .kit/build_views.py. BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / ".kit"), str(ROOT / "cad" / "src")]
import build_views as bv  # noqa: E402
from build_views import Part  # noqa: E402
from model import PARAMS as P, build_components, derived, lid_patch  # noqa: E402

OUT = ROOT / "docs" / "05-build-plan"
DWG = ROOT / "cad" / "drawings"
DATE = "2026-09-30"
REPO = "github.com/BoujeeEnjinia1701/binlevel"
D = derived(P)
C = build_components(P)
EW, ED, EH = P["enc"]

COL = {"plate": "#94A3B8", "studs": "#334155", "base": "#E5E7EB", "cover": "#D1D5DB", "gasket": "#111827",
       "bseals": "#B91C1C", "standoffs": "#64748B", "antenna": "#111827", "board": "#16A34A", "parts": "#2563EB",
       "driver": "#0F766E", "holder": "#1F2937", "cell": "#C2410C", "strap": "#7C3AED", "screws": "#111827",
       "probe": "#0E7490", "collar": "#B45309", "window": "#7DD3FC", "tof_holder": "#D97706", "tof": "#7C3AED",
       "vent": "#F8FAFC", "bolts": "#111827", "lid": "#A8A29E"}


def S(*keys):
    out = None
    for k in keys:
        out = C[k].shape if out is None else out + C[k].shape
    return out


def part(name, shape, color, explode=(0, 0, 0), alpha=1.0):
    return Part(name, shape, color, None, tuple(explode), alpha)


def lid():
    return part("Bin lid (HDPE, site part)", lid_patch(P), COL["lid"])


# ----------------------------------------------------------------- named parts, in build order
def made():
    return {
        "plate": part("Bracket plate with its four studs", S("plate", "studs"), COL["plate"]),
        "base": part("Enclosure base, drilled", C["base"].shape, COL["base"]),
        "fix": part("Sealing washers and standoffs (4 each)", S("bseals", "standoffs"), COL["standoffs"]),
        "antenna": part("Antenna", C["antenna"].shape, COL["antenna"]),
        "board": part("Electronics board", C["board"].shape, COL["board"]),
        "parts": part("Module, breakouts and capacitor", S("module", "sensors_bo", "power_bo", "cap"), COL["parts"]),
        "driver": part("Ultrasonic driver board", S("driver", "driver_standoffs"), COL["driver"]),
        "cell": part("Cell holder, cell and strap", S("holder", "cell", "strap"), COL["cell"]),
        "bscrews": part("Board screws (4)", C["board_screws"].shape, COL["screws"]),
        "cover": part("Enclosure cover, drilled", C["cover"].shape, COL["cover"]),
        "probe": part("Transducer probe", C["probe"].shape, COL["probe"]),
        "collar": part("Probe collar (printed)", C["collar"].shape, COL["collar"]),
        "window": part("Window disc", C["window"].shape, COL["window"]),
        "tof_holder": part("ToF holder (printed)", C["tof_holder"].shape, COL["tof_holder"]),
        "tof": part("ToF breakout", C["tof"].shape, COL["tof"]),
        "vent": part("Vent", C["vent"].shape, "#94A3B8"),
        "close": part("Gasket and cover screws", S("gasket", "cover_screws"), COL["gasket"]),
        "bolts": part("M6 bolts, washers and nuts", S("bolts", "seal_washers", "nuts"), COL["bolts"]),
    }


ORDER = ["plate", "base", "fix", "antenna", "board", "parts", "driver", "cell", "bscrews", "cover", "probe",
         "collar", "window", "tof_holder", "tof", "vent", "close", "bolts"]


# ----------------------------------------------------------------- overview
def overview():
    M = made()
    off = {"plate": (0, 0, 70), "base": (0, 0, 20), "fix": (0, 0, -15), "antenna": (-150, 40, 40),
           "board": (0, 0, -70), "parts": (0, 0, -55), "driver": (0, 0, -100), "cell": (-150, 0, -55),
           "bscrews": (0, 0, -85), "cover": (180, 0, -55), "probe": (180, 0, -125), "collar": (180, 0, 30),
           "window": (180, 0, 0), "tof_holder": (180, 0, 22), "tof": (180, 0, 45), "vent": (180, 0, -105),
           "close": (180, 0, -25), "bolts": (0, 0, 110)}
    parts = []
    for k in ORDER:
        p = M[k]
        p.explode = off[k]
        parts.append(p)
    return bv.overview(parts, OUT / "overview.png", "BinLevel prototype: every component, pulled apart",
                       subtitle="Numbered in build order. Seen from the front right and slightly below. Left: the base and what goes in it; right: the cover and its sensors",
                       elev=-14, azim=-62, size=(11, 7.5), dpi=150, key=True)


# ----------------------------------------------------------------- making sketches
def sheets():
    import build123d as b
    M = made()
    base = dict(project="BinLevel", date=DATE)
    out = []
    sx, sy = P["stud_xy"]
    bpx, bpy = P["bolt_pitch"]

    # 101 bracket plate
    out.append(bv.component_sheet(
        Part("Bracket plate", S("plate", "studs"), COL["plate"]), [M["base"], M["bolts"]],
        dwg_no="BNL-DWG-101", title="BinLevel bracket plate: making sketch",
        material="Aluminium sheet 2 mm, 5052 class; four M4 x 12 flush-head press-in studs",
        view_shape=b.Pos(0, 0, -EH) * S("plate", "studs"), inset_view=(-25, -55),
        notes=["Blank 150 x 80 mm, 2 mm 5052 aluminium, square. Round the corners",
               "  about 3 mm and deburr every edge.",
               "Measure from the centre lines. The face that goes against the bin",
               "  lid is the top face; the box hangs under the other face.",
               f"Bolt holes: four 6.6 mm at {bpx / 2:.0f} mm each side of the long centre",
               f"  line and {bpy / 2:.0f} mm each side of the short one ({bpx:.0f} x {bpy:.0f}).",
               f"Stud holes: four 4.2 mm at {sx:.0f} mm and {sy:.0f} mm each side",
               f"  ({2 * sx:.0f} x {2 * sy:.0f}). Check the hole size on the stud maker's sheet.",
               "Press the four M4 x 12 flush-head studs in from the top face with a",
               "  press or a vice with smooth jaws, until the heads sit flush.",
               "Fit: top face flat on the lid underside; the box base sits flat",
               "  on the lower face, the studs through its floor.",
               "Check: studs square to the plate, heads flush, none turns by hand."],
        **base))

    # 102 enclosure base, drilled
    out.append(bv.component_sheet(
        Part("Enclosure base", C["base"].shape, COL["base"]), [M["plate"], M["fix"], M["board"], M["cover"]],
        dwg_no="BNL-DWG-102", title="BinLevel enclosure base: drilling sketch",
        material="Bought IP67 ABS or PC box 115 x 65 x 55 mm (base part)",
        view_shape=b.Pos(0, 0, -P["split_z"]) * C["base"].shape, inset_view=(-25, -55),
        notes=["The deep part of a stock IP67 box, 115 x 65 mm outside, 40 mm",
               "  deep from the rim, 2.5 mm wall, four corner screw towers.",
               f"Drill four 4.5 mm holes in the floor at {sx:.0f} and {sy:.0f} mm each side",
               "  of the centre lines. Easiest: stand the base on the bracket plate,",
               "  centre it, and mark through the stud positions.",
               "Tape the floor, pilot drill 2.5 mm slowly with wood behind, then",
               "  4.5 mm. Deburr inside and out; no solvents on ABS or PC.",
               "Fit: the outside of the floor sits flat on the plate; the studs pass",
               "  through, and a sealing washer and a standoff go on each one inside.",
               "Check: the base sits flat on the plate with all four studs through",
               "  and no hole cracked."],
        **base))

    # 103 enclosure cover, drilled, drawn upside down so the top view shows the outside of the floor
    flip = b.Rot(0, 0, 180) * b.Rot(180, 0, 0) * b.Pos(0, 0, -P["split_z"] / 2) * C["cover"].shape
    out.append(bv.component_sheet(
        Part("Enclosure cover", C["cover"].shape, COL["cover"]), [M["base"], M["probe"], M["tof_holder"], M["collar"], M["vent"]],
        dwg_no="BNL-DWG-103", title="BinLevel enclosure cover: drilling sketch",
        material="Bought IP67 ABS or PC box 115 x 65 x 55 mm (cover part)",
        view_shape=flip, inset_view=(-30, -55),
        notes=["Drawn upside down: the cover lies outside face up with the unit's",
               "  front edge toward you, as in the cover layout picture of the plan,",
               "  so the transducer hole is on the right of the top view.",
               f"Transducer hole 25 mm, {-P['us_x']:.0f} mm from the centre toward the end",
               f"  that is on the left when the unit is seen from the front. Window",
               f"  hole 11 mm, {P['tof_x']:.0f} mm toward the other end. Both on the long centre line.",
               f"Vent hole 8.2 mm, on the short centre line, {-P['vent_xy'][1]:.0f} mm from the",
               "  long centre line toward the front edge.",
               "Tape the face, pilot 3 mm slowly with wood behind, open out with a",
               "  step drill, light pressure. Deburr; no solvents.",
               "Fit: the probe goes through the 25 mm hole; the printed collar and",
               "  ToF holder are bonded inside; the vent nut goes inside.",
               "Check: no crack from any hole under a bright lamp."],
        **base))

    # 104 electronics board
    out.append(bv.component_sheet(
        Part("Electronics board", C["board"].shape, COL["board"]), [M["base"], M["fix"], M["parts"], M["driver"], M["cell"]],
        dwg_no="BNL-DWG-104", title="BinLevel electronics board: making sketch",
        material="Perforated prototyping board, FR-4, 1.6 mm, 2.54 mm pitch",
        view_shape=b.Pos(0, 0, -D["pcb_bot"]) * C["board"].shape, inset_view=(-30, -55),
        notes=["Cut the board to 90 x 50 mm with a fine saw; file the edges smooth.",
               "Measure from the centre lines. The top face carries the cell and",
               "  the breakouts; the driver board hangs under the other face.",
               f"Fixing holes: four 4.3 mm at {sx:.0f} and {sy:.0f} mm each side of centre.",
               f"Driver board holes: four 3.2 mm at {P['driver_x'] - 17.5:.0f} and {P['driver_x'] + 17.5:.0f} mm",
               "  along, 11 mm each side across. Match your driver board's holes.",
               f"Strap slots: two 12 x 3 mm on the cross line, {P['cell_xy'][1] + P['cell_d'] / 2 + 0.5:.1f} mm toward the back",
               f"  edge and {-(P['cell_xy'][1] - P['cell_d'] / 2 - 0.5):.1f} mm toward the front edge. Drill and file.",
               "Lay out on the top: cell holder along the front half; module,",
               "  sensor breakouts, power parts and capacitor along the back half.",
               "Fit: the top face sits on the four standoff ends, held by four M4",
               "  screws from below.",
               "Check: the board drops onto the standoffs without forcing."],
        **base))

    # 105 probe collar
    ux = P["us_x"]
    out.append(bv.component_sheet(
        Part("Probe collar", C["collar"].shape, COL["collar"]), [M["cover"], M["probe"]],
        dwg_no="BNL-DWG-105", title="BinLevel probe collar: making sketch",
        material="ASA, 3D printed, 100 % infill",
        view_shape=b.Pos(-ux, 0, -D["cover_floor"]) * C["collar"].shape, inset_view=(30, -55),
        notes=[f"Flange {P['collar'][0]:.0f} mm across, {P['collar'][1]:.0f} mm thick; tube {P['collar'][2]:.0f} mm across,",
               f"  {P['collar'][3]:.0f} mm tall overall; bore 24.0 mm to suit the probe.",
               "Print flange down in ASA in an enclosed printer. Measure your probe",
               "  first and print the bore 0.1 to 0.2 mm under it, for a push fit.",
               "Add a 2.5 mm hole through the tube wall 6 mm above the flange and",
               "  tap it M3 for a nylon-tipped grub screw.",
               "Fit: push the probe through the cover hole from outside so its face",
               f"  stands {P['us_protrude']} mm proud. Seal the gap in the hole with neutral-cure",
               "  silicone; slide the collar over the probe from inside and bond the",
               "  flange to the floor with two-part plastics epoxy.",
               "Tighten the grub screw finger tight once the epoxy has cured.",
               "Check: the probe does not move when pushed by hand."],
        **base))

    # 106 ToF holder (with the window disc)
    tx = P["tof_x"]
    out.append(bv.component_sheet(
        Part("ToF holder", C["tof_holder"].shape, COL["tof_holder"]), [M["cover"], M["window"], M["tof"]],
        dwg_no="BNL-DWG-106", title="BinLevel ToF holder and window: making sketch",
        material="ASA, 3D printed; window 16 mm x 1.5 mm PMMA or glass",
        view_shape=b.Pos(-tx, 0, -D["cover_floor"]) * C["tof_holder"].shape, inset_view=(30, -55),
        notes=["Block 20 x 22 x 6 mm, printed flat in ASA, 100 % infill.",
               "Through it: an 11 mm light hole on its centre.",
               "Underneath: a 16.5 mm recess 1.5 mm deep for the window disc.",
               "On top: a 13.5 x 18.5 mm pocket 2 mm deep for the ToF breakout,",
               "  with two 1.8 mm holes for M2 screws at the breakout's holes.",
               "Window: a 16 mm disc of 1.5 mm clear PMMA or glass, cut with a",
               "  hole saw or bought; keep its film on until fitting.",
               "Fit: window in the recess with a thin ring of neutral-cure silicone",
               "  on its face; holder centred over the 11 mm cover hole and bonded",
               "  to the floor with plastics epoxy. Breakout in the pocket, sensor",
               "  down onto the window, held by two M2 screws.",
               "Check: looking in from outside, the sensor is centred in the hole."],
        **base))
    return out


# ----------------------------------------------------------------- drilling layouts
def layouts():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, FancyBboxPatch
    INK, MUT, AC = "#111827", "#4B5563", "#0F766E"
    res = []
    OUT.mkdir(parents=True, exist_ok=True)
    pw, pd = P["plate"]
    sx, sy = P["stud_xy"]
    bx, by = P["bolt_pitch"][0] / 2, P["bolt_pitch"][1] / 2

    def frame(title, sub, size):
        fig = plt.figure(figsize=size, dpi=150)
        fig.text(0.03, 0.975, title, fontsize=13, fontweight="bold", color=INK, va="top")
        fig.text(0.03, 0.925, sub, fontsize=8.5, color=MUT, va="top")
        fig.text(0.03, 0.015, "BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT", fontsize=7, color="#B45309")
        fig.text(0.97, 0.015, REPO, fontsize=7, color=AC, ha="right", family="monospace")
        return fig

    def hole(ax, x, y, d, label, dy):
        ax.add_patch(plt.Circle((x, y), d / 2, fc="white", ec=INK, lw=1.1))
        ax.plot([x - d / 2 - 2, x + d / 2 + 2], [y, y], color=MUT, lw=0.4)
        ax.plot([x, x], [y - d / 2 - 2, y + d / 2 + 2], color=MUT, lw=0.4)
        if label:
            ax.text(x, y + dy, label, ha="center", va="bottom" if dy > 0 else "top", fontsize=7.2, color=INK,
                    bbox=dict(boxstyle="round,pad=0.15", fc="#F3F4F6", ec="none"))

    # plate, seen from the top face (the face against the lid)
    fig = frame("Bracket plate: hole positions",
                "Seen from the top face (the face against the bin lid). Sizes in mm from the centre lines, taken from the model.", (11, 6.6))
    ax = fig.add_axes([0.05, 0.08, 0.9, 0.8]); ax.set_aspect("equal"); ax.set_axis_off()
    ax.add_patch(FancyBboxPatch((-pw / 2 + 3, -pd / 2 + 3), pw - 6, pd - 6, boxstyle="round,pad=3", fc="#F1F5F9", ec=INK, lw=1.2))
    ax.add_patch(Rectangle((-EW / 2, -ED / 2), EW, ED, fc="none", ec=MUT, lw=0.7, ls="--"))
    ax.text(0, -ED / 2 + 3, "outline of the box under the plate", ha="center", va="bottom", fontsize=7, color=MUT)
    ax.axvline(0, ymin=0.08, ymax=0.92, color=MUT, lw=0.6, ls=(0, (8, 3, 2, 3)))
    ax.axhline(0, xmin=0.06, xmax=0.94, color=MUT, lw=0.6, ls=(0, (8, 3, 2, 3)))
    for x, y in [(sx_ * bx, sy_ * by) for sx_ in (-1, 1) for sy_ in (-1, 1)]:
        hole(ax, x, y, 6.6, "6.6 bolt" if y > 0 else None, 5)
    for x, y in [(sx_ * sx, sy_ * sy) for sx_ in (-1, 1) for sy_ in (-1, 1)]:
        hole(ax, x, y, P["stud_hole_d"], "4.2 stud" if y > 0 else None, 4)
    # dimensions
    for x0, x1, yl, t in ((-bx, bx, -pd / 2 - 9, f"{2 * bx:.0f} between bolt holes"), (-sx, sx, -pd / 2 - 18, f"{2 * sx:.0f} between studs"),
                          (-pw / 2, pw / 2, pd / 2 + 8, f"{pw:.0f} plate")):
        ax.annotate("", xy=(x0, yl), xytext=(x1, yl), arrowprops=dict(arrowstyle="<->", color=AC, lw=0.8))
        ax.text(0, yl - 1.2, t, ha="center", va="top", fontsize=8, color=AC, bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none"))
    for y0, y1, xl, t in ((-by, by, pw / 2 + 8, f"{2 * by:.0f}"), (-sy, sy, pw / 2 + 20, f"{2 * sy:.0f}"), (-pd / 2, pd / 2, -pw / 2 - 10, f"{pd:.0f}")):
        ax.annotate("", xy=(xl, y0), xytext=(xl, y1), arrowprops=dict(arrowstyle="<->", color=AC, lw=0.8))
        ax.text(xl + 1.5, 0, t, ha="left", va="center", fontsize=8, color=AC, rotation=90)
    ax.set_xlim(-pw / 2 - 16, pw / 2 + 48); ax.set_ylim(-pd / 2 - 26, pd / 2 + 14)
    fig.savefig(OUT / "plate-holes.png", facecolor="white"); plt.close(fig); res.append(OUT / "plate-holes.png")

    # cover floor, seen from outside (from below), front edge toward the reader
    fig = frame("Enclosure cover: drilling layout",
                "Seen from outside (from below the unit), front edge toward you. Sizes in mm from the centre lines, taken from the model.\n"
                "Solid circle: the hole to drill. Dashed circle: the part that sits on the floor inside.", (11, 6.8))
    ax = fig.add_axes([0.05, 0.08, 0.9, 0.78]); ax.set_aspect("equal"); ax.set_axis_off()
    ax.add_patch(FancyBboxPatch((-EW / 2 + 4, -ED / 2 + 4), EW - 8, ED - 8, boxstyle="round,pad=4", fc="#F3F4F6", ec=INK, lw=1.2))
    tx, ty = P["tower_xy"]
    for x, y in [(a * tx, c * ty) for a in (-1, 1) for c in (-1, 1)]:
        ax.add_patch(plt.Circle((x, y), 3.5, fc="#E5E7EB", ec=MUT, lw=0.6))
    ax.text(-tx, ty - 5, "cover screw\n(with the box)", ha="center", va="top", fontsize=6.5, color=MUT)
    ax.axvline(0, ymin=0.06, ymax=0.94, color=MUT, lw=0.6, ls=(0, (8, 3, 2, 3)))
    ax.axhline(0, xmin=0.04, xmax=0.96, color=MUT, lw=0.6, ls=(0, (8, 3, 2, 3)))
    # Seen from below with the front (-Y) toward the reader, the unit's -X end is on the right of the
    # page, so x is mirrored here: the transducer end (the left end seen from the front) is on the right.
    ux, tx_ = -P["us_x"], -P["tof_x"]
    vx, vy = -P["vent_xy"][0], P["vent_xy"][1]
    ax.add_patch(plt.Circle((ux, 0), P["collar"][0] / 2, fc="none", ec=MUT, lw=0.6, ls="--"))
    hole(ax, ux, 0, P["us_hole_d"], None, 0)
    ax.text(ux, 15.5, "Transducer\n25.0 hole", ha="center", va="bottom", fontsize=7.2, color=INK,
            bbox=dict(boxstyle="round,pad=0.15", fc="#F3F4F6", ec="none"))
    ax.add_patch(Rectangle((tx_ - 10, -11), 20, 22, fc="none", ec=MUT, lw=0.6, ls="--"))
    hole(ax, tx_, 0, P["win_d"], None, 0)
    ax.text(tx_, 12.5, "ToF window\n11.0 hole", ha="center", va="bottom", fontsize=7.2, color=INK,
            bbox=dict(boxstyle="round,pad=0.15", fc="#F3F4F6", ec="none"))
    hole(ax, vx, vy, P["vent_hole_d"], None, 0)
    ax.text(vx + 7, vy, "Vent, 8.2 hole", ha="left", va="center", fontsize=7.2, color=INK,
            bbox=dict(boxstyle="round,pad=0.15", fc="#F3F4F6", ec="none"))
    yl = -ED / 2 - 6
    for x0, x1, t, yy in ((ux, 0, f"{abs(ux):.0f}", yl), (0, tx_, f"{abs(tx_):.0f}", yl)):
        ax.annotate("", xy=(x0, yy), xytext=(x1, yy), arrowprops=dict(arrowstyle="<->", color=AC, lw=0.8))
        ax.text((x0 + x1) / 2, yy - 1.2, t, ha="center", va="top", fontsize=8, color=AC)
    ax.annotate("", xy=(-EW / 2 - 6, 0), xytext=(-EW / 2 - 6, vy), arrowprops=dict(arrowstyle="<->", color=AC, lw=0.8))
    ax.plot([-EW / 2 - 8, vx - 5], [vy, vy], color=AC, lw=0.4, ls=":")
    ax.text(-EW / 2 - 7.5, vy / 2, f"{-vy:.0f}", ha="right", va="center", fontsize=8, color=AC)
    ax.text(vx - 6, vy - 2.5, "vent on the centre line,\n20 toward the front edge", ha="right", va="top", fontsize=6.8, color=MUT)
    ax.text(0, -ED / 2 - 15, "front edge of the unit (toward you)", ha="center", va="top", fontsize=8, color=MUT)
    ax.text(-EW / 2, ED / 2 + 2, f"cover {EW:.0f} x {ED:.0f} outside", ha="left", va="bottom", fontsize=7.5, color=MUT)
    ax.text(EW / 2, ED / 2 + 2, "transducer end: the LEFT end when the unit is seen from the front", ha="right", va="bottom", fontsize=7.5, color="#B45309")
    ax.set_xlim(-EW / 2 - 16, EW / 2 + 8); ax.set_ylim(-ED / 2 - 22, ED / 2 + 8)
    fig.savefig(OUT / "cover-holes.png", facecolor="white"); plt.close(fig); res.append(OUT / "cover-holes.png")
    return res


# ----------------------------------------------------------------- joints
def _win(sh, x0, x1, y0, y1, z0, z1):
    import build123d as b
    return sh & (b.Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * b.Box(x1 - x0, y1 - y0, z1 - z0))


def joints(only=None):
    out = []
    sx, sy = P["stud_xy"]
    J = {}
    # 1 stud through the base floor into the standoff, cut through the stud
    J[1] = (lambda: [("Bracket plate", "plate", COL["plate"]), ("Press-in stud, head flush", "studs", COL["studs"]),
                     ("Base floor", "base", COL["base"]), ("Bonded sealing washer", "bseals", COL["bseals"]),
                     ("Hex standoff on the stud", "standoffs", COL["standoffs"])],
            (sx - 16, sx + 6, sy, sy + 12, 38, 60), "Joint 1: stud, base floor, sealing washer and standoff (cut open)",
            "Cut through one stud, seen from the front. The standoff squeezes the sealing washer against the floor", 12, -90)
    # 2 board on a standoff
    J[2] = (lambda: [("Hex standoff", "standoffs", COL["standoffs"]), ("Electronics board", "board", COL["board"]),
                     ("M4 x 8 screw from below", "board_screws", COL["screws"]), ("Base back wall", "base", COL["base"])],
            (sx - 16, sx + 6, sy, ED / 2, 13, 32), "Joint 2: electronics board on a standoff (cut open)",
            "Cut through one standoff, seen from the front. The board's top face sits on the standoff end", 12, -90)
    # 3 driver board under the board
    dx = P["driver_x"]
    J[3] = (lambda: [("Electronics board", "board", COL["board"]), ("M3 x 4 nylon standoffs", "driver_standoffs", COL["standoffs"]),
                     ("Ultrasonic driver board, parts down", "driver", "#B45309")],
            (dx - 24, dx + 24, -11, 16, 6, 24), "Joint 3: ultrasonic driver board under the electronics board (cut open)",
            "Cut through two of its four standoffs, seen from the front. 4 mm nylon standoffs, M3 nylon screws", -6, -88)
    # 4 probe and collar
    ux = P["us_x"]
    J[4] = (lambda: [("Cover floor", "cover", COL["cover"]), ("Transducer probe", "probe", COL["probe"]),
                     ("Probe collar, bonded to the floor", "collar", COL["collar"])],
            (ux - 19, ux + 22, 0, 18, -16, 15), "Joint 4: transducer probe and its collar in the cover (cut open)",
            "Cut through the probe, seen from the front. Silicone fills the 0.5 mm gap in the hole; the collar holds the probe", 10, -90)
    # 5 ToF window stack
    tx = P["tof_x"]
    J[5] = (lambda: [("Cover floor", "cover", COL["cover"]), ("Window disc, sealed", "window", COL["window"]),
                     ("ToF holder, bonded", "tof_holder", COL["tof_holder"]), ("ToF breakout, sensor down", "tof", COL["tof"])],
            (tx - 14, tx + 14, 0, 14, -1, 11), "Joint 5: ToF window, holder and breakout (cut open)",
            "Cut through the window, seen from the front. The window seals over the 11 mm hole from inside", 15, -90)
    # 6 M6 bolt through lid and plate beside the box
    bx, by = P["bolt_pitch"][0] / 2, P["bolt_pitch"][1] / 2
    J[6] = (lambda: [("Bin lid (site part)", None, COL["lid"]), ("Bracket plate", "plate", COL["plate"]),
                     ("Enclosure base", "base", COL["base"]), ("Tamper bolt and sealing washer", ("bolts", "seal_washers"), COL["bolts"]),
                     ("Washer and nyloc nut", "nuts", "#475569")],
            (bx - 20, bx + 12, by, by + 10, 38, 70), "Joint 6: tamper bolt through the lid and plate, beside the box (cut open)",
            "Cut through one bolt, seen from the front. The nut sits 1.5 mm clear of the box", 10, -90)
    # 7 cover to base at a corner
    tx_, ty_ = P["tower_xy"]
    J[7] = (lambda: [("Enclosure base", "base", COL["base"]), ("Enclosure cover", "cover", COL["cover"]),
                     ("Gasket in the rim groove", "gasket", COL["gasket"]), ("Cover screw", "cover_screws", "#475569")],
            (tx_ - 9, EW / 2, ty_, ty_ + 3, -1, 33), "Joint 7: cover to base at a corner (cut open)",
            "Cut through a cover screw, seen from the front. The screw pulls the cover rim onto the gasket", 10, -90)
    # 8 cell, holder and strap
    cx, cy = P["cell_xy"]
    J[8] = (lambda: [("Electronics board", "board", COL["board"]), ("Cell holder", "holder", COL["holder"]),
                     ("C cell", "cell", COL["cell"]), ("Strap through the board slots", "strap", COL["strap"])],
            (cx - 1, cx + 4, cy - 18, cy + 18, D["pcb_bot"] - 3, D["cell_z"] + 16), "Joint 8: cell, holder and strap (cut open)",
            "Cut across the middle of the cell, seen from the right. The strap passes round the cell and under the board", 10, 0)
    for n, (fn, box_, title, sub, el, az) in J.items():
        if only and n not in only:
            continue
        ps = []
        for name, key, col in fn():
            if key is None:
                sh = lid_patch(P)
            elif isinstance(key, tuple):
                sh = S(*key)
            else:
                sh = C[key].shape
            ps.append(part(name, _win(sh, *box_), col))
        out.append(bv.joint(ps, OUT / f"joint-{n:02d}.png", title, subtitle=sub, elev=el, azim=az, size=(8, 6)))
    return out


# ----------------------------------------------------------------- assembly steps
def steps(only=None):
    M = made()
    out = []

    def mv(p, e):
        return Part(p.name, p.shape, p.color, None, tuple(e), p.alpha)

    plate, base, fix = M["plate"], M["base"], M["fix"]
    T = {}
    T[1] = lambda: ([part("Bracket plate", C["plate"].shape, COL["plate"])], [mv(part("Press-in studs (4)", C["studs"].shape, COL["studs"]), (0, 0, 40))],
                    "press the studs into the bracket plate", "From the top face, with a press or a vice with smooth jaws, until the heads are flush",
                    dict(elev=35, azim=-55))
    T[2] = lambda: ([plate], [mv(base, (0, 0, -70))], "enclosure base onto the plate",
                    "Seen from below. The base floor goes flat on the plate with the studs through its four holes",
                    dict(elev=-30, azim=-55, label_done=True))
    T[3] = lambda: ([plate, base], [mv(part("Bonded sealing washers (4)", C["bseals"].shape, COL["bseals"]), (0, 0, -45)),
                                    mv(part("Hex standoffs (4)", C["standoffs"].shape, COL["standoffs"]), (0, 0, -80))],
                    "sealing washers and standoffs onto the studs", "Seen from below, into the open base. Rubber side to the floor; standoffs firm by hand plus a quarter turn",
                    dict(elev=-55, azim=-60, label_done=False))
    T[4] = lambda: ([plate, base, fix], [mv(M["antenna"], (0, -45, -40))], "antenna onto the inner wall",
                    "Seen from below. Clean the back wall inside, peel and press the antenna on, lead toward the module end",
                    dict(elev=-50, azim=-110, label_done=False))
    T[5] = lambda: ([M["board"]], [mv(part("LoRaWAN module on its breakout", C["module"].shape, COL["parts"]), (0, 0, 40)),
                                   mv(part("Accelerometer and temperature breakouts", C["sensors_bo"].shape, "#7C3AED"), (0, 0, 40)),
                                   mv(part("Regulator, load switch and fuse", C["power_bo"].shape, "#0F766E"), (0, 0, 40)),
                                   mv(part("Buffer capacitor", C["cap"].shape, "#B45309"), (0, 0, 40)),
                                   mv(part("Cell holder (no cell yet)", C["holder"].shape, COL["holder"]), (0, 0, 40))],
                    "build the electronics board", "Each part soldered on its pins; then wire them as the wiring diagram shows",
                    dict(elev=40, azim=-60, label_done=True))
    top = [M["board"], M["parts"], part("Cell holder", C["holder"].shape, COL["holder"])]
    T[6] = lambda: (top, [mv(M["driver"], (0, 0, -45))], "ultrasonic driver board under the board",
                    "Seen from below. Four M3 nylon standoffs and screws; the driver board's parts face down",
                    dict(elev=-35, azim=-60, label_done=False))
    T[7] = lambda: (top + [M["driver"]], [mv(part("C cell", C["cell"].shape, COL["cell"]), (0, 0, 60)),
                                          mv(part("Strap through the board slots", C["strap"].shape, COL["strap"]), (0, -60, 0))],
                    "cell and strap (only at safety stop S3)", "Cell into the holder, plus end to plus mark; strap round it and through both slots, pulled snug",
                    dict(elev=30, azim=-60, label_done=False))
    boardset = part("Electronics board, complete", S("board", "module", "sensors_bo", "power_bo", "cap", "holder", "cell", "strap", "driver", "driver_standoffs"), COL["board"])
    T[8] = lambda: ([plate, base, fix, M["antenna"]], [mv(part("Electronics board with cell and breakouts", S("board", "module", "sensors_bo", "power_bo", "cap", "holder", "cell", "strap"), COL["board"]), (0, 0, -90)),
                                                       mv(part("Driver board (already on the board)", S("driver", "driver_standoffs"), "#B45309"), (0, 0, -90)),
                                                       mv(M["bscrews"], (0, 0, -150))],
                    "electronics board into the base", "Seen from below. Board top face onto the standoff ends; four M4 x 8 screws from below. Antenna lead to the module",
                    dict(elev=-35, azim=-60, label_done=False))
    T[9] = lambda: ([M["cover"]], [mv(M["probe"], (0, 0, -60)), mv(M["collar"], (0, 0, 50))],
                    "transducer probe and collar into the cover", "Probe in from outside, face 14.5 mm proud, silicone in the gap; collar over it from inside, bonded with epoxy",
                    dict(elev=30, azim=-60, label_done=True))
    T[10] = lambda: ([M["cover"], M["probe"], M["collar"]], [mv(M["window"], (0, 0, 30)), mv(M["tof_holder"], (0, 0, 55)), mv(M["tof"], (0, 0, 80))],
                     "window, ToF holder and ToF breakout", "Window into the holder with a ring of silicone; holder bonded over the 11 mm hole; breakout in its pocket on two M2 screws",
                     dict(elev=35, azim=-60, label_done=False))
    T[11] = lambda: ([M["cover"], M["probe"], M["collar"], M["window"], M["tof_holder"], M["tof"]], [mv(M["vent"], (0, 0, -40))],
                     "vent into the cover", "Seen from below. In from outside, its nut inside, tightened to the maker's torque",
                     dict(elev=-35, azim=-60, label_done=False))
    unit_top = [plate, base, fix, M["antenna"], boardset, M["bscrews"]]
    coverset = part("Cover with sensors and vent", S("cover", "probe", "collar", "window", "tof_holder", "tof", "vent"), COL["cover"])
    T[12] = lambda: (unit_top, [mv(coverset, (0, 0, -100)), mv(part("Cover screws (4)", C["cover_screws"].shape, COL["screws"]), (0, 0, -170))],
                     "close the cover", "Seen from below. Plug in the transducer and ToF leads, check the gasket, then four cover screws evenly, cross pattern",
                     dict(elev=-25, azim=-55, label_done=False))
    unit = unit_top + [coverset, part("Cover screws", C["cover_screws"].shape, COL["screws"])]
    T[13] = lambda: (unit, [mv(part("Tamper bolts with sealing washers (from above)", S("bolts", "seal_washers"), COL["bolts"]), (0, 0, 60)),
                                       mv(part("Washers and nyloc nuts (from below)", C["nuts"].shape, "#475569"), (0, 0, -50))],
                     "unit onto the bin lid", "Bin lid not drawn: it lies between the bolt heads and the plate. Bolts from above, washers and nuts below",
                     dict(elev=22, azim=-55, label_done=False))
    for n, fn in T.items():
        if only and n not in only:
            continue
        done, new, title, sub, kw = fn()
        out.append(bv.step(done, new, OUT / f"step-{n:02d}.png", f"Step {n}: {title}", subtitle=sub, **kw))
    return out


# ----------------------------------------------------------------- wiring
def wiring():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    fig = plt.figure(figsize=(12, 7.2), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 120); ax.set_ylim(0, 72); ax.set_axis_off()
    INK, MUT = "#111827", "#4B5563"
    ax.text(2, 70, "BinLevel prototype: block-level wiring", fontsize=13, fontweight="bold", color=INK, va="top")
    ax.text(2, 66.6, "Bought breakouts wired on the prototyping board; no circuit board is laid out.\n"
            "Plugs on both sensor leads let the cover come away.", fontsize=8.5, color=MUT, va="top")
    ax.text(2, 1.5, "BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT", fontsize=7, color="#B45309")
    ax.text(118, 1.5, REPO, fontsize=7, color="#0F766E", ha="right", family="monospace")
    import matplotlib.patheffects as pe
    ax.add_patch(FancyBboxPatch((1.5, 13), 85.5, 49, boxstyle="round,pad=0.4", fc="#F8FAFC", ec="#94A3B8", lw=1, ls="--"))
    ax.text(3, 60.8, "On the electronics board, in the enclosure base", fontsize=8, color=MUT, va="top")
    ax.add_patch(FancyBboxPatch((92, 8), 26, 46, boxstyle="round,pad=0.4", fc="#FFF7ED", ec="#D97706", lw=1, ls="--"))
    ax.text(93.5, 52.8, "In the cover", fontsize=8, color=MUT, va="top")

    def blk(x, y, w, h, title, sub, color):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3", fc="white", ec=color, lw=1.8, zorder=4))
        ax.text(x + w / 2, y + h - 1.4, title, ha="center", va="top", fontsize=9, fontweight="bold", color=INK, zorder=5)
        ax.text(x + w / 2, y + h - 4.3, sub, ha="center", va="top", fontsize=7.2, color=MUT, linespacing=1.3, zorder=5)

    def wire(pts, color, lw=2.0, ls="-"):
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=color, lw=lw, ls=ls, solid_capstyle="round", zorder=2,
                path_effects=[pe.Stroke(linewidth=lw + 3, foreground="white"), pe.Normal()])

    def lab(x, y, text, color, ha="left"):
        ax.text(x, y, text, fontsize=7.2, color=color, ha=ha, va="center", zorder=6,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none"))
    RED, BLU, GRY, RF = "#B91C1C", "#1D4ED8", "#6B7280", "#374151"
    blk(3, 44, 17, 11, "C cell, holder", "Li-SOCl2 3.6 V,\n8.5 Ah, strapped", "#C2410C")
    blk(25, 44, 13, 11, "Fuse", "PTC or 0.5 A\nfuse", "#7C3AED")
    blk(43, 44, 16, 11, "3.3 V regulator", "nanopower LDO\nand 1,000 uF", "#16A34A")
    blk(64, 41, 18, 14, "LoRaWAN module", "RAK3172 on its\nbreakout", "#2563EB")
    blk(3, 22, 17, 13, "Board sensors", "accelerometer and\ntemperature breakouts,\nalways powered", "#7C3AED")
    blk(25, 22, 16, 13, "Load switch", "sensor power,\non only when\nmeasuring", "#16A34A")
    blk(64, 22, 18, 13, "Driver board", "ultrasonic,\nunder the board", "#0F766E")
    blk(95, 37, 20, 11, "Transducer probe", "plug on its\nshortened cable", "#0E7490")
    blk(95, 11, 20, 12, "ToF breakout", "6-way lead\nwith a plug", "#7C3AED")
    blk(98, 57, 17, 9, "Antenna", "on the base wall", RF)
    wire([(20, 49.5), (25, 49.5)], RED)
    wire([(38, 49.5), (43, 49.5)], RED)
    wire([(59, 49.5), (64, 49.5)], RED, 1.6); lab(61.5, 52, "3.3 V", RED, "center")
    wire([(40.5, 55), (40.5, 58.5), (70, 58.5), (70, 55)], GRY, 1.0, "--"); lab(55, 58.5, "battery divider to the module's ADC pin", GRY, "center")
    wire([(46, 44), (46, 39.5), (11.5, 39.5), (11.5, 35)], RED, 1.4); lab(28, 39.5, "3.3 V, always on", RED, "center")
    wire([(53, 44), (53, 37), (36, 37), (36, 35)], RED, 1.4); lab(45, 35.6, "3.3 V", RED, "center")
    wire([(64, 46), (62.6, 46), (62.6, 32), (41, 32)], GRY, 1.0); lab(50, 32, "enable", GRY, "center")
    wire([(41, 26), (64, 26)], RED, 1.4); lab(49, 26, "switched 3.3 V", RED, "center")
    wire([(64, 43), (61, 43), (61, 18.5), (11.5, 18.5), (11.5, 22)], BLU, 1.2); lab(30, 18.5, "I2C and wake line, 0.25 mm²", BLU, "center")
    wire([(75, 41), (75, 35)], BLU, 1.2); lab(75.6, 38, "trigger, echo", BLU)
    wire([(33, 22), (33, 15), (95, 15)], RED, 1.2); lab(75, 15, "switched 3.3 V", RED, "center")
    wire([(82, 46), (89, 46), (89, 19), (95, 19)], BLU, 1.2); lab(89.6, 21.5, "I2C,\nXSHUT", BLU)
    wire([(82, 29), (92, 29), (92, 42.5), (95, 42.5)], BLU, 1.6); lab(86, 26.4, "transducer\ncable", BLU, "center")
    wire([(79, 55), (79, 61.5), (98, 61.5)], RF, 1.2); lab(88, 63.6, "RF lead (u.FL)", RF, "center")
    ax.text(3, 9.6, "Safety: keep the cell out of its holder until stop S3 in section 6 of the plan. Never charge, short or heat the cell.",
            fontsize=7.6, color="#B45309", fontweight="bold")
    ax.text(3, 6.2, "Red: power (all from one 3.6 V cell). Blue: signal. Grey: control and sensing. "
            "Board wiring 0.25 mm² (24 AWG), except the thick red cell, fuse and regulator input wires, 0.5 mm² (20 AWG).", fontsize=7.2, color=MUT)
    out = OUT / "wiring.png"
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor="white"); plt.close(fig)
    return out


if __name__ == "__main__":
    args = sys.argv[1:] or ["overview", "sheets", "layouts", "joints", "steps", "wiring"]
    fns = {"overview": overview, "sheets": sheets, "layouts": layouts, "joints": joints, "steps": steps, "wiring": wiring}
    i = 0
    while i < len(args):
        w = args[i]
        nums = []
        while i + 1 < len(args) and args[i + 1].isdigit():
            nums.append(int(args[i + 1])); i += 1
        r = fns[w](nums) if nums else fns[w]()
        print(w, "->", r)
        i += 1
