"""BinLevel general arrangement sheet BNL-DWG-001, Rev P2 (TRL 3).

Run from the repo root:  python cad/src/sheets.py
Writes cad/drawings/BNL-DWG-001.svg, .pdf and .png from the parametric model in
cad/src/model.py with .kit/drawing.py. Dimensions are taken from PARAMS and derived(), so
they follow any parameter change. The concept blueprint in media/ is BNL-DWG-010.
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / ".kit"), str(ROOT / "cad" / "src")]
from drawing import Sheet, _viewbox, _t, M, TB_Y, INK, MUTED  # noqa: E402
from model import PARAMS as P, assembly, derived  # noqa: E402

DATE = "2026-09-25"


def safe_project_views(part, workdir, line_weight=0.35, iso_below=False):
    """Same views as drawing.project_views, but edge by edge, so that a degenerate edge from the
    hidden-line projection is skipped instead of stopping the export."""
    from build123d import ExportSVG, LineType, Unit
    workdir = Path(workdir); workdir.mkdir(parents=True, exist_ok=True)
    bb = part.bounding_box()
    c = bb.center(); d = max(bb.size.X, bb.size.Y, bb.size.Z) * 10
    setups = {"front": ((c.X, c.Y - d, c.Z), (0, 0, 1)), "top": ((c.X, c.Y, c.Z + d), (0, 1, 0)),
              "right": ((c.X + d, c.Y, c.Z), (0, 0, 1)), "iso": ((c.X + d, c.Y - d, c.Z + (-d if iso_below else d) * 0.8), (0, 0, 1))}
    out, skipped = {}, 0
    for name, (origin, up) in setups.items():
        visible, hidden = part.project_to_viewport(origin, up, (c.X, c.Y, c.Z))
        ex = ExportSVG(unit=Unit.MM, line_weight=line_weight)
        ex.add_layer("Visible", line_color=0x111827)
        ex.add_layer("Hidden", line_color=0x6B7280, line_type=LineType.ISO_DASH, line_weight=line_weight / 2)
        for layer, edges in (("Visible", visible), ("Hidden", hidden if name != "iso" else [])):
            for e in edges:
                try:
                    ex.add_shape(e, layer=layer)
                except (AssertionError, ValueError, ZeroDivisionError):
                    skipped += 1
        p = workdir / f"{name}.svg"
        ex.write(str(p))
        out[name] = p
    print(f"projected views; skipped {skipped} degenerate edges")
    return out


def ortho_cells(sheet, views, names=("front", "top", "right")):
    """Repeat Sheet.add_ortho's layout arithmetic to find where each view lands (x, y, w, h)."""
    ax, ay, aw, ah = M + 10, M + 16, 245, TB_Y - M - 20
    gap, lab = 14, 12
    dims = {n: _viewbox(Path(views[n]).read_text())[2:] for n in names}
    fw, fh = dims["front"]; tw, th = dims["top"]; rw, rh = dims["right"]
    k = sheet.scale
    ax += (aw - (k * (max(fw, tw) + rw) + gap)) / 2
    ay += (ah - (k * (th + max(fh, rh)) + gap + 2 * lab)) / 2
    colw = k * max(fw, tw)
    front_y = ay + k * th + lab + gap
    row_h = k * max(fh, rh)
    return {"top": (ax, ay, colw, k * th), "front": (ax, front_y, colw, row_h),
            "right": (ax + colw + gap, front_y, k * rw, row_h)}


def dim_h(x1, x2, y, text):
    a = 1.4
    return [f'<line x1="{x1:.2f}" y1="{y:.2f}" x2="{x2:.2f}" y2="{y:.2f}" stroke="{INK}" stroke-width="0.18"/>',
            f'<path d="M{x1:.2f} {y:.2f} l{a} -0.5 l0 1 Z" fill="{INK}"/>',
            f'<path d="M{x2:.2f} {y:.2f} l{-a} -0.5 l0 1 Z" fill="{INK}"/>',
            _t((x1 + x2) / 2, y - 1.0, text, 2.3, 400, INK, "middle", mono=True)]


