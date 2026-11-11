"""Generate finray_tests/cad/GRIP-9010_assy-finray-gripper.json: a hand-driven parallel gripper
with slide-in fin-ray fingers, plus three finger designs to compare.

Frame: X = jaw travel, Y = forward (fingers point +Y), Z = up. Base bottom at z = 0.

Drive: an M6 x 70 hex screw (ISO 4017), held axially in the end wall between its head (in the
knob) and a nyloc nut, runs in an M6 nut trapped in carriage A. Carriage A's rack turns a z18
m1 pinion on a post in the base; the pinion drives carriage B's rack the other way, so both
jaws close symmetrically about x = 0. Pitch 1 mm: one knob turn = 1 mm per jaw.

Fingers: a dovetail tongue on the root slides down into a groove in each jaw post (TPU in PETG).
The left finger is the right one turned over (rotated 180 deg about Y): one STL per design.

Run from the repo root:
    python3 finray_tests/tools/gen_finray.py
    tools/build.sh finray_tests
    python3 finray_tests/tools/verify_finray.py
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
import parts  # noqa: E402

OUT = 'finray_tests/cad/GRIP-9010_assy-finray-gripper.json'
VDIR = 'finray_tests'
PN = {'base': 'GRIP-0052', 'car_a': 'GRIP-0053', 'car_b': 'GRIP-0054', 'pinion': 'GRIP-0055', 'knob': 'GRIP-0056',
      'fa': 'GRIP-0057', 'fb': 'GRIP-0058', 'fc': 'GRIP-0059'}

# ----------------------------------------------------------------------------- layout (mm)
BASE_X = (-72.0, 62.0)
BASE_Y = (-44.0, 16.0)
BASE_T = 4.0
RAIL_Y0, RAIL_H, RAIL_NECK, RAIL_TOP = 0.0, 5.0, 10.0, 14.0   # male dovetail on the base, along X
RAIL_YC = RAIL_Y0 + RAIL_NECK / 2                             # 5.0
SLIDE = 0.25            # dovetail clearance per side (moving parts)
LIFT = 0.3              # carriages / racks / pinion float this far over the base top
Z0 = BASE_T + LIFT      # 4.3: underside of the moving parts
CAR_Y = (-5.0, 15.0)    # carriage footprint in Y; its +Y face is the jaw post face
CAR_L = 22.0            # carriage length in X
POST_Y = CAR_Y[1]       # finger root sits against this face
FLOOR = 2.0             # material between the rail channel and the finger groove floor
ZF0 = BASE_T + RAIL_H + SLIDE + FLOOR      # 11.25: finger bottom = groove floor
H = 20.0                # finger height (extrusion)
ZT = ZF0 + H            # 31.25: carriage top = finger top
XG_MIN, XG_MAX, XG0 = 1.0, 35.0, 20.0      # grip face |x|: closed (2 mm gap), open (70 mm), as built
WALL_X = (-72.0, -66.0)                    # screw end wall
WALL_Z = 24.0
SCREW_Y, SCREW_Z = 4.0, 17.0
SCREW_L, SCREW_D, HEAD_K, HEX_AF = 70.0, 6.0, 4.0, 10.0
NYLOC_M, NUT_M = 8.0, 5.0
KNOB_D, KNOB_T, KNOB_GAP = 32.0, 12.0, 0.3

# gears: pinion z18 m1 on a post at (0, PIN_Y); rack A above it (teeth -Y), rack B below (teeth +Y)
MOD, ZP, BACKLASH = 1.0, 18, 0.3
RP = MOD * ZP / 2                       # 9.0
PIN_Y = -23.0
GEAR_T = 6.0
RACK_BACK = 5.75                        # rack bar depth behind the root line
ARM_Z = (14.6, 18.0)                    # carriage B arm, above the pinion screw head (top 14.1)
POST_D, POST_TOP = 6.0, Z0 + GEAR_T + 0.3  # pinion runs on the post; washer sits on the post top

# finger (local u along the finger from the root face, v across from the grip face)
L, W, TIP_W, ROOT = 60.0, 20.0, 2.0, 5.0
TIP_WALL = 1.5        # solid tip when the walls are too thin to meet before the tip
TONGUE = dict(depth=4.0, neck=8.0, wide=12.0)
FIT = 0.15              # finger tongue in groove, per side (user fit rule 0.10-0.15)
DESIGNS = {
    # key: (ribs, angle deg (+ = rib leans toward the tip going from grip face to back), rib t, grip wall, back wall)
    'fa': (6, 0.0, 0.9, 1.35, 1.35),
    'fb': (5, 15.0, 0.9, 0.9, 0.9),
    'fc': (7, -15.0, 1.35, 1.8, 1.8),
}

cmds = []
PARTS = []          # (component name, PN)


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


def prism_xy(pts, z0, h, op, body, name):
    c("sketch.create", plane="XY", offset=f"{fx(z0)} mm", name=f"{name}_sk")
    c("sketch.line", points=[[fx(x), fx(y)] for x, y in pts], closed=True)
    c("sketch.finish")
    p = dict(distance=f"{fx(h)} mm", operation=op, name=name)
    p.update({"body_name": body} if op == "new" else {"targets": [body]})
    c("solid.extrude", **p)


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


def area(poly):
    return 0.5 * sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]))


# ----------------------------------------------------------------------------- gears
def inv(a):
    return math.tan(a) - a


def gear_points(center, z, phase_deg, mod=MOD, backlash=BACKLASH, n_flank=7):
    """Involute spur gear outline, a tooth centred at phase_deg (same construction as strandbeest gen_dual)."""
    r = mod * z / 2
    rb, ra, rf = r * math.cos(math.radians(20)), r + mod, r - 1.25 * mod
    psi_p = (math.pi * mod / 2 - backlash / 2) / (2 * r)
    a_p = math.radians(20)

    def half(R):
        return psi_p + inv(a_p) - inv(math.acos(rb / max(R, rb)))
    r0 = max(rb, rf)
    radii = [r0 + (ra - r0) * i / (n_flank - 1) for i in range(n_flank)]
    pts = []
    for k in range(z):
        phi = math.radians(phase_deg) + 2 * math.pi * k / z
        flank = ([(rf, half(rb))] if rf < rb else []) + [(R, half(R)) for R in radii]
        pts += [(R, phi - h) for R, h in flank] + [(R, phi + h) for R, h in reversed(flank)]
        h0 = flank[0][1]
        a0, a1 = phi + h0, phi + 2 * math.pi / z - h0
        pts += [(rf, a0 + (a1 - a0) * i / 3) for i in (1, 2)]
    return [(center[0] + R * math.cos(a), center[1] + R * math.sin(a)) for R, a in pts]


def rack_points(x0, x1, y_pitch, teeth_dir):
    """Rack outline in XY: pitch line y_pitch, teeth pointing teeth_dir (+1: +Y, -1: -Y), bar behind.
    Gaps centred on x = k*pi (world, as built): the pinion has teeth at +-90 deg there."""
    p = math.pi * MOD
    s = p / 2 - BACKLASH / 2
    t20 = math.tan(math.radians(20))
    tip, root = y_pitch + teeth_dir * MOD, y_pitch - teeth_dir * 1.25 * MOD
    back = root - teeth_dir * RACK_BACK
    k0, k1 = math.ceil((x0 - p / 2) / p), math.floor((x1 - p / 2) / p)
    prof = [(x0, root)]
    for k in range(k0, k1 + 1):
        xc = p / 2 + k * p                  # tooth centre
        hr, ht = s / 2 + 1.25 * MOD * t20, s / 2 - MOD * t20
        if xc - hr < x0 + 0.5 or xc + hr > x1 - 0.5:
            continue
        prof += [(xc - hr, root), (xc - ht, tip), (xc + ht, tip), (xc + hr, root)]
    prof += [(x1, root), (x1, back), (x0, back)]
    return prof


# ----------------------------------------------------------------------------- finger
def finger_local(key):
    """Outline (u, v), tongue (u, v) and cell polygons (u, v) of one fin-ray design."""
    n, ang, rt, tg, tb = DESIGNS[key]
    m = (W - TIP_W) / L                        # back face slope
    beta = math.atan(m)
    kb = W - tb / math.cos(beta)               # back inner line: v = kb - m u
    outline = [(0, 0), (L, 0), (L, TIP_W), (0, W)]
    tc = W / 2
    tongue = [(-TONGUE['depth'], tc - TONGUE['wide'] / 2), (-TONGUE['depth'], tc + TONGUE['wide'] / 2),
              (0.5, tc + TONGUE['neck'] / 2 - 0.25), (0.5, tc - TONGUE['neck'] / 2 + 0.25)]
    a = math.radians(ang)
    d = (math.sin(a), math.cos(a))             # rib direction, grip -> back
    nrm = (math.cos(a), -math.sin(a))          # rib normal (toward +u)
    u_meet = (kb - tg) / m                     # where the inner lines meet
    u_end = min(u_meet, L - TIP_WALL)          # thin walls meet past the tip: close with a tip wall
    us = [ROOT + (u_end - ROOT) * i / (n + 1) for i in range(1, n + 1)]

    def on_grip(p0):                           # line p0 + t d meets v = tg
        t = (tg - p0[1]) / d[1]
        return (p0[0] + t * d[0], tg)

    def on_back(p0):                           # meets v = kb - m u
        t = (kb - m * p0[0] - p0[1]) / (d[1] + m * d[0])
        return (p0[0] + t * d[0], p0[1] + t * d[1])

    edges = []                                  # (minus edge point, plus edge point) per rib
    for u in us:
        p = (u, tg)
        edges.append(((p[0] - nrm[0] * rt / 2, p[1] - nrm[1] * rt / 2), (p[0] + nrm[0] * rt / 2, p[1] + nrm[1] * rt / 2)))
    cells = []
    prev = None
    for em, ep in edges:
        if prev is None:
            q = [(ROOT, tg), on_grip(em), on_back(em), (ROOT, kb - m * ROOT)]
        else:
            q = [on_grip(prev), on_grip(em), on_back(em), on_back(prev)]
        cells.append(q)
        prev = ep
    if u_meet <= u_end + 1e-9:
        cells.append([on_grip(prev), (u_end, tg), on_back(prev)])
    else:
        cells.append([on_grip(prev), (u_end, tg), (u_end, kb - m * u_end), on_back(prev)])
    for q in cells:
        assert area(q) > 1.0, (key, q)
        assert all(-1e-6 <= v <= W and ROOT - 1e-6 <= u <= L for u, v in q), (key, q)
    return outline, tongue, cells


def to_world(pts, side, xg, dy=0.0):
    """side +1: right jaw (B), grip face at x = +xg facing -X. side -1: left jaw (A), mirrored."""
    return [(side * (xg + v), POST_Y + dy + u) for u, v in pts]


def finger_volume(key):
    outline, tongue, cells = finger_local(key)
    tc, d = W / 2, TONGUE['depth']
    tongue_in = [(-d, tc - TONGUE['wide'] / 2), (-d, tc + TONGUE['wide'] / 2), (0, tc + TONGUE['neck'] / 2), (0, tc - TONGUE['neck'] / 2)]
    a = abs(area(outline)) + abs(area(tongue_in)) - sum(abs(area(q)) for q in cells)
    return a * H


def build_finger(key, i, side, xg, dy=0.0):
    name = comp(key, i)
    new_component(name)
    outline, tongue, cells = finger_local(key)
    prism_xy(to_world(outline, side, xg, dy), ZF0, H, "new", name, f"{name}_body")
    prism_xy(to_world(tongue, side, xg, dy), ZF0, H, "join", name, f"{name}_tongue")
    for j, q in enumerate(cells):
        prism_xy(to_world(q, side, xg, dy), ZF0 - 1, H + 2, "cut", name, f"{name}_cell{j}")
    PARTS.append((name, PN[key]))
    return name


# ----------------------------------------------------------------------------- build
def build():
    cmds.clear()
    PARTS.clear()
    c("document.metadata.set", values={"part_number": "GRIP-9010",
                                       "description": "ASSY, GRIPPER, THUMB SCREW, SLIDE-IN FIN RAY FINGERS",
                                       "revision": "X1", "project": "finray_tests"})
    for name, expr, why in [
        ("slide_clr", f"{SLIDE} mm", "dovetail rail clearance per side (moving parts)"),
        ("finger_fit", f"{FIT} mm", "finger tongue in jaw groove, per side (user fit rule 0.10-0.15, NEEDS PRINT TEST)"),
        ("pin_fit", "0.15 mm", "pinion bore on the base post, per side"),
        ("screw_hole", "6.6 mm", "M6 clearance, ISO 273 medium"),
        ("tap_m3", "2.5 mm", "M3 thread-forming hole in the pinion post"),
        ("nut_af", "10.3 mm", "M6 nut trap across flats (nut 10 AF)"),
        ("hex_pocket", "10.1 mm", "M6 hex head press-fit pocket in the knob (head 10 AF, NEEDS PRINT TEST)"),
    ]:
        c("parameters.add", name=name, expression=expr, comment=why)

    # ---------------------------------------------------------------- base GRIP-0052
    b = comp('base')
    c("component.create", name=b, activate=True, grounded=True)
    box(BASE_X, BASE_Y, (0, BASE_T), "new", b, "plate")
    box(WALL_X, CAR_Y, (BASE_T - 0.5, WALL_Z), "join", b, "screw_wall")
    sl = RAIL_H * (RAIL_TOP - RAIL_NECK) / 2 / RAIL_H       # flank run per side (2 mm)
    e = sl * 0.5 / RAIL_H                                  # flank continued 0.5 into the plate
    rail = [(RAIL_Y0 + e, BASE_T - 0.5), (RAIL_Y0 + RAIL_NECK - e, BASE_T - 0.5), (RAIL_Y0 + RAIL_NECK + sl, BASE_T + RAIL_H),
            (RAIL_Y0 - sl, BASE_T + RAIL_H)]
    prism_yz(rail, WALL_X[1] - 0.5, BASE_X[1] - WALL_X[1] + 0.5, "join", b, "rail")
    cyl("screw_hole", (WALL_X[0] - 1, SCREW_Y, SCREW_Z), WALL_X[1] - WALL_X[0] + 2, "X", "cut", b, "screw_bore")
    cyl(f"{POST_D} mm", (0, PIN_Y, BASE_T - 0.5), POST_TOP - BASE_T + 0.5, "Z", "join", b, "pinion_post")
    cyl("9 mm", (0, PIN_Y, BASE_T - 0.5), LIFT + 0.5, "Z", "join", b, "post_collar")
    cyl("tap_m3", (0, PIN_Y, POST_TOP - 9), 9.5, "Z", "cut", b, "post_tap")
    PARTS.append((b, PN['base']))

    # ---------------------------------------------------------------- carriages
    off = SLIDE / math.cos(math.atan(sl / RAIL_H))          # flank offset, measured along Y

    def flank(z, s):                                         # rail flank grown by SLIDE; s -1 left, +1 right
        return RAIL_YC + s * (RAIL_NECK / 2 + sl * (z - BASE_T) / RAIL_H + off)
    zc0, zc1 = Z0 - 1, BASE_T + RAIL_H + SLIDE
    chan = [(flank(zc0, -1), zc0), (flank(zc0, 1), zc0), (flank(zc1, 1), zc1), (flank(zc1, -1), zc1)]
    tc = W / 2
    slope = (TONGUE['wide'] - TONGUE['neck']) / 2 / TONGUE['depth']
    tw = TONGUE['wide'] / 2 + 0.2 * slope + FIT * math.hypot(1, slope)   # groove 0.2 deeper than the tongue
    groove = [(-TONGUE['depth'] - 0.2, tc - tw), (-TONGUE['depth'] - 0.2, tc + tw),
              (0.5, tc + TONGUE['neck'] / 2 - 0.5 * slope + FIT * math.hypot(1, slope)),
              (0.5, tc - TONGUE['neck'] / 2 + 0.5 * slope - FIT * math.hypot(1, slope))]
    for key, side in (('car_a', -1), ('car_b', 1)):
        name = comp(key)
        new_component(name)
        x0, x1 = sorted((side * XG0, side * (XG0 + CAR_L)))
        box((x0, x1), CAR_Y, (Z0, ZT), "new", name, f"{key}_block")
        prism_yz(chan, x0 - 1, CAR_L + 2, "cut", name, f"{key}_rail_channel")
        prism_xy(to_world(groove, side, XG0), ZF0, H + 1, "cut", name, f"{key}_finger_groove")
        if key == 'car_a':
            rack = rack_points(x0, -XG0 + 45, PIN_Y + RP, -1)
            prism_xy(rack, Z0, GEAR_T, "join", name, "rack_a")
            box((x0, x1), (PIN_Y + RP + 1.25 + 2, CAR_Y[0] + 0.5), (Z0, Z0 + GEAR_T), "join", name, "rack_a_web")
            cyl("screw_hole", (x0 - 1, SCREW_Y, SCREW_Z), CAR_L + 2, "X", "cut", name, "screw_bore")
            xm = (x0 + x1) / 2
            box((xm - (NUT_M + 0.3) / 2, xm + (NUT_M + 0.3) / 2), (SCREW_Y - 10.3 / 2, SCREW_Y + 10.3 / 2),
                (SCREW_Z - HEX_AF / math.sqrt(3) - 0.15, ZT + 1), "cut", name, "nut_trap")
        else:
            rack = rack_points(XG0 - 45, x1, PIN_Y - RP, 1)
            prism_xy(rack, Z0, GEAR_T, "join", name, "rack_b")
            yb = PIN_Y - RP - 1.25 - RACK_BACK
            box((x0, x1), (yb, PIN_Y - RP - 2.0), (Z0, ARM_Z[1]), "join", name, "rack_b_riser")
            box((x0, x1), (yb, CAR_Y[0] + 0.5), ARM_Z, "join", name, "arm_b")
        PARTS.append((name, PN[key]))

    # ---------------------------------------------------------------- pinion GRIP-0055
    pn_ = comp('pinion')
    new_component(pn_)
    prism_xy(gear_points((0, PIN_Y), ZP, 90.0), Z0, GEAR_T, "new", pn_, "pinion_gear")
    cyl(f"{POST_D + 0.3} mm", (0, PIN_Y, Z0 - 1), GEAR_T + 2, "Z", "cut", pn_, "pinion_bore")
    PARTS.append((pn_, PN['pinion']))

    # ---------------------------------------------------------------- knob GRIP-0056 (+ purchased screw, nuts)
    kn = comp('knob')
    new_component(kn)
    kx0 = WALL_X[0] - KNOB_GAP - KNOB_T
    scal = []
    for k in range(240):
        a = 2 * math.pi * k / 240
        r = KNOB_D / 2 - 0.8 * (0.5 + 0.5 * math.cos(24 * a))
        scal.append((SCREW_Y + r * math.cos(a), SCREW_Z + r * math.sin(a)))
    prism_yz(scal, kx0, KNOB_T, "new", kn, "knob_body")
    hexp = [(SCREW_Y + 10.1 / math.sqrt(3) * math.cos(math.pi / 3 * k), SCREW_Z + 10.1 / math.sqrt(3) * math.sin(math.pi / 3 * k))
            for k in range(6)]
    prism_yz(hexp, WALL_X[0] - KNOB_GAP - HEAD_K - 0.2, HEAD_K + 1, "cut", kn, "hex_pocket")
    cyl("screw_hole", (kx0 - 1, SCREW_Y, SCREW_Z), KNOB_T + 2, "X", "cut", kn, "knob_bore")
    PARTS.append((kn, PN['knob']))

    hx = lambda af: [(SCREW_Y + af / math.sqrt(3) * math.cos(math.pi / 3 * k + math.pi / 6),  # noqa: E731
                      SCREW_Z + af / math.sqrt(3) * math.sin(math.pi / 3 * k + math.pi / 6)) for k in range(6)]
    purchased = []
    sc = "M6x70-ISO4017_F1"
    new_component(sc)
    head_x1 = WALL_X[0] - KNOB_GAP
    head = [(SCREW_Y + HEX_AF / math.sqrt(3) * math.cos(math.pi / 3 * k), SCREW_Z + HEX_AF / math.sqrt(3) * math.sin(math.pi / 3 * k))
            for k in range(6)]
    prism_yz(head, head_x1 - HEAD_K, HEAD_K, "new", sc, "screw_head")
    cyl("5.8 mm", (head_x1 - 0.01, SCREW_Y, SCREW_Z), SCREW_L + 0.01, "X", "join", sc, "screw_shank")
    purchased.append((sc, "ISO 4017 M6x70", "SCREW, HEX, M6 X 70, FULL THREAD"))
    ny = "M6-nyloc-DIN985_F1"
    new_component(ny)
    prism_yz(hx(HEX_AF), WALL_X[1], NYLOC_M, "new", ny, "nyloc")
    cyl("6 mm", (WALL_X[1] - 1, SCREW_Y, SCREW_Z), NYLOC_M + 2, "X", "cut", ny, "nyloc_bore")
    purchased.append((ny, "DIN 985 M6", "NUT, NYLOC, M6"))
    nt = "M6-nut-ISO4032_F1"
    new_component(nt)
    xa0, xa1 = -XG0 - CAR_L, -XG0
    xm = (xa0 + xa1) / 2
    prism_yz(hx(HEX_AF), xm - NUT_M / 2, NUT_M, "new", nt, "nut")
    cyl("6 mm", (xm - NUT_M / 2 - 1, SCREW_Y, SCREW_Z), NUT_M + 2, "X", "cut", nt, "nut_bore")
    purchased.append((nt, "ISO 4032 M6", "NUT, HEX, M6"))

    # ---------------------------------------------------------------- fingers: A mounted, B and C parked in front
    mounted = (build_finger('fa', 1, -1, XG0), build_finger('fa', 2, 1, XG0))
    parked = []
    for key, dy in (('fb', 75.0), ('fc', 150.0)):
        parked += [build_finger(key, 1, -1, XG0, dy), build_finger(key, 2, 1, XG0, dy)]

    # ---------------------------------------------------------------- joints
    c("component.activate", component=0)
    o = lambda n: f"{n}:1"  # noqa: E731
    lim_a = [[XG0 - XG_MAX, XG0 - XG_MIN]]           # carriage A moves +X to close
    c("joint.as_built", type="slider", a=o(b), b=o(comp('car_a')), at={"point": [0, RAIL_YC, BASE_T], "z": [1, 0, 0]},
      name="S_A", limits=lim_a)
    c("joint.as_built", type="slider", a=o(b), b=o(comp('car_b')), at={"point": [0, RAIL_YC, BASE_T], "z": [1, 0, 0]},
      name="S_B", limits=[[XG_MIN - XG0, XG_MAX - XG0]])
    c("joint.as_built", type="revolute", a=o(b), b=o(pn_), at={"point": [0, PIN_Y, Z0], "z": [0, 0, 1]}, name="R_pinion")
    c("joint.as_built", type="revolute", a=o(b), b=o(kn), at={"point": [WALL_X[0], SCREW_Y, SCREW_Z], "z": [1, 0, 0]},
      name="R_knob")
    c("joint.as_built", type="rigid", a=o(kn), b=o(sc), name="screw_in_knob")
    c("joint.as_built", type="rigid", a=o(kn), b=o(ny), name="nyloc_on_screw")
    c("joint.as_built", type="rigid", a=o(comp('car_a')), b=o(nt), name="nut_in_carriage")
    c("joint.as_built", type="rigid", a=o(comp('car_a')), b=o(mounted[0]), name="finger_A")
    c("joint.as_built", type="rigid", a=o(comp('car_b')), b=o(mounted[1]), name="finger_B")
    for n in parked:
        c("joint.as_built", type="rigid", a=o(b), b=o(n), name=f"park_{n}")
    c("joint.screw", a="R_knob", b="S_A", pitch="1 mm")
    # rack A runs above the pinion, rack B below: A moving +X turns the pinion clockwise (seen from +Z),
    # which moves B -X. Signs checked by the mesh test in verify_finray.py (wrong sign = teeth overlap)
    c("joint.rack_pinion", a="S_A", b="R_pinion", radius=RP, reverse=True)
    c("joint.rack_pinion", a="R_pinion", b="S_B", radius=RP)

    # ---------------------------------------------------------------- metadata + exports
    reg = parts.register()
    for name, pn in PARTS:
        c("component.metadata.set", component=name, part_number=pn, description=reg[pn]['Description'],
          revision="X1", bom_type="normal")
    for name, pn, d in purchased:
        c("component.metadata.set", component=name, part_number=pn, description=d, bom_type="purchased")
    done = set()
    for name, pn in PARTS:
        if pn in done:
            continue
        done.add(pn)
        for ext, cmd in (('step', 'file.export_step'), ('stl', 'file.export_stl'), ('3mf', 'file.export_3mf')):
            p = dict(path=f"{VDIR}/exports/{parts.export(pn, 'X1', ext)}", bodies=[name])
            if ext != 'step':
                p["quality"] = "fine"
            c(cmd, **p)
    return cmds


def write(cmd_list):
    for sub in ('cad', 'exports', 'docs'):
        os.makedirs(os.path.join(VDIR, sub), exist_ok=True)
    with open(OUT, 'w') as fh:
        fh.write('[\n' + ',\n'.join(' ' + json.dumps(x, separators=(',', ':')) for x in cmd_list) + '\n]\n')


if __name__ == '__main__':
    write(build())
    print(OUT, len(cmds), 'steps')
    for k in DESIGNS:
        print(k, PN[k], 'expected volume %.1f mm3' % finger_volume(k))
