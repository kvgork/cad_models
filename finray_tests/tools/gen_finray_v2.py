"""Generate the finray_tests v2 rigs: one base with swappable actuation modules, fingers with an open root.

Variants (python3 finray_tests/tools/gen_finray_v2.py [parallel|pull|csocket|all]):
  parallel  finray_tests/v2_multi-actuation/cad/GRIP-9017_assy-finray-multi-actuation.json (committed):
            parallel module mounted, pull module parked behind the base.
  pull      the same rig with the pull module mounted and the parallel holders parked. Check variant only
            (no exports); verify_finray_v2.py builds it into its scratch folder.
  csocket   finray_tests/v2b_c-socket/cad/GRIP-9018_assy-finray-c-socket.json (committed): the parallel rig with
            C-socket holders and fingers with Ø5 corner cylinders, to test that root as well.

Frame as v1 (gen_finray.py): X = jaw travel, Y = forward (fingers point +Y), Z = up, base bottom at z = 0.
The drive is v1's: an M6 thumb screw moves carriage A, a z18 pinion mirrors it to carriage B (1 mm per turn).
New in v2: the carriages carry no finger. Each has two M3 heat-set inserts on top, and a module is screwed on:

  parallel  a holder (one part, both sides) clamps the finger root between a floor and a cap; two snap pins go
            through the floor, the finger's corner bosses and the cap. The finger moves with the carriage.
  pull      a bracket screwed to the base (slots, M3 nuts in the base) pins the OUTER root corner; a slider
            guided in the bracket pins the INNER corner (its pin hole is slotted in X so the root can deform).
            A cam plate on the carriage has a 45 deg slot over the slider's drive boss, so closing the knob by
            1 mm pulls the inner corner 1 mm back along the finger (0..6 mm, slot ends = stops).

Fingers: the five v1 rib layouts (DESIGNS in gen_finray.py), but the 5 mm solid root block is gone: the two
flanks end in corner bosses (Ø7, pin hole Ø3.4) joined only through the ribs, so pulling one corner bends the
fin ray instead of tilting it. Stage 1 (user 2026-11-17): finger A only, parallel + pull modules.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
import gen_finray as g  # noqa: E402
import parts  # noqa: E402

c, fx, box, cyl, prism_xy, prism_yz, new_component = g.c, g.fx, g.box, g.cyl, g.prism_xy, g.prism_yz, g.new_component

VDIR = {'parallel': 'finray_tests/v2_multi-actuation', 'pull': 'finray_tests/v2_multi-actuation',
        'csocket': 'finray_tests/v2b_c-socket'}
ASSY = {'parallel': ('GRIP-9017', 'ASSY, FINRAY TEST RIG V2, SWAPPABLE ACTUATION MODULES'),
        'pull': ('GRIP-9017', 'ASSY, FINRAY TEST RIG V2, PULL MODULE MOUNTED (CHECK VARIANT)'),
        'csocket': ('GRIP-9018', 'ASSY, FINRAY TEST RIG V2B, PARALLEL, C-SOCKET FINGER ROOTS')}
PN = {'base': 'GRIP-0124', 'car_a': 'GRIP-0125', 'car_b': 'GRIP-0126', 'pinion': 'GRIP-0055', 'knob': 'GRIP-0056',
      'hold': 'GRIP-0127', 'br_l': 'GRIP-0128', 'br_r': 'GRIP-0129', 'slider': 'GRIP-0130',
      'cam_l': 'GRIP-0131', 'cam_r': 'GRIP-0132', 'finger': 'GRIP-0133', 'pin': 'GRIP-0134',
      'finger_c': 'GRIP-0135', 'hold_c': 'GRIP-0136'}

# ----------------------------------------------------------------------------- layout (mm)
BASE_X, BASE_Y, BASE_T = g.BASE_X, (-44.0, 48.0), g.BASE_T
XG0 = g.XG0                    # 20: grip-face |x| as built
XG_MIN, XG_MAX = g.XG_MIN, g.XG_MAX
XG_MIN_C = 5.0                 # C-socket holders overhang the grip face by 4 mm: closest gap 10 mm
ZF0, H = g.ZF0, g.H            # finger z 11.25 .. 31.25 (as v1: same grip height)
ZC = ZF0 + H + 0.2             # 31.45: carriage top = cap underside
HEAD_H_ = 3.0                  # snap-pin head height (see PIN constants below)
CAP = (ZC, ZC + 3.0)           # 31.45 .. 34.45
FLOOR = (ZF0 - 3.0, ZF0 - 0.2)  # 8.25 .. 11.05
Y_R = 40.0                     # finger root face (u = 0)
UC = -3.9                      # boss centre u (behind the root face; the first cell starts at u = -0.3)
YB = Y_R + UC                  # 36.1
BOSS_R, PIN_HOLE, NECK = 3.5, 3.4, 1.8
VB = (BOSS_R, g.W - BOSS_R)    # boss centre v: flush with the grip face / the back face at the root
INS = (3.0, 17.0)              # module screws: v of the two carriage inserts (y = INS_Y)
INS_Y, INS_D, INS_DEPTH = 5.0, 4.0, 6.0
CAM_Z0 = CAP[1] + HEAD_H_ + 0.3   # 37.75: cam plate underside, 0.3 over the pin heads (heads pass under it)
PULL_MAX = 6.0                 # inner-corner pull at full stroke (slot ends at -1 and +7)
SL_Y0 = 24.0                   # slider rear face at zero pull
DRIVE = (3.5, 27.0)            # slider drive boss (v, y) at zero pull
NUT_Y, NUT_X = 19.0, (15.0, 25.0, 35.0, 45.0, 55.0)   # M3 nut pockets under the base (each side)
BR_SCREW = (11.0, 21.0)        # bracket screw slot centres (v), slots +-5 mm along X
PARK_DY = -110.0               # unused module parked behind the base

# C-socket root (v2b): Ø5 cylinders on the neck mid-lines, in C-sockets open toward the finger
CR, C_UC, C_PLAY, C_MOUTH = 2.5, -3.0, 0.15, 3.5
C_VC = (NECK / 2, g.W - NECK / 2)

# snap pin (as strandbeest v8): shank 3.1 in Ø3.4 holes, barb 4.0 / 2.8, head Ø5.5 x 3
PIN_D, HEAD_D, HEAD_H = PIN_HOLE - 0.3, 5.5, 3.0
BARB_D, BARB_TIP, BARB_H, BARB_UP, SLOT_W, SLOT_DOWN, FLAT = 4.0, 2.8, 1.5, 0.2, 0.8, 4.0, 0.25

PARTS = []        # (component, PN)
PURCHASED = []    # (component, PN, description)


def comp(key, inst):
    return f"{parts.fname(PN[key])}_{inst}"


def mx(pts, side):
    return [(side * x, y) for x, y in pts]


def bx(side, x, y, z, op, body, name):
    """box given in right-side coordinates (x > 0), mirrored for side -1."""
    xs = sorted((side * x[0], side * x[1]))
    box(xs, y, z, op, body, name)


def cylz(side, d, xy, z0, h, op, body, name):
    cyl(d if isinstance(d, str) else f"{fx(d)} mm", (side * xy[0], xy[1], z0), h, "Z", op, body, name)


def slot_z(side, p0, p1, w, z, op, body, name):
    """Stadium (p0 -> p1, width w) in right-side coordinates, as a prism z[0]..z[1]."""
    (x0, y0), (x1, y1) = p0, p1
    a = math.atan2(y1 - y0, x1 - x0)
    pts = []
    for (cx_, cy_), a0 in (((x1, y1), a - math.pi / 2), ((x0, y0), a + math.pi / 2)):
        for k in range(13):
            t = a0 + math.pi * k / 12
            pts.append((cx_ + w / 2 * math.cos(t), cy_ + w / 2 * math.sin(t)))
    prism_xy(mx(pts, side), z[0], z[1] - z[0], op, body, name)


# ----------------------------------------------------------------------------- fingers
def finger_profile(key, root):
    """Outline, extra joins (polygons) and cells in (u, v) for the open-root finger; root 'pin' or 'c'."""
    n, ang, rt, tg, tb = g.DESIGNS[key]
    outline, _tongue, cells = g.finger_local(key)
    m = (g.W - g.TIP_W) / g.L
    kb = g.W - tb / math.cos(math.atan(m))
    cells = [list(q) for q in cells]
    u0 = -0.3 if root == 'pin' else -0.6         # first cell opened past the root face: no root block
    cells[0][0] = (u0, tg)
    cells[0][3] = (u0, kb - m * u0)
    uc = UC if root == 'pin' else C_UC
    necks = [[(uc, 0.0), (0.5, 0.0), (0.5, NECK), (uc, NECK)],
             [(uc, g.W - NECK), (0.3, g.W - NECK), (0.3, g.W - m * 0.3), (uc, g.W)]]
    return outline, necks, cells


def finger_world(pts, side, xg):
    return [(side * (xg + v), Y_R + u) for u, v in pts]


def build_finger(key, inst, side, xg, root='pin', dy=0.0):
    pk = 'finger' if root == 'pin' else 'finger_c'
    name = comp(pk, inst)
    new_component(name)
    outline, necks, cells = finger_profile(key, root)
    w = lambda pts: [(x, y + dy) for x, y in finger_world(pts, side, xg)]  # noqa: E731
    prism_xy(w(outline), ZF0, H, "new", name, f"{name}_body")
    for j, q in enumerate(necks):
        prism_xy(w(q), ZF0, H, "join", name, f"{name}_neck{j}")
    if root == 'pin':
        for j, v in enumerate(VB):
            cyl(f"{2 * BOSS_R} mm", (side * (xg + v), YB + dy, ZF0), H, "Z", "join", name, f"{name}_boss{j}")
    else:
        for j, v in enumerate(C_VC):
            cyl(f"{2 * CR} mm", (side * (xg + v), Y_R + C_UC + dy, ZF0), H, "Z", "join", name, f"{name}_cyl{j}")
    for j, q in enumerate(cells):
        prism_xy(w(q), ZF0 - 1, H + 2, "cut", name, f"{name}_cell{j}")
    if root == 'pin':
        for j, v in enumerate(VB):
            cyl("pin_hole", (side * (xg + v), YB + dy, ZF0 - 1), H + 2, "Z", "cut", name, f"{name}_pinhole{j}")
    PARTS.append((name, PN[pk]))
    return name


def snap_pin(inst, xy, z_head_seat, z_far):
    """One-piece snap pin pointing down: head on z_head_seat (cap top), barb shoulder BARB_UP below z_far."""
    name = comp('pin', inst)
    new_component(name)
    x, y = xy
    z_sh = z_far - BARB_UP
    tip = z_sh - BARB_H
    cyl("head_d", (x, y, z_head_seat), HEAD_H, "Z", "new", name, f"{name}_head")
    cyl("pin_d", (x, y, z_sh - 0.3), z_head_seat - z_sh + 0.31, "Z", "join", name, f"{name}_shank")
    c("solid.cone", diameter=f"{BARB_TIP} mm", top_diameter=f"{BARB_D} mm", height=f"{BARB_H} mm",
      base=[fx(x), fx(y), fx(tip)], operation="join", targets=[name], name=f"{name}_barb")
    for s_, tag in ((-1, 'flat'), (1, 'flat2')):      # two flats (+-y), whole pin as v8: prints lying on one
        box((x - 10, x + 10), sorted((y + s_ * (PIN_D / 2 - FLAT), y + s_ * 10)), (tip - 1, z_head_seat + HEAD_H + 1),
            "cut", name, f"{name}_{tag}")
    sl = BARB_H + BARB_UP + SLOT_DOWN
    box((x - SLOT_W / 2, x + SLOT_W / 2), (y - 10, y + 10), (tip - 1, tip + sl), "cut", name, f"{name}_slot")
    PARTS.append((name, PN['pin']))
    return name


# ----------------------------------------------------------------------------- base + drive (v1 + module mounts)
def build_base():
    b = comp('base', 'F1')
    c("component.create", name=b, activate=True, grounded=True)
    box(BASE_X, BASE_Y, (0, BASE_T), "new", b, "plate")
    box(g.WALL_X, g.CAR_Y, (BASE_T - 0.5, g.WALL_Z), "join", b, "screw_wall")
    sl = g.RAIL_H * (g.RAIL_TOP - g.RAIL_NECK) / 2 / g.RAIL_H
    e = sl * 0.5 / g.RAIL_H
    rail = [(g.RAIL_Y0 + e, BASE_T - 0.5), (g.RAIL_Y0 + g.RAIL_NECK - e, BASE_T - 0.5),
            (g.RAIL_Y0 + g.RAIL_NECK + sl, BASE_T + g.RAIL_H), (g.RAIL_Y0 - sl, BASE_T + g.RAIL_H)]
    prism_yz(rail, g.WALL_X[1] - 0.5, BASE_X[1] - g.WALL_X[1] + 0.5, "join", b, "rail")
    cyl("screw_hole", (g.WALL_X[0] - 1, g.SCREW_Y, g.SCREW_Z), g.WALL_X[1] - g.WALL_X[0] + 2, "X", "cut", b, "screw_bore")
    cyl(f"{g.POST_D} mm", (0, g.PIN_Y, BASE_T - 0.5), g.POST_TOP - BASE_T + 0.5, "Z", "join", b, "pinion_post")
    cyl("9 mm", (0, g.PIN_Y, BASE_T - 0.5), g.LIFT + 0.5, "Z", "join", b, "post_collar")
    cyl("tap_m3", (0, g.PIN_Y, g.POST_TOP - 9), 9.5, "Z", "cut", b, "post_tap")
    for side in (-1, 1):                                       # M3 nut pockets for the pull brackets
        for x in NUT_X:
            t = f"{'L' if side < 0 else 'R'}{int(x)}"
            hexp = [(side * x + 5.8 / math.sqrt(3) * math.cos(math.pi / 3 * k), NUT_Y + 5.8 / math.sqrt(3) *
                     math.sin(math.pi / 3 * k)) for k in range(6)]
            prism_xy(hexp, -1, 1 + 2.6, "cut", b, f"nut_pocket_{t}")
            cylz(side, "m3_clear", (x, NUT_Y), 1.0, BASE_T, "cut", b, f"nut_bolt_{t}")
    PARTS.append((b, PN['base']))
    return b


def build_carriages():
    sl = g.RAIL_H * (g.RAIL_TOP - g.RAIL_NECK) / 2 / g.RAIL_H
    off = g.SLIDE / math.cos(math.atan(sl / g.RAIL_H))

    def flank(z, s):
        return g.RAIL_YC + s * (g.RAIL_NECK / 2 + sl * (z - BASE_T) / g.RAIL_H + off)
    zc0, zc1 = g.Z0 - 1, BASE_T + g.RAIL_H + g.SLIDE
    chan = [(flank(zc0, -1), zc0), (flank(zc0, 1), zc0), (flank(zc1, 1), zc1), (flank(zc1, -1), zc1)]
    names = {}
    for key, side in (('car_a', -1), ('car_b', 1)):
        name = comp(key, 'F1')
        new_component(name)
        x0, x1 = sorted((side * XG0, side * (XG0 + g.CAR_L)))
        box((x0, x1), g.CAR_Y, (g.Z0, ZC), "new", name, f"{key}_block")
        prism_yz(chan, x0 - 1, g.CAR_L + 2, "cut", name, f"{key}_rail_channel")
        if key == 'car_a':
            rack = g.rack_points(x0, -XG0 + 45, g.PIN_Y + g.RP, -1)
            prism_xy(rack, g.Z0, g.GEAR_T, "join", name, "rack_a")
            box((x0, x1), (g.PIN_Y + g.RP + 1.25 + 2, g.CAR_Y[0] + 0.5), (g.Z0, g.Z0 + g.GEAR_T), "join", name, "rack_a_web")
            cyl("screw_hole", (x0 - 1, g.SCREW_Y, g.SCREW_Z), g.CAR_L + 2, "X", "cut", name, "screw_bore")
            xm = (x0 + x1) / 2
            box((xm - (g.NUT_M + 0.3) / 2, xm + (g.NUT_M + 0.3) / 2), (g.SCREW_Y - 10.3 / 2, g.SCREW_Y + 10.3 / 2),
                (g.SCREW_Z - g.HEX_AF / math.sqrt(3) - 0.15, ZC + 1), "cut", name, "nut_trap")
        else:
            rack = g.rack_points(XG0 - 45, x1, g.PIN_Y - g.RP, 1)
            prism_xy(rack, g.Z0, g.GEAR_T, "join", name, "rack_b")
            yb = g.PIN_Y - g.RP - 1.25 - g.RACK_BACK
            box((x0, x1), (yb, g.PIN_Y - g.RP - 2.0), (g.Z0, g.ARM_Z[1]), "join", name, "rack_b_riser")
            box((x0, x1), (yb, g.CAR_Y[0] + 0.5), g.ARM_Z, "join", name, "arm_b")
        for j, v in enumerate(INS):                 # M3 heat-set inserts for the modules
            cylz(side, "insert_hole", (XG0 + v, INS_Y), ZC - INS_DEPTH, INS_DEPTH + 1, "cut", name, f"{key}_insert{j}")
        PARTS.append((name, PN[key]))
        names[key] = name
    pn_ = comp('pinion', 'F1')
    new_component(pn_)
    prism_xy(g.gear_points((0, g.PIN_Y), g.ZP, 90.0), g.Z0, g.GEAR_T, "new", pn_, "pinion_gear")
    cyl(f"{g.POST_D + 0.3} mm", (0, g.PIN_Y, g.Z0 - 1), g.GEAR_T + 2, "Z", "cut", pn_, "pinion_bore")
    PARTS.append((pn_, PN['pinion']))
    names['pinion'] = pn_
    return names


def build_knob_and_screw():
    kn = comp('knob', 'F1')
    new_component(kn)
    kx0 = g.WALL_X[0] - g.KNOB_GAP - g.KNOB_T
    scal = []
    for k in range(240):
        a = 2 * math.pi * k / 240
        r = g.KNOB_D / 2 - 0.8 * (0.5 + 0.5 * math.cos(24 * a))
        scal.append((g.SCREW_Y + r * math.cos(a), g.SCREW_Z + r * math.sin(a)))
    prism_yz(scal, kx0, g.KNOB_T, "new", kn, "knob_body")
    hexp = [(g.SCREW_Y + 10.1 / math.sqrt(3) * math.cos(math.pi / 3 * k), g.SCREW_Z + 10.1 / math.sqrt(3) *
             math.sin(math.pi / 3 * k)) for k in range(6)]
    prism_yz(hexp, g.WALL_X[0] - g.KNOB_GAP - g.HEAD_K - 0.2, g.HEAD_K + 1, "cut", kn, "hex_pocket")
    cyl("screw_hole", (kx0 - 1, g.SCREW_Y, g.SCREW_Z), g.KNOB_T + 2, "X", "cut", kn, "knob_bore")
    PARTS.append((kn, PN['knob']))
    hx = lambda af: [(g.SCREW_Y + af / math.sqrt(3) * math.cos(math.pi / 3 * k + math.pi / 6),  # noqa: E731
                      g.SCREW_Z + af / math.sqrt(3) * math.sin(math.pi / 3 * k + math.pi / 6)) for k in range(6)]
    sc = "M6x70-ISO4017_F1"
    new_component(sc)
    head_x1 = g.WALL_X[0] - g.KNOB_GAP
    head = [(g.SCREW_Y + g.HEX_AF / math.sqrt(3) * math.cos(math.pi / 3 * k), g.SCREW_Z + g.HEX_AF / math.sqrt(3) *
             math.sin(math.pi / 3 * k)) for k in range(6)]
    prism_yz(head, head_x1 - g.HEAD_K, g.HEAD_K, "new", sc, "screw_head")
    cyl("5.8 mm", (head_x1 - 0.01, g.SCREW_Y, g.SCREW_Z), g.SCREW_L + 0.01, "X", "join", sc, "screw_shank")
    PURCHASED.append((sc, "ISO 4017 M6x70", "SCREW, HEX, M6 X 70, FULL THREAD"))
    ny = "M6-nyloc-DIN985_F1"
    new_component(ny)
    prism_yz(hx(g.HEX_AF), g.WALL_X[1], g.NYLOC_M, "new", ny, "nyloc")
    cyl("6 mm", (g.WALL_X[1] - 1, g.SCREW_Y, g.SCREW_Z), g.NYLOC_M + 2, "X", "cut", ny, "nyloc_bore")
    PURCHASED.append((ny, "DIN 985 M6", "NUT, NYLOC, M6"))
    nt = "M6-nut-ISO4032_F1"
    new_component(nt)
    xm = (-XG0 - g.CAR_L + -XG0) / 2
    prism_yz(hx(g.HEX_AF), xm - g.NUT_M / 2, g.NUT_M, "new", nt, "nut")
    cyl("6 mm", (xm - g.NUT_M / 2 - 1, g.SCREW_Y, g.SCREW_Z), g.NUT_M + 2, "X", "cut", nt, "nut_bore")
    PURCHASED.append((nt, "ISO 4032 M6", "NUT, HEX, M6"))
    return kn, sc, ny, nt


def m3_head(name, side, xy, z_seat):
    """Purchased M3 socket head (ISO 4762), head only + shank stub, for clearance checks."""
    new_component(name)
    cylz(side, 5.5, xy, z_seat, 3.0, "new", name, f"{name}_head")
    PURCHASED.append((name, "ISO 4762 M3", "SCREW, SOCKET HEAD, M3"))
    return name


# ----------------------------------------------------------------------------- modules
def holder_parallel(inst, side, xg, dy=0.0):
    """Parallel module: one part for both sides (symmetric about the finger mid-plane v = 10)."""
    name = comp('hold', inst)
    new_component(name)
    xi, xo = xg - 0.5, xg + g.W + 0.5
    bx(side, (xi, xo), (g.CAR_Y[0] + dy, YB + BOSS_R + 0.4 + dy), CAP, "new", name, f"{name}_cap")
    bx(side, (xi, xo), (28.0 + dy, YB + BOSS_R + 0.4 + dy), FLOOR, "join", name, f"{name}_floor")
    bx(side, (xi, xo), (28.0 + dy, 31.3 + dy), (FLOOR[0], CAP[0] + 0.3), "join", name, f"{name}_back")
    bx(side, (xi, xo), (g.CAR_Y[1] + 0.1 + dy, g.CAR_Y[1] + 2.1 + dy), (24.0, CAP[0] + 0.3), "join", name, f"{name}_lip")
    for j, v in enumerate(INS):
        cylz(side, "m3_clear", (xg + v, INS_Y + dy), CAP[0] - 1, 5, "cut", name, f"{name}_screw{j}")
    for j, v in enumerate(VB):
        cylz(side, "pin_hole", (xg + v, YB + dy), FLOOR[0] - 1, CAP[1] - FLOOR[0] + 2, "cut", name, f"{name}_pin{j}")
    PARTS.append((name, PN['hold']))
    return name


def holder_c_socket(inst, side, xg, dy=0.0):
    """v2b: socket block (open top) on a cap plate screwed to the carriage; symmetric about v = 10."""
    name = comp('hold_c', inst)
    new_component(name)
    xi, xo = xg - 4.0, xg + g.W + 4.0
    yb0 = Y_R + C_UC - CR - 4.0                         # 30.5: socket block rear face
    bx(side, (xi, xo), (yb0 + dy, Y_R + dy), (FLOOR[0], CAP[1]), "new", name, f"{name}_block")   # flush with the cap top: prints cap down
    bx(side, (xi, xo), (g.CAR_Y[0] + dy, yb0 + 0.5 + dy), CAP, "join", name, f"{name}_cap")
    bx(side, (xi, xo), (28.0 + dy, yb0 + 0.5 + dy), (FLOOR[0], CAP[0] + 0.3), "join", name, f"{name}_back")
    bx(side, (xi, xo), (g.CAR_Y[1] + 0.1 + dy, g.CAR_Y[1] + 2.1 + dy), (24.0, CAP[0] + 0.3), "join", name, f"{name}_lip")
    for j, v in enumerate(C_VC):
        cylz(side, 2 * (CR + C_PLAY), (xg + v, Y_R + C_UC + dy), FLOOR[1], CAP[1] + 1 - FLOOR[1], "cut", name, f"{name}_bore{j}")
        bx(side, (xg + v - C_MOUTH / 2, xg + v + C_MOUTH / 2), (Y_R + C_UC + dy, Y_R + 1 + dy), (FLOOR[1], CAP[1] + 1),
           "cut", name, f"{name}_mouth{j}")
    bx(side, (xg + C_VC[0] + CR + 1.0, xg + C_VC[1] - CR - 1.0), (Y_R - 4.0 + dy, Y_R + 1 + dy), (FLOOR[1], CAP[1] + 1),
       "cut", name, f"{name}_relief")
    for j, v in enumerate(INS):
        cylz(side, "m3_clear", (xg + v, INS_Y + dy), CAP[0] - 1, 5, "cut", name, f"{name}_screw{j}")
    PARTS.append((name, PN['hold_c']))
    return name


def bracket_pull(side, xf, dy=0.0):
    key = 'br_l' if side < 0 else 'br_r'
    name = comp(key, 'F1')
    BR_OUT = xf + 24.0          # block, wall and cap end flush: the bracket prints lying on this face
    new_component(name)
    bx(side, (xf - 3.0, BR_OUT), (16.0 + dy, 31.0 + dy), (BASE_T, FLOOR[0] - 0.2), "new", name, f"{name}_block")
    bx(side, (xf + 20.5, BR_OUT), (28.0 + dy, YB + BOSS_R + 0.4 + dy), (BASE_T, CAP[1]), "join", name, f"{name}_wall")
    bx(side, (xf + 12.0, xf + 20.8), (30.5 + dy, YB + BOSS_R + 0.4 + dy), FLOOR, "join", name, f"{name}_floor")
    bx(side, (xf + 12.0, BR_OUT), (30.5 + dy, YB + BOSS_R + 0.4 + dy), CAP, "join", name, f"{name}_cap")
    bx(side, (xf - 3.0, xf - 0.75), (22.0 + dy, 31.0 + dy), (FLOOR[0] - 0.5, FLOOR[1]), "join", name, f"{name}_guide_in")
    bx(side, (xf + 7.75, xf + 10.0), (22.0 + dy, 31.0 + dy), (FLOOR[0] - 0.5, FLOOR[1]), "join", name, f"{name}_guide_out")
    cylz(side, "pin_hole", (xf + VB[1], YB + dy), FLOOR[0] - 1, CAP[1] - FLOOR[0] + 2, "cut", name, f"{name}_pin")
    # groove for the inner pin's barb (hangs under the slider floor) over the whole pull stroke
    g0 = FLOOR[0] - BARB_UP - BARB_H - 0.5
    bx(side, (xf + VB[0] - BARB_D / 2 - 2.0, xf + VB[0] + BARB_D / 2 + 2.0), (YB - PULL_MAX - 1.0 - BARB_D / 2 - 0.5 + dy, 31.5 + dy),
       (g0, FLOOR[0]), "cut", name, f"{name}_barb_groove")
    for j, v in enumerate(BR_SCREW):
        slot_z(side, (xf + v - 5, NUT_Y + dy), (xf + v + 5, NUT_Y + dy), 3.4, (BASE_T - 1, FLOOR[0]), "cut", name,
               f"{name}_slot{j}")
    PARTS.append((name, PN[key]))
    return name


def slider_pull(inst, side, xf, p=0.0, dy=0.0):
    """Symmetric about its pin line (v = 3.5): one part for both sides."""
    name = comp('slider', inst)
    new_component(name)
    yy = dy - p
    xa, xb = xf + VB[0] - 4.0, xf + VB[0] + 4.0
    bx(side, (xa, xb), (SL_Y0 + yy, YB + BOSS_R + 0.4 + yy), FLOOR, "new", name, f"{name}_floor")
    bx(side, (xa, xb), (SL_Y0 + yy, 31.3 + yy), (FLOOR[0], CAP[0] + 0.3), "join", name, f"{name}_back")
    bx(side, (xa, xb), (SL_Y0 + yy, YB + BOSS_R + 0.4 + yy), CAP, "join", name, f"{name}_cap")
    cylz(side, "drive_d", (xf + DRIVE[0], DRIVE[1] + yy), CAP[1] - 0.3, CAM_Z0 + 3.0 - 0.2 - CAP[1] + 0.3, "join", name,
         f"{name}_drive")
    slot_z(side, (xf + VB[0] - 1.5, YB + yy), (xf + VB[0] + 1.5, YB + yy), PIN_HOLE, (FLOOR[0] - 1, CAP[1] + 1),
           "cut", name, f"{name}_pinslot")
    PARTS.append((name, PN['slider']))
    return name


def cam_plate(side, xg, dy=0.0):
    key = 'cam_l' if side < 0 else 'cam_r'
    name = comp(key, 'F1')
    new_component(name)
    xi, xo = xg - 0.5, xg + g.W + 0.5
    z1 = CAM_Z0                                           # plate underside: over the snap-pin heads on the caps
    bx(side, (xi, xo), (g.CAR_Y[0] + dy, g.CAR_Y[1] + dy), (ZC, z1 + 0.3), "new", name, f"{name}_standoff")
    bx(side, (xi, xo), (g.CAR_Y[0] + dy, 33.0 + dy), (z1, z1 + 3.0), "join", name, f"{name}_plate")
    d0, d1 = -1.0, PULL_MAX + 1.0                         # slot ends: 1 mm past zero and past full pull
    slot_z(side, (xg + DRIVE[0] + d0, DRIVE[1] - d0 + dy), (xg + DRIVE[0] + d1, DRIVE[1] - d1 + dy), 4.4,
           (z1 - 1, z1 + 4), "cut", name, f"{name}_slot")
    for j, v in enumerate(INS):
        cylz(side, "m3_clear", (xg + v, INS_Y + dy), ZC - 1, z1 + 5 - ZC, "cut", name, f"{name}_screw{j}")
        cylz(side, 6.0, (xg + v, INS_Y + dy), z1 + 1.0, 3.0, "cut", name, f"{name}_cbore{j}")   # M3x12 fits (2 mm deep)
    PARTS.append((name, PN[key]))
    return name


# ----------------------------------------------------------------------------- assembly
def params():
    for name, expr, why in [
        ("slide_clr", f"{g.SLIDE} mm", "dovetail rail clearance per side (moving parts)"),
        ("pin_fit", "0.15 mm", "pinion bore on the base post, per side"),
        ("screw_hole", "6.6 mm", "M6 clearance, ISO 273 medium"),
        ("tap_m3", "2.5 mm", "M3 thread-forming hole in the pinion post"),
        ("m3_clear", "3.4 mm", "M3 clearance (module screws, bracket screws)"),
        ("insert_hole", f"{INS_D} mm", "M3 heat-set insert in the carriage top (CLAUDE.md 4.0-4.2, NEEDS PRINT TEST)"),
        ("pin_hole", f"{PIN_HOLE} mm", "snap-pin hole in holders, brackets, sliders and the TPU finger bosses"),
        ("pin_d", f"{PIN_D} mm", "printed snap pin shank: 0.15 mm play per side (user rule 0.10-0.15)"),
        ("head_d", f"{HEAD_D} mm", "printed snap pin head"),
        ("drive_d", "4.0 mm", "slider drive boss in the 4.4 mm cam slot (0.2 per side)"),
    ]:
        c("parameters.add", name=name, expression=expr, comment=why)


def build(mode):
    g.cmds.clear()
    PARTS.clear()
    PURCHASED.clear()
    pn, desc = ASSY[mode]
    c("document.metadata.set", values={"part_number": pn, "description": desc, "revision": "X1",
                                       "project": "finray_tests"})
    params()
    b = build_base()
    car = build_carriages()
    kn, sc, ny, nt = build_knob_and_screw()
    o = lambda n: f"{n}:1"  # noqa: E731
    rigid = []                                            # (a, b)
    extra_joints = []

    def park(names):
        rigid.extend((b, n) for n in names)

    mounted_pull = mode == 'pull'
    # fingers (shared by every module): mounted in whichever module is on the carriages
    root = 'c' if mode == 'csocket' else 'pin'
    fingers = {s: build_finger('fa', f"F{i}", s, XG0, root) for i, s in ((1, -1), (2, 1))}
    pins = {}
    if mode in ('parallel', 'pull'):
        hold_dy = PARK_DY if mounted_pull else 0.0
        holders = {s: holder_parallel(f"F{i}", s, XG0, hold_dy) for i, s in ((1, -1), (2, 1))}
        heads = {}
        for i, s in ((1, -1), (2, 1)):
            for j in (0, 1):
                heads[(s, j)] = m3_head(f"M3x8-ISO4762_hold{i}{j}", s, (XG0 + INS[j], INS_Y + hold_dy), CAP[1])
        pull_dy = 0.0 if mounted_pull else PARK_DY
        br = {s: bracket_pull(s, XG0, pull_dy) for s in (-1, 1)}
        sl = {s: slider_pull(f"F{i}", s, XG0, 0.0, pull_dy) for i, s in ((1, -1), (2, 1))}
        cam = {s: cam_plate(s, XG0, pull_dy) for s in (-1, 1)}
        brs = {}
        for s in (-1, 1):
            for j, v in enumerate(BR_SCREW):
                x_nut = min(NUT_X, key=lambda xn: abs(xn - (XG0 + v)))
                brs[(s, j)] = m3_head(f"M3x8-ISO4762_br{'L' if s < 0 else 'R'}{j}", s, (x_nut, NUT_Y + pull_dy),
                                      FLOOR[0] - 0.2)
        # pins: in the mounted module
        for i, s in ((1, -1), (2, 1)):
            for j, v in enumerate(VB):
                pins[(s, j)] = snap_pin(f"F{i}{'io'[j]}", (s * (XG0 + v), YB), CAP[1], FLOOR[0])
        car_of = {-1: car['car_a'], 1: car['car_b']}
        if not mounted_pull:
            for s in (-1, 1):
                rigid += [(car_of[s], holders[s]), (holders[s], fingers[s]), (holders[s], pins[(s, 0)]),
                          (holders[s], pins[(s, 1)]), (holders[s], heads[(s, 0)]), (holders[s], heads[(s, 1)])]
            park(list(br.values()) + list(sl.values()) + list(cam.values()) + list(brs.values()))
        else:
            park(list(holders.values()) + list(heads.values()))
            for s in (-1, 1):
                rigid += [(car_of[s], cam[s]), (b, br[s]), (br[s], fingers[s]), (br[s], pins[(s, 1)]),
                          (sl[s], pins[(s, 0)]), (b, brs[(s, 0)]), (b, brs[(s, 1)])]
                nm = f"P_{'L' if s < 0 else 'R'}"
                extra_joints.append(("joint.as_built", dict(type="slider", a=o(br[s]), b=o(sl[s]),
                                     at={"point": [fx(s * (XG0 + VB[0])), fx(YB), FLOOR[0]], "z": [0, -1, 0]},
                                     name=nm, limits=[[-1.0, PULL_MAX + 1.0]])))
                dx = 1.0 / math.sqrt(2)
                extra_joints.append(("joint.as_built", dict(type="pin_slot", a=o(cam[s]), b=o(sl[s]),
                                     at={"point": [fx(s * (XG0 + DRIVE[0])), DRIVE[1], CAP[1]], "z": [0, 0, 1],
                                         "x": [fx(s * dx), fx(-dx), 0]}, name=f"CAM_{'L' if s < 0 else 'R'}")))
    else:                                                 # csocket
        holders = {s: holder_c_socket(f"F{i}", s, XG0) for i, s in ((1, -1), (2, 1))}
        car_of = {-1: car['car_a'], 1: car['car_b']}
        for i, s in ((1, -1), (2, 1)):
            hs = [m3_head(f"M3x8-ISO4762_hold{i}{j}", s, (XG0 + INS[j], INS_Y), CAP[1]) for j in (0, 1)]
            rigid += [(car_of[s], holders[s]), (holders[s], fingers[s])] + [(holders[s], h) for h in hs]

    # joints
    c("component.activate", component=0)
    xg_min = XG_MIN_C if mode == 'csocket' else XG_MIN
    c("joint.as_built", type="slider", a=o(b), b=o(car['car_a']), at={"point": [0, g.RAIL_YC, BASE_T], "z": [1, 0, 0]},
      name="S_A", limits=[[XG0 - XG_MAX, XG0 - xg_min]])
    c("joint.as_built", type="slider", a=o(b), b=o(car['car_b']), at={"point": [0, g.RAIL_YC, BASE_T], "z": [1, 0, 0]},
      name="S_B", limits=[[xg_min - XG0, XG_MAX - XG0]])
    c("joint.as_built", type="revolute", a=o(b), b=o(car['pinion']), at={"point": [0, g.PIN_Y, g.Z0], "z": [0, 0, 1]},
      name="R_pinion")
    c("joint.as_built", type="revolute", a=o(b), b=o(kn), at={"point": [g.WALL_X[0], g.SCREW_Y, g.SCREW_Z],
                                                               "z": [1, 0, 0]}, name="R_knob")
    c("joint.as_built", type="rigid", a=o(kn), b=o(sc), name="screw_in_knob")
    c("joint.as_built", type="rigid", a=o(kn), b=o(ny), name="nyloc_on_screw")
    c("joint.as_built", type="rigid", a=o(car['car_a']), b=o(nt), name="nut_in_carriage")
    for a_, b_ in rigid:
        c("joint.as_built", type="rigid", a=o(a_), b=o(b_), name=f"fix_{b_}")
    for cmd, p in extra_joints:
        c(cmd, **p)
    c("joint.screw", a="R_knob", b="S_A", pitch="1 mm")
    c("joint.rack_pinion", a="S_A", b="R_pinion", radius=g.RP, reverse=True)
    c("joint.rack_pinion", a="R_pinion", b="S_B", radius=g.RP)

    # metadata + exports
    reg = parts.register()
    for name, p in PARTS:
        c("component.metadata.set", component=name, part_number=p, description=reg[p]['Description'],
          revision="X1", bom_type="normal")
    for name, p, d in PURCHASED:
        c("component.metadata.set", component=name, part_number=p, description=d, bom_type="purchased")
    if mode != 'pull':
        done = set()
        for name, p in PARTS:
            if p in done:
                continue
            done.add(p)
            for ext, cmd in (('step', 'file.export_step'), ('stl', 'file.export_stl'), ('3mf', 'file.export_3mf')):
                q = dict(path=f"{VDIR[mode]}/exports/{parts.export(p, 'X1', ext)}", bodies=[name])
                if ext != 'step':
                    q["quality"] = "fine"
                c(cmd, **q)
    return list(g.cmds)


def out_path(mode, scratch=None):
    pn = ASSY[mode][0]
    stem = parts.fname(pn)
    if mode == 'pull':
        return os.path.join(scratch or '.', f"{stem}_pull.json")
    return f"{VDIR[mode]}/cad/{stem}.json"


def write(mode, path):
    cmd_list = build(mode)
    if mode != 'pull':
        for sub in ('cad', 'exports', 'docs'):
            os.makedirs(os.path.join(VDIR[mode], sub), exist_ok=True)
    with open(path, 'w') as fh:
        fh.write('[\n' + ',\n'.join(' ' + json.dumps(x, separators=(',', ':')) for x in cmd_list) + '\n]\n')
    print(path, len(cmd_list), 'steps')


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    scratch = sys.argv[2] if len(sys.argv) > 2 else None
    for m in (('parallel', 'csocket') if which == 'all' else (which,)):
        write(m, out_path(m, scratch))