def dim_v(x, y1, y2, text, side=-1):
    a = 1.4
    cx, cy = x + side * 1.0, (y1 + y2) / 2
    return [f'<line x1="{x:.2f}" y1="{y1:.2f}" x2="{x:.2f}" y2="{y2:.2f}" stroke="{INK}" stroke-width="0.18"/>',
            f'<path d="M{x:.2f} {y1:.2f} l-0.5 {a} l1 0 Z" fill="{INK}"/>',
            f'<path d="M{x:.2f} {y2:.2f} l-0.5 {-a} l1 0 Z" fill="{INK}"/>',
            f'<g transform="rotate(-90 {cx:.2f} {cy:.2f})">{_t(cx, cy, text, 2.3, 400, INK, "middle", mono=True)}</g>']


def ext(x1, y1, x2, y2):
    return f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{MUTED}" stroke-width="0.13"/>'


def leader(x1, y1, x2, y2, text, anchor="start"):
    return [f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{MUTED}" stroke-width="0.15"/>',
            f'<circle cx="{x1:.2f}" cy="{y1:.2f}" r="0.5" fill="{INK}"/>',
            _t(x2 + (1 if anchor == "start" else -1), y2 + 0.8, text, 2.1, 400, INK, anchor)]


def main():
    D = derived(P)
    work = ROOT / "cad" / "drawings" / "_views"
    asm = assembly()
    views = safe_project_views(asm, work)
    views["iso"] = safe_project_views(assembly(with_lid=False), work / "below", iso_below=True)["iso"]
    bb = asm.bounding_box()
    s = Sheet(project="BinLevel", title="General arrangement, sensor unit under lid", dwg_no="BNL-DWG-001", rev="P2",
              author="Amish Chadha", date=DATE, scale=None, theme="technical",
              material="ABS or PC box; 5052 aluminium bracket; stainless bolts; bought-in parts per bom/bom.csv. PRELIMINARY, NOT FOR FABRICATION",
              revisions=[("P1", "Preliminary GA for TRL 3 (from cad/src/model.py)", DATE, "AC"),
                         ("P2", "2 mm aluminium bracket; mass note (DDR-002)", DATE, "AC")])
    s.add_ortho(views)
    k = s.scale
    c = ortho_cells(s, views)
    L = []
    ew, ed, eh = P["enc"]
    pw, pd = P["plate"]
    bpx, bpy = P["bolt_pitch"]
    lu = D["lid_under"]
    face = -P["us_protrude"]

    # front view (from -Y): X to the right, Z up
    x, y, w, h = c["front"]
    X = lambda mx: x + (mx - bb.min.X) * k
    Z = lambda mz: y + h - (mz - bb.min.Z) * k
    xl = X(bb.min.X) - 6
    L += [ext(X(-pw / 2), Z(lu), xl - 1, Z(lu)), ext(X(P["us_x"] - P["us_d"] / 2), Z(face), xl - 1, Z(face))]
    L += dim_v(xl, Z(lu), Z(face), f"{D['below_lid']:.1f} below lid")
    xr = X(bb.max.X) + 6
    L += [ext(X(ew / 2), Z(eh), xr + 1, Z(eh)), ext(X(ew / 2), Z(0), xr + 1, Z(0))]
    L += dim_v(xr, Z(eh), Z(0), f"{eh:.0f}", side=1)
    zt = Z(bb.max.Z)
    L += dim_h(X(-ew / 2), X(ew / 2), zt - 5, f"{ew:.0f} box")
    L += [ext(X(-ew / 2), Z(eh), X(-ew / 2), zt - 6), ext(X(ew / 2), Z(eh), X(ew / 2), zt - 6)]
    L += dim_h(X(P["us_x"]), X(P["tof_x"]), zt - 11, f"{P['tof_x'] - P['us_x']:.0f} sensor centers")
    L += [ext(X(P["us_x"]), Z(eh), X(P["us_x"]), zt - 12), ext(X(P["tof_x"]), Z(eh), X(P["tof_x"]), zt - 12)]
    L += leader(X(-P["lid_patch"][0] / 2 + 10), Z(lu + P["lid_t"] / 2), X(-P["lid_patch"][0] / 2 + 10) - 2,
                Z(bb.max.Z) - 16, "CONTAINER LID, HDPE (NOT IN BOM)", "end")
    L += leader(X(P["us_x"]), Z(face + 2), X(P["us_x"]) - 12, Z(face) + 5, "3 ULTRASONIC FACE", "end")
    L += leader(X(P["tof_x"]), Z(0.5), X(P["tof_x"]) + 12, Z(face) + 5, "4 TOF WINDOW")

    # top view (from +Z): X to the right, Y up the sheet
    x, y, w, h = c["top"]
    Xt = lambda mx: x + (mx - bb.min.X) * k
    Yt = lambda my: y + h - (my - bb.min.Y) * k
    L += dim_h(Xt(-bpx / 2), Xt(bpx / 2), Yt(bb.max.Y) - 4, f"{bpx:.0f} bolt pitch")
    L += [ext(Xt(-bpx / 2), Yt(bpy / 2), Xt(-bpx / 2), Yt(bb.max.Y) - 5), ext(Xt(bpx / 2), Yt(bpy / 2), Xt(bpx / 2), Yt(bb.max.Y) - 5)]
    L += dim_v(Xt(bb.min.X) - 5, Yt(bpy / 2), Yt(-bpy / 2), f"{bpy:.0f}")
    L += [ext(Xt(-bpx / 2), Yt(bpy / 2), Xt(bb.min.X) - 6, Yt(bpy / 2)), ext(Xt(-bpx / 2), Yt(-bpy / 2), Xt(bb.min.X) - 6, Yt(-bpy / 2))]
    L += leader(Xt(bpx / 2), Yt(bpy / 2), Xt(bb.max.X) + 3, Yt(bb.max.Y) - 1, f"4X M6 TAMPER BOLT, {P['bolt_d'] + 1:.0f} HOLE IN LID")

    # right view (from +X)
    x, y, w, h = c["right"]
    Yr = lambda my: x + (my - bb.min.Y) * k
    Zr = lambda mz: y + h - (mz - bb.min.Z) * k
    zr = Zr(bb.max.Z)
    L += dim_h(Yr(-pd / 2), Yr(pd / 2), zr - 5, f"{pd:.0f} plate")
    L += [ext(Yr(-pd / 2), Zr(lu), Yr(-pd / 2), zr - 6), ext(Yr(pd / 2), Zr(lu), Yr(pd / 2), zr - 6)]
    L += dim_h(Yr(-ed / 2), Yr(ed / 2), zr - 11, f"{ed:.0f} box")
    L += [ext(Yr(-ed / 2), Zr(eh), Yr(-ed / 2), zr - 12), ext(Yr(ed / 2), Zr(eh), Yr(ed / 2), zr - 12)]

    s._layers += L
    s.add_svg(views["iso"], 276, 32, 140, 100, label="Isometric view", sublabel="From below, lid omitted; not to scale")
    s.add_notes("Main dimensions and interfaces (mm)", [
        f"Enclosure IP67 {ew:.0f} x {ed:.0f} x {eh:.0f}, wall {P['enc_wall']}; cover split {P['split_z']:.0f} above base",
        f"Bracket {pw:.0f} x {pd:.0f} x {P['plate_t']} 5052 aluminium, end tabs {P['tab'][0]:.0f} x {P['tab'][1]:.0f}",
        f"4 x M6 x {P['bolt_len']:.0f} tamper bolts on {bpx:.0f} x {bpy:.0f}; 18 washers; lid {P['lid_t']:.0f} HDPE",
        f"Envelope below lid {D['footprint'][0]:.0f} x {D['footprint'][1]:.0f} x {D['below_lid']:.1f} (R16: 160 x 90 x 100)",
        f"Transducer {P['us_d']:.0f} dia at X {P['us_x']:.0f}, face {P['us_protrude']} below box; hole {P['us_hole_d']:.0f}",
        f"ToF window {P['win_d']:.0f} dia at X +{P['tof_x']:.0f}; C cell {P['cell_d']} x {P['cell_len']:.0f} strapped",
        f"1,100 L container: face to floor {D['face_to_floor']:,.0f}; mount at lid center",
        "Mass about 334 g with 2 mm aluminium (BNL-CAL-001 v0.2, I1)",
        "Third-angle; front view from -Y; enclosure base at Z = 0",
    ], x=276, y=158, width=146)
    out = s.save(ROOT / "cad" / "drawings" / "BNL-DWG-001")
    shutil.rmtree(work, ignore_errors=True)
    print(f"wrote {out} and .pdf, .png at scale {k:g}")


if __name__ == "__main__":
    main()
