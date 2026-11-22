"""Generate grasp_validation/cad/GRIP-9015_assy-grasp-bench-stage1-2.json: the grasp validation
bench, build stages 1-2 (vault: 05-Wiki/research/2026-11-15-validating-grasping-performance.md,
suite design PROTOCOL.md sec. 4.3, 4.1, 4.6, 4.13).

Stage 1, force chain FC-1: a sensor hub box (ESP32 + 4 x HX711 + INA219, boards slide into rails)
and a calibration kit for the split artifacts (V cradle + mass platform; dead weights are the reference).
Stage 2: DR-1a dovetail receptacle (the GRIP-0002 adapter channel, bolted to 2020 extrusion or a
table) and the IO-1 split artifacts in two shapes of the 30 mm size: block W30 (pinch) and cylinder
D30 (wrap). One TAL220B-format bar cell (55 x 12.7 x 12.7, 2 x M5 at 40 mm pitch; the 1, 5 and
20 kg cells share this body) moves between the jaw pairs with two screws.

Split artifact frame: X = cell axis (fixed end and cable at -X), Z = squeeze axis (gripper jaws press
on the +-Z faces), artifact centred on the origin. Jaw A is screwed to the cell's fixed end from
below, jaw B to its load end from above; each jaw touches the cell only on that end block, and a
1.5 mm pocket keeps it clear elsewhere, so the whole squeeze goes through the cell's bending
beam. Two 4 mm steel dowels (pressed through A, sliding in blind holes in B) carry shear and moment.

Run from the repo root:
    python3 grasp_validation/tools/gen_grasp.py
    tools/build.sh grasp_validation
    python3 grasp_validation/tools/verify_grasp.py
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
import parts  # noqa: E402

VDIR = 'grasp_validation'
OUT = f'{VDIR}/cad/GRIP-9015_assy-grasp-bench-stage1-2.json'
PN = {'aw': 'GRIP-0098', 'bw': 'GRIP-0099', 'ad': 'GRIP-0100', 'bd': 'GRIP-0101', 'cradle': 'GRIP-0102',
      'platform': 'GRIP-0103', 'dr': 'GRIP-0104', 'box': 'GRIP-0105', 'lid': 'GRIP-0106'}

# ----------------------------------------------------------------------------- load cell (TAL220B drawing)
CELL_L, CELL_W, CELL_H = 55.0, 12.7, 12.7
HOLE_X = 20.0               # M5 holes at x = -20 (fixed end, A) and +20 (load end, B): 40 mm pitch
END_BLOCK = 14.0            # clamped end block length (drawing: 14 at each end)
M5_CLR, M5_CB_D, M5_CB_H = 5.5, 10.5, 3.2      # ISO 273 medium; ISO 7380 button head dk 9.5, k 2.75
# ----------------------------------------------------------------------------- split jaws
SIZE = 30.0                 # across the squeeze faces (both shapes)
JAW_L = 86.0                # x +-43: the cell (+-27.5) plus the dowels and a 6 mm cable gap at -X
ZI = CELL_H / 2             # 6.35: jaw inner face = cell face (contact on the end block only)
POCKET = 1.5                # relief over the rest of the cell: room for beam deflection
POCKET_Y = 7.5              # pocket half width (cell 6.35 + 1.15); the jaw rails outside it are the print face
POCKET_END = 31.0           # pocket stops 3.5 mm past the cell end: closed on all sides, prints as a bridge
DOWEL_X, DOWEL_D = 38.0, 4.0
DOWEL_PRESS = 3.8           # 0.2 interference on the diameter (CLAUDE.md press-fit rule)
DOWEL_SLIP = 4.3            # 0.15 per side (printed-pin rule; steel pin in printed hole, NEEDS PRINT TEST)
DOWEL_L = 28.0              # ISO 2338 4 m6 x 28: through A (8.65), gap 12.7, 6.65 into B
DOWEL_B_DEPTH = 7.5         # blind in B (8.65 thick): 1.15 floor, 0.85 end clearance
LABEL_H, LABEL_D = 4.0, 0.6
# ----------------------------------------------------------------------------- calibration kit
CRADLE = dict(x=(-30.0, 30.0), y=(-25.0, 25.0), z=(-30.0, -8.0))   # under the D30 artifact (axis at z 0)
PLAT = dict(x=(-60.0, 60.0), y=(-40.0, 40.0), t=5.0, rail_t=3.0, rail_h=5.0, rail_clr=0.3)
# ----------------------------------------------------------------------------- DR-1a receptacle (GRIP-0069 channel)
DT = dict(len=40.0, bot=34.0, top=28.0, h=6.0, clr=0.2, rail_w=48.0, stop=4.0, floor=5.0, lock_d=4.0)
DR_HOLE_X = 10.0            # 2 x M5 at 20 mm pitch along the channel: one 2020 slot
# ----------------------------------------------------------------------------- hub box
BOX = dict(ix=150.0, iy=90.0, iz=35.0, wall=2.25, floor=2.4, boss_d=8.0, ins_d=4.0, ins_depth=7.0, lid_t=2.4)
RAIL_T, GROOVE, PCB, PCB_CLR, LIP = 3.0, 1.0, 1.6, 0.2, 1.2
# boards: key, width (NEEDS CHECK on your modules), board underside above the floor, centre, long axis, rail length
BOARDS = [
    ('hx1', 21.0, 5.0, (-55.0, -24.0), 'Y', 24.0),
    ('hx2', 21.0, 5.0, (-25.0, -24.0), 'Y', 24.0),
    ('hx3', 21.0, 5.0, (5.0, -24.0), 'Y', 24.0),
    ('hx4', 21.0, 5.0, (35.0, -24.0), 'Y', 24.0),
    ('esp32', 28.0, 10.0, (-45.0, 22.0), 'X', 24.0),     # DevKitC: headers point down, 10 mm under the board
    ('ina219', 20.5, 5.0, (40.0, 22.0), 'X', 24.0),
]
CELL_HOLES_X = [-55.0, -25.0, 5.0, 35.0]   # load-cell cable entries in the -Y wall, one per HX711
# assembly placement (mm): parts spread out so nothing overlaps
POS = {'w30': (0.0, 0.0), 'd30': (0.0, 90.0), 'dr': (150.0, 0.0), 'box': (0.0, -160.0)}

cmds = []
PARTS = []          # (component, PN)
PURCH = []          # (component, PN, description)


def c(command, **params):
    cmds.append({"command": command, "params": params})


def fx(v):
    return round(v, 4)


def comp(key, i=1):
    return f"{parts.fname(PN[key])}_F{i}"


def new_component(name, grounded=False):
    c("component.activate", component=0)
    c("component.create", name=name, activate=True, grounded=grounded)


def box(x, y, z, op, body, name):
    p = dict(length=f"{fx(x[1] - x[0])} mm", width=f"{fx(y[1] - y[0])} mm", height=f"{fx(z[1] - z[0])} mm",
             center=[fx((x[0] + x[1]) / 2), fx((y[0] + y[1]) / 2), fx((z[0] + z[1]) / 2)], operation=op, name=name)
    p.update({"body_name": body} if op == "new" else {"targets": [body]})
    c("solid.box", **p)


def prism_yz(pts, x0, length, op, body, name):
    """Profile in (y, z), extruded along +X from x0."""
    c("sketch.create", plane="YZ", offset=f"{fx(x0)} mm", name=f"{name}_sk")
    c("sketch.line", points=[[fx(y), fx(z)] for y, z in pts], closed=True)
    c("sketch.finish")
    p = dict(distance=f"{fx(length)} mm", operation=op, name=name)
    p.update({"body_name": body} if op == "new" else {"targets": [body]})
    c("solid.extrude", **p)


def cyl(d, base, h, axis, op, body, name):
    p = dict(diameter=d if isinstance(d, str) else f"{fx(d)} mm", height=f"{fx(h)} mm",
             base=[fx(v) for v in base], axis=axis, operation=op, name=name)
    p.update({"body_name": body} if op == "new" else {"targets": [body]})
    c("solid.cylinder", **p)


def label_end(body, text, x_face, y, z, name):
    """Debossed text on an end face (plane x = x_face, outward +X), centred on (y, z)."""
    c("sketch.create", plane="YZ", offset=f"{fx(x_face - LABEL_D)} mm", name=f"{name}_sk")
    c("sketch.text", text=text, at=[fx(y), fx(z - LABEL_H / 2)], height=LABEL_H, align="center")
    c("sketch.finish")
    c("solid.extrude", distance=f"{LABEL_D + 0.1} mm", operation="cut", targets=[body], name=name)


def label_top(body, text, x, y, z_top, h, name):
    c("sketch.create", plane="XY", offset=f"{fx(z_top - LABEL_D)} mm", name=f"{name}_sk")
    c("sketch.text", text=text, at=[fx(x), fx(y - h / 2)], height=h, align="center")
    c("sketch.finish")
    c("solid.extrude", distance=f"{LABEL_D + 0.1} mm", operation="cut", targets=[body], name=name)


# ----------------------------------------------------------------------------- split artifact
def jaw(key, side, shape, ox, oy):
    """side -1 = A (below the cell, fixed end -X), +1 = B (above, load end +X)."""
    name = comp(key)
    new_component(name)
    R = SIZE / 2
    zo = side * R                     # outer extreme (contact apex)
    zi = side * ZI                    # inner face
    zlo, zhi = min(zi, zo), max(zi, zo)
    x = (ox - JAW_L / 2, ox + JAW_L / 2)
    if shape == 'w':
        box(x, (oy - R, oy + R), (zlo, zhi), "new", name, "jaw")
    else:
        cyl(SIZE, (x[0], oy, 0), JAW_L, "X", "new", name, "jaw")
        # keep only this side of the inner face
        if side < 0:
            box((x[0] - 1, x[1] + 1), (oy - R - 1, oy + R + 1), (zi, R + 1), "cut", name, "half")
        else:
            box((x[0] - 1, x[1] + 1), (oy - R - 1, oy + R + 1), (-R - 1, zi), "cut", name, "half")
    # pocket: clear of the cell everywhere except this jaw's end block
    if side < 0:      # A clamps x in [-27.5, -27.5 + 14]; pocket from there to the +X end
        px = (ox - CELL_L / 2 + END_BLOCK, ox + POCKET_END)
        pz = (zi - POCKET, zi + 0.01)
    else:             # B clamps the load end block; pocket from the -X end to it
        px = (ox - POCKET_END, ox + CELL_L / 2 - END_BLOCK)
        pz = (zi - 0.01, zi + POCKET)
    box(px, (oy - POCKET_Y, oy + POCKET_Y), pz, "cut", name, "pocket")
    # M5 clearance + button-head counterbore from the outer face
    hx = ox + side * HOLE_X
    cyl(M5_CLR, (hx, oy, zlo - 1), (zhi - zlo) + 2, "Z", "cut", name, "m5_hole")
    if side < 0:
        cyl(M5_CB_D, (hx, oy, zo - 1), M5_CB_H + 1, "Z", "cut", name, "m5_cbore")
    else:
        cyl(M5_CB_D, (hx, oy, zo - M5_CB_H), M5_CB_H + 1, "Z", "cut", name, "m5_cbore")
    # dowels: through A (press), blind in B (slip)
    for i, dx in enumerate((-DOWEL_X, DOWEL_X)):
        if side < 0:
            cyl(DOWEL_PRESS, (ox + dx, oy, zlo - 1), (zhi - zlo) + 2, "Z", "cut", name, f"dowel_press_{i}")
        else:
            cyl(DOWEL_SLIP, (ox + dx, oy, zi - 0.01), DOWEL_B_DEPTH + 0.01, "Z", "cut", name, f"dowel_slip_{i}")
    tag = ('A' if side < 0 else 'B') + f"{SIZE:.0f}"
    zl = side * (ZI + (R - ZI) / 2)
    label_end(name, tag, x[1], oy, zl, "label")
    PARTS.append((name, PN[key]))
    return name


def cell_and_dowels(tag, ox, oy):
    cname = f"load-cell-TAL220B-{tag}_F1"
    new_component(cname)
    box((ox - CELL_L / 2, ox + CELL_L / 2), (oy - CELL_W / 2, oy + CELL_W / 2), (-CELL_H / 2, CELL_H / 2), "new",
        cname, "cell")
    for i, hx in enumerate((-HOLE_X, HOLE_X)):
        cyl(5.0, (ox + hx, oy, -CELL_H / 2 - 1), CELL_H + 2, "Z", "cut", cname, f"thread_{i}")
    PURCH.append((cname, "TAL220B", "LOAD CELL, BAR, TAL220B FORMAT, 55 X 12.7, 2 X M5 (1/5/20 KG)"))
    for i, dx in enumerate((-DOWEL_X, DOWEL_X)):
        dn = f"dowel-4x28-ISO2338-{tag}_F{i + 1}"
        new_component(dn)
        z0 = -SIZE / 2 + 0.0
        cyl(DOWEL_D - 0.2, (ox + dx, oy, z0), DOWEL_L, "Z", "new", dn, "dowel")   # drawn 0.1/side under size
        PURCH.append((dn, "ISO 2338 4 m6 x 28", "PIN, DOWEL, 4 X 28, STEEL"))


def artifact(shape, ox, oy):
    a = jaw('a' + shape, -1, shape, ox, oy)
    b = jaw('b' + shape, 1, shape, ox, oy)
    cell_and_dowels(f"{shape}30", ox, oy)
    return a, b


# ----------------------------------------------------------------------------- calibration kit
def cradle(ox, oy):
    name = comp('cradle')
    new_component(name)
    cx, cy, cz = CRADLE['x'], CRADLE['y'], CRADLE['z']
    box((ox + cx[0], ox + cx[1]), (oy + cy[0], oy + cy[1]), cz, "new", name, "block")
    # 90 deg V: a cylinder of radius R sits with its axis R*sqrt2 above the vertex (axis at z 0)
    zv = -SIZE / 2 * math.sqrt(2)
    hw = cz[1] + 1 - zv          # half width at the cut top
    prism_yz([(oy, zv), (oy + hw, cz[1] + 1), (oy - hw, cz[1] + 1)], ox + cx[0] - 1, cx[1] - cx[0] + 2, "cut", name, "vee")
    # relief at the V root so the counterbore / vertex never touch
    box((ox + cx[0] - 1, ox + cx[1] + 1), (oy - 1.5, oy + 1.5), (zv - 1.5, zv + 2), "cut", name, "root_relief")
    label_top(name, "D30 CAL", ox, oy + 19, cz[1], 5.0, "label")
    PARTS.append((name, PN['cradle']))


def platform(ox, oy):
    name = comp('platform')
    new_component(name)
    z0 = SIZE / 2
    px, py = PLAT['x'], PLAT['y']
    box((ox + px[0], ox + px[1]), (oy + py[0], oy + py[1]), (z0, z0 + PLAT['t']), "new", name, "plate")
    yr = SIZE / 2 + PLAT['rail_clr']
    for s in (-1, 1):
        y0 = oy + s * yr
        y1 = oy + s * (yr + PLAT['rail_t'])
        box((ox - 40, ox + 40), (min(y0, y1), max(y0, y1)), (z0 - PLAT['rail_h'], z0 + 0.5), "join", name, f"rail_{s}")
    # position marks: three debossed lines across the top at x = -20, 0, +20 (load positions for the 3-point check)
    zt = z0 + PLAT['t']
    for i, mx in enumerate((-20.0, 0.0, 20.0)):
        box((ox + mx - 0.5, ox + mx + 0.5), (oy + py[0] + 5, oy + py[1] - 5), (zt - LABEL_D, zt + 0.1), "cut", name,
            f"mark_{i}")
    label_top(name, "CAL", ox - 40, oy + 25, zt, 6.0, "label")
    PARTS.append((name, PN['platform']))


# ----------------------------------------------------------------------------- DR-1a receptacle
def receptacle(ox, oy):
    name = comp('dr')
    new_component(name)
    T, L, h, clr = DT['floor'], DT['len'], DT['h'], DT['clr']
    x = (ox - L / 2, ox + L / 2 + DT['stop'])
    box(x, (oy - DT['rail_w'] / 2, oy + DT['rail_w'] / 2), (0, T + h), "new", name, "block")
    ch = [(oy - (DT['bot'] / 2 + clr), T), (oy + DT['bot'] / 2 + clr, T), (oy + DT['top'] / 2 + clr, T + h),
          (oy - (DT['top'] / 2 + clr), T + h)]
    prism_yz(ch, ox - L / 2 - 1, L + 1, "cut", name, "channel")
    # thumb-screw lock: M3 insert hole from the +Y rail, as GRIP-0069
    cyl(DT['lock_d'], (ox, oy + DT['top'] / 2 - 0.5, T + h / 2), DT['rail_w'] / 2 - DT['top'] / 2 + 1, "Y", "cut",
        name, "lock_hole")
    for i, dx in enumerate((-DR_HOLE_X, DR_HOLE_X)):
        cyl(M5_CLR, (ox + dx, oy, -1), T + 2, "Z", "cut", name, f"m5_{i}")
        cyl(M5_CB_D, (ox + dx, oy, T - M5_CB_H), M5_CB_H + 1, "Z", "cut", name, f"m5_cbore_{i}")
    label_top(name, "DR1", ox - 6, oy - (DT['rail_w'] / 2 + DT['top'] / 2 + clr) / 2, T + h, 4.0, "label")
    PARTS.append((name, PN['dr']))


# ----------------------------------------------------------------------------- hub box + lid
def hub(ox, oy):
    name = comp('box')
    new_component(name)
    w, f = BOX['wall'], BOX['floor']
    ix, iy, iz = BOX['ix'], BOX['iy'], BOX['iz']
    box((ox - ix / 2 - w, ox + ix / 2 + w), (oy - iy / 2 - w, oy + iy / 2 + w), (0, f + iz), "new", name, "shell")
    box((ox - ix / 2, ox + ix / 2), (oy - iy / 2, oy + iy / 2), (f, f + iz + 1), "cut", name, "cavity")
    bp = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            bx_, by_ = ox + sx * (ix / 2 - BOX['boss_d'] / 2 + 0.3), oy + sy * (iy / 2 - BOX['boss_d'] / 2 + 0.3)
            bp.append((bx_, by_))
            cyl(BOX['boss_d'], (bx_, by_, f - 0.5), iz + 0.5, "Z", "join", name, f"boss_{sx}_{sy}")
            cyl(BOX['ins_d'], (bx_, by_, f + iz - BOX['ins_depth']), BOX['ins_depth'] + 0.01, "Z", "cut", name,
                f"insert_{sx}_{sy}")
    for key, wb, zb, (bx_, by_), ax, rl in BOARDS:
        zb = f + zb
        top = zb + PCB + LIP
        for s in (-1, 1):
            inner = wb / 2 + PCB_CLR - GROOVE           # rail inner face from the board centre line
            a0, a1 = sorted((s * inner, s * (inner + RAIL_T)))
            g0, g1 = sorted((s * inner - 0.01 * s, s * (wb / 2 + PCB_CLR)))
            if ax == 'Y':
                box((ox + bx_ + a0, ox + bx_ + a1), (oy + by_ - rl / 2, oy + by_ + rl / 2), (f - 0.5, top), "join", name,
                    f"rail_{key}_{s}")
                box((ox + bx_ + g0, ox + bx_ + g1), (oy + by_ - rl / 2 - 1, oy + by_ + rl / 2 + 1),
                    (zb - 0.1, zb + PCB + 0.15), "cut", name, f"groove_{key}_{s}")
            else:
                box((ox + bx_ - rl / 2, ox + bx_ + rl / 2), (oy + by_ + a0, oy + by_ + a1), (f - 0.5, top), "join", name,
                    f"rail_{key}_{s}")
                box((ox + bx_ - rl / 2 - 1, ox + bx_ + rl / 2 + 1), (oy + by_ + g0, oy + by_ + g1),
                    (zb - 0.1, zb + PCB + 0.15), "cut", name, f"groove_{key}_{s}")
    # openings: USB at -X (ESP32), supply in/out at +X (INA219), 4 load-cell cables at -Y, bus/IMU at +Y
    esp = next(b for b in BOARDS if b[0] == 'esp32')
    zusb = f + esp[2] + PCB + 1.5
    box((ox - ix / 2 - w - 1, ox - ix / 2 + 0.5), (oy + esp[3][1] - 6, oy + esp[3][1] + 6), (zusb - 4, zusb + 4), "cut",
        name, "usb_port")
    for i, yy in enumerate((22.0, 8.0)):
        cyl(6.0, (ox + ix / 2 - 0.5, oy + yy, f + 15), w + 1.5, "X", "cut", name, f"supply_{i}")
    for i, xx in enumerate(CELL_HOLES_X):
        cyl(6.0, (ox + xx, oy - iy / 2 - w - 1, f + 20), w + 1.5, "Y", "cut", name, f"cell_cable_{i}")
    cyl(8.0, (ox, oy + iy / 2 - 0.5, f + 20), w + 1.5, "Y", "cut", name, "bus_cable")
    PARTS.append((name, PN['box']))

    lid = comp('lid')
    new_component(lid)
    z0 = f + iz + 10.0                 # exploded 10 mm above the rim
    t = BOX['lid_t']
    box((ox - ix / 2 - w, ox + ix / 2 + w), (oy - iy / 2 - w, oy + iy / 2 + w), (z0, z0 + t), "new", lid, "lid")
    for i, (bx_, by_) in enumerate(bp):
        cyl(3.4, (bx_, by_, z0 - 1), t + 2, "Z", "cut", lid, f"screw_{i}")
    label_top(lid, "GRASP HUB", ox, oy, z0 + t, 8.0, "label")
    PARTS.append((lid, PN['lid']))


def build():
    cmds.clear(); PARTS.clear(); PURCH.clear()
    c("document.metadata.set", values={"part_number": "GRIP-9015",
                                       "description": "ASSY, GRASP VALIDATION BENCH, STAGES 1-2",
                                       "revision": "X1", "project": "grasp_validation"})
    for n, e, why in [
        ("cell_l", f"{CELL_L} mm", "TAL220B body length (HTC drawing); 1/5/20 kg cells share it"),
        ("cell_hole_pitch", f"{2 * HOLE_X} mm", "M5 hole pitch on the cell (drawing: 40)"),
        ("artifact_size", f"{SIZE} mm", "distance across the squeeze faces (IO-1 30 mm size)"),
        ("pocket", f"{POCKET} mm", "relief over the bending beam: jaw touches only its own end block"),
        ("dowel_press", f"{DOWEL_PRESS} mm", "4 mm steel dowel pressed through jaw A (0.2 interference, NEEDS PRINT TEST)"),
        ("dowel_slip", f"{DOWEL_SLIP} mm", "4 mm dowel slides in jaw B (0.15 per side, NEEDS PRINT TEST)"),
        ("dt_clr", f"{DT['clr']} mm", "dovetail channel clearance per side, same as GRIP-0069 (keep dt_* equal)"),
        ("pcb_clr", f"{PCB_CLR} mm", "board edge to groove bottom, per side"),
    ]:
        c("parameters.add", name=n, expression=e, comment=why)
    ox, oy = POS['w30']
    a, b = artifact('w', ox, oy)
    c("component.activate", component=0)
    ox2, oy2 = POS['d30']
    artifact('d', ox2, oy2)
    cradle(ox2, oy2)
    platform(ox, oy)
    receptacle(*POS['dr'])
    hub(*POS['box'])
    c("component.activate", component=0)
    reg = parts.register()
    for name, pn in PARTS:
        c("component.metadata.set", component=name, part_number=pn, description=reg[pn]['Description'],
          revision="X1", bom_type="normal")
    for name, pn, d in PURCH:
        c("component.metadata.set", component=name, part_number=pn, description=d, bom_type="purchased")
    for name, pn in PARTS:
        for ext, cmd in (('step', 'file.export_step'), ('stl', 'file.export_stl'), ('3mf', 'file.export_3mf')):
            p = dict(path=f"{VDIR}/exports/{parts.export(pn, 'X1', ext)}", bodies=[name])
            if ext != 'step':
                p["quality"] = "fine"
            c(cmd, **p)
    return cmds


def expected():
    """Analytic volumes (mm3) for the verifier: exact for boxes, cylinders and pockets; labels excluded."""
    R = SIZE / 2
    t = R - ZI
    hole = math.pi / 4 * (M5_CLR ** 2 * (t - M5_CB_H) + M5_CB_D ** 2 * M5_CB_H)
    pk_a = (JAW_L / 2 - (-CELL_L / 2 + END_BLOCK)) * 2 * POCKET_Y * POCKET
    pk_b = (CELL_L / 2 - END_BLOCK + JAW_L / 2) * 2 * POCKET_Y * POCKET
    dp = 2 * math.pi / 4 * DOWEL_PRESS ** 2 * t
    ds = 2 * math.pi / 4 * DOWEL_SLIP ** 2 * DOWEL_B_DEPTH
    w = JAW_L * SIZE * t
    seg = R * R * math.acos(ZI / R) - ZI * math.sqrt(R * R - ZI * ZI)     # circular segment area
    d = JAW_L * seg
    return {'aw': w - hole - pk_a - dp, 'bw': w - hole - pk_b - ds,
            'ad': d - hole - pk_a - dp, 'bd': d - hole - pk_b - ds}


def write(cmd_list):
    for sub in ('cad', 'exports', 'docs'):
        os.makedirs(os.path.join(VDIR, sub), exist_ok=True)
    with open(OUT, 'w') as fh:
        fh.write('[\n' + ',\n'.join(' ' + json.dumps(x, separators=(',', ':')) for x in cmd_list) + '\n]\n')


if __name__ == '__main__':
    write(build())
    print(OUT, len(cmds), 'steps')
    for k, v in expected().items():
        print(k, PN[k], 'expected volume (no label) %.1f mm3' % v)
