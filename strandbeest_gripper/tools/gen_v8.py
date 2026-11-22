"""Generate v8_four-bar/cad/GRIP-9016_assy-four-bar.json: the v7 jaw motion with a four-bar per leg.

v8 (user request 2026-11-15: "keep the movement of the jaws the same but simplify, make smaller / less
components"). Each 7-link Jansen leg becomes a crank-rocker four-bar (fourbar.py): an eccentric on the
crank gear drives a coupler ring; the coupler point P carries the jaw, the coupler's B end runs on a
rocker that pivots on a frame column Q. Same jaw opening (H 8.96 per jaw), same flat clamp-and-pull
stroke (19.9 mm with the gap within 0.153 mm per jaw; Jansen 0.189), same parallel twin-leg jaws.

Why an eccentric instead of a crank pin: the coupler sweeps over the crank centre O, so a pin at J1
would leave no room for a crank shaft going up to the top plate. The ring around an eccentric boss
on the gear lets the D5 crank shaft run straight from the base to the top plate (held at both ends,
v7 lesson).

Layout (world = leg frame of finger 1 leg A, O_A1 at the origin; the clamp flat runs along x):
  - leg B = leg A shifted by D along x, same crank angle (Z46 crank gears, a Z24 idler X between them);
  - finger 2 = finger 1 mirrored about the clamp line y = YC (cranks turn the other way);
  - X1 meshes X2 on the clamp line: 6 gears in a tree A1-X1-B1, X1-X2, X2-A2, X2-B2;
  - one top plate on the 4 Q columns (frame post + journal for the rocker + plate stub), no pillars;
  - the jaw: hole at P of leg A, 2 mm slot at P of leg B (print tolerance), 45 mm free beyond it.

Z stack: base 0-4 | gear 4.5-9.5 (0.5 over the base, no thrust bosses: built clear, rests on the base) (idlers 4.5-9.0) | eccentric flange 9.5-10, boss to 13.5 |
coupler 10-13.5 | rocker 14-17.5, jaw 14-22 | top plate 22.5-26.5 | knob 27-35.

    python3 strandbeest_gripper/tools/gen_v8.py          (from the repo root)
    tools/build.sh strandbeest_gripper/v8_four-bar
    python3 strandbeest_gripper/tools/verify_v8.py
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'tools'))
import parts  # noqa: E402
import fourbar as fb  # noqa: E402

REV = lambda pn: parts.register()[pn]['Rev']  # noqa: E731  revision from PARTS.md

# Variant 'b' (v8b, 2026-11-22): the Z24 idlers lifted off their D3 snap pins and jumped teeth (pin held by 2 mm of
# base, split by its snap slot, flats = up to 0.4 play). v8b: a solid D8 post on the frame carries each idler
# (0.15 per side), a D10 cap-head snap pin through the post keeps the idler from lifting more than 0.2.
# Select with `python3 gen_v8.py b` or V8_VARIANT=b (verify_v8 / build_guide_v8 take the same argument).
VARIANT = os.environ.get('V8_VARIANT') or ('b' if 'b' in sys.argv[1:] else '')
VDIR = 'strandbeest_gripper/v8_four-bar'
ASSY = 'GRIP-9016'
PN = {'frame': 'GRIP-0107', 'plate': 'GRIP-0108', 'knob': 'GRIP-0109',
      ('crank', 'A1'): 'GRIP-0110', ('crank', 'B1'): 'GRIP-0111', ('crank', 'A2'): 'GRIP-0112', ('crank', 'B2'): 'GRIP-0113',
      'idler': 'GRIP-0114', 'coupler': 'GRIP-0115', 'rocker': 'GRIP-0116', 'jaw': 'GRIP-0117',
      'shaft': 'GRIP-0118', 'shaft_knob': 'GRIP-0119', 'pin_q': 'GRIP-0120', 'pin_b': 'GRIP-0121',
      'pin_p': 'GRIP-0122', 'pin_x': 'GRIP-0123'}
if VARIANT == 'b':
    VDIR, ASSY = 'strandbeest_gripper/v8b_idler-post', 'GRIP-9019'
    PN.update({'frame': 'GRIP-0137', 'idler': 'GRIP-0138', 'pin_x': 'GRIP-0139'})
LEGS = ('A1', 'B1', 'A2', 'B2')

# ---------------------------------------------------------------------------- dimensions
CLEAR = 0.15                     # printed pin in printed hole, per side (user rule 0.10-0.15)
MOD, ZC, ZX = 1.0, 46, 24        # crank gear Z46: its root circle (21.75) carries the whole eccentric flange
BACKLASH = 0.3
RC, RX = MOD * ZC / 2, MOD * ZX / 2
E = fb.LEG['r']                  # eccentricity = crank radius
SHAFT_D, SHAFT_AF = 5.0, 3.4     # crank shaft D5 with two flats 3.4 apart (key + print flats)
BOSS_R = E + (SHAFT_D / 2 + CLEAR) + 1.2          # eccentric boss: 1.2 mm wall outside the shaft bore
RING_BORE_R = BOSS_R + CLEAR
RING_R = RING_BORE_R + 2.2       # coupler ring wall 2.2 (fourbar fit: RING = 6.2 = ring outer - e)
FLANGE_R = BOSS_R + 1.0          # thrust flange the ring rests on
BAR_W = 7.0                      # link width (sketch slot width takes numbers only)
JAW_W, JAW_H = 11.0, 8.0         # jaw = v7 pad width; clamp faces on the clamp line
CLAMP_GAP = 1.53                 # v7 clamp gap
L_FREE = 45.0                    # jaw length beyond leg B's P
JAW_SLOT = 2.0                   # leg-B jaw slot length (parallelogram: no binding from print errors)
EYE_Q = 11.0                     # rocker eye at Q (journal bore 6.3)
JOURNAL_D = 6.0
POST_D = 7.0
O_STUB_D = 8.0
KNOB_R, KNURLS = 20.0, 40

BASE_T = 4.0
# v8b idler post (frame) and cap pin
XPOST_D = 8.0                    # solid frame post the idler turns on
XCAP_D = 10.0                    # cap-pin head: covers the D8.3 idler bore by 0.85 per side
XLIFT = 0.2                      # idler may lift this much before it meets the cap head
Z_GEAR, GEAR_T, IDLE_T = 4.5, 5.0, 4.5
Z_GTOP = Z_GEAR + GEAR_T                          # 9.5
Z_L1, LINK_T, GAP = 10.0, 3.5, 0.5
Z_L1T = Z_L1 + LINK_T                             # 13.5 (boss top flush)
Z_L2 = Z_L1T + GAP                                # 14.0
Z_L2T = Z_L2 + LINK_T                             # 17.5
Z_JAWT = Z_L2 + JAW_H                             # 22.0
TP0, TP_T = Z_JAWT + GAP, 4.0                     # top plate 22.5-26.5
TP1 = TP0 + TP_T
KNOB_Z0, KNOB_H = TP1 + GAP, 8.0
KNOB_T = KNOB_Z0 + KNOB_H

# pins (v4b/v7 snap pins, two flats)
PIN_R = (3.4 - 2 * CLEAR) / 2
FLAT = 0.25
HEAD_H, BARB_H, BARB_UP, SLOT_W, SLOT_DOWN, SHANK_OVER = 3.0, 1.5, 0.2, 0.8, 4.0, 0.3
PRESS_CH = 0.3                   # X2: lead-in chamfer on the coupler press holes
PHEAD_H = 1.5                    # press-pin and idler-pin heads (thin: under the plate / inside the idler)
XPOST_TOP = Z_GEAR + IDLE_T - PHEAD_H          # v8b: 7.5, cap head 7.5-9.0 flush with the idler top
SH_HEAD_D, SH_HEAD_H = 8.0, 2.0  # crank shaft head under the base
SH_BARB_D, SH_BARB_TIP, SH_SLOT, SH_SLOT_DOWN = 5.9, 4.6, 1.0, 5.0
SH_SEAT = 2.5                    # shaft head top = base counterbore ceiling

# ---------------------------------------------------------------------------- geometry
P0 = fb.pose(0.0)
YMIN = fb.metrics()['ymin']
YC = YMIN - JAW_W / 2 - CLAMP_GAP / 2              # clamp line (finger 2 = mirror)
XH = -(YC + RX)                                    # idler X1 centre below O, on the X1-X2 mesh
D = 2 * math.sqrt((RC + RX) ** 2 - XH ** 2)        # leg spacing A -> B
assert D > 2 * (RC + MOD) + 0.5, D                 # crank gears A and B do not touch


def mir(p):
    return (p[0], 2 * YC - p[1])


def leg_pts(leg, pose=P0):
    s = D if leg[0] == 'B' else 0.0
    q = {k: (v[0] + s, v[1]) for k, v in pose.items()}
    return q if leg[1] == '1' else {k: mir(v) for k, v in q.items()}


JP = {leg: leg_pts(leg) for leg in LEGS}
XC = {1: (D / 2, -XH), 2: mir((D / 2, -XH))}
NOTCH_Y = 7.0                                      # half width of the base notch / plate window over the slot


def fx(v):
    return round(v, 4)


cmds = []


def c(command, **params):
    cmds.append({"command": command, "params": params})


def cname(key, i):
    return f"{parts.fname(PN[key])}_{i}"


def occ(key, i):
    return f"{cname(key, i)}:1"


def new_component(name, grounded=False):
    c("component.activate", component=0)
    c("component.create", name=name, activate=True, grounded=grounded)


def cyl(d, z0, h, pt, op, body, name):
    p = dict(diameter=d if isinstance(d, str) else f"{fx(d)} mm", height=f"{fx(h)} mm",
             base=[fx(pt[0]), fx(pt[1]), fx(z0)], operation=op, name=name)
    if op == "new":
        p["body_name"] = body
    else:
        p["targets"] = [body]
    c("solid.cylinder", **p)


def poly(name, pts, z0, h, op, body):
    c("sketch.create", plane="XY", offset=f"{fx(z0)} mm", name=f"{name}_sk")
    c("sketch.line", points=[[fx(x), fx(y)] for x, y in pts], closed=True)
    c("sketch.finish")
    p = dict(distance=f"{fx(h)} mm", operation=op, name=name)
    if op == "new":
        p["body_name"] = body
    else:
        p["targets"] = [body]
    c("solid.extrude", **p)


def slot(name, p, q, w, z0, h, op, body):
    c("sketch.create", plane="XY", offset=f"{fx(z0)} mm", name=f"{name}_sk")
    c("sketch.slot.center_to_center", p0=[fx(p[0]), fx(p[1])], p1=[fx(q[0]), fx(q[1])], width=w)
    c("sketch.finish")
    pr = dict(distance=f"{fx(h)} mm", operation=op, name=name)
    if op == "new":
        pr["body_name"] = body
    else:
        pr["targets"] = [body]
    c("solid.extrude", **pr)


def circle_pts(ctr, r, n=72, ymax=None):
    """Circle as a polygon; ymax clips it to |y - ctr.y| <= ymax (double-D)."""
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n
        y = r * math.sin(a)
        if ymax is not None:
            y = max(-ymax, min(ymax, y))
        out.append((ctr[0] + r * math.cos(a), ctr[1] + y))
    return out


def hull(points):
    pts = sorted(set((round(x, 4), round(y, 4)) for x, y in points))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def disc_hull(discs):
    return hull([(p[0] + r * math.cos(a * math.pi / 18), p[1] + r * math.sin(a * math.pi / 18))
                 for p, r in discs for a in range(36)])


def deboss(body, text, center, h, z_top, name, angle=0.0):
    a = math.radians(angle)
    at = (center[0] + math.sin(a) * h / 2, center[1] - math.cos(a) * h / 2)
    c("sketch.create", plane="XY", offset=f"{fx(z_top - 0.6)} mm", name=f"{name}_sk")
    c("sketch.text", text=text, at=[fx(at[0]), fx(at[1])], height=h, angle=fx(angle), align="center")
    c("sketch.finish")
    c("solid.extrude", distance="0.7 mm", operation="cut", targets=[body], name=name)


# ---------------------------------------------------------------------------- gears
def inv(a):
    return math.tan(a) - a


def gear_points(ctr, z, phase_deg, n_flank=7):
    """Involute spur gear outline (gen_dual.gear_points without the servo transform)."""
    r = MOD * z / 2
    rb = r * math.cos(math.radians(20))
    ra, rf = r + MOD, r - 1.25 * MOD
    psi_p = (math.pi * MOD / 2 - BACKLASH / 2) / (2 * r)
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
        nxt = phi + 2 * math.pi / z
        a0, a1 = phi + flank[0][1], nxt - flank[0][1]
        pts += [(rf, a0 + (a1 - a0) * i / 3) for i in range(1, 3)]
    return [(ctr[0] + R * math.cos(a), ctr[1] + R * math.sin(a)) for R, a in pts]


def mesh_phase(ph_a, z_a, c_a, c_b, z_b):
    """Tooth phase of gear b so it meshes with gear a (gen_v3.mesh_phase, tested off the centre line)."""
    ra, rb = MOD * z_a / 2, MOD * z_b / 2
    alpha = math.degrees(math.atan2(c_b[1] - c_a[1], c_b[0] - c_a[0]))
    pa = 360.0 / z_a
    d = ((alpha - ph_a + pa / 2) % pa) - pa / 2
    s = -ra * math.radians(d)
    return alpha + 180.0 - math.degrees((s - math.pi * MOD / 2) / rb)


PH = {'A1': 0.0}
PH['X1'] = mesh_phase(PH['A1'], ZC, JP['A1']['O'], XC[1], ZX)
PH['B1'] = mesh_phase(PH['X1'], ZX, XC[1], JP['B1']['O'], ZC)
PH['X2'] = mesh_phase(PH['X1'], ZX, XC[1], XC[2], ZX)
PH['A2'] = mesh_phase(PH['X2'], ZX, XC[2], JP['A2']['O'], ZC)
PH['B2'] = mesh_phase(PH['X2'], ZX, XC[2], JP['B2']['O'], ZC)


# ---------------------------------------------------------------------------- pins
def two_flats(body, p, r, zl, zh, flat=FLAT):
    """User rule 2026-11-15: two parallel flats (+-y): print lying on one."""
    off = r - flat
    for s_, tag in ((-1, 'flat'), (1, 'flat2')):
        c("solid.box", length="20 mm", width="10 mm", height=f"{fx(zh - zl + 2)} mm",
          center=[fx(p[0]), fx(p[1] + s_ * (off + 5)), fx((zl + zh) / 2)],
          operation="cut", targets=[body], name=f"{body}_{tag}")


def snap_pin(body, p, z_seat, z_cap, down=False, head_h=HEAD_H, r=PIN_R, head_d="ppin_head_d",
             shank_d="ppin_d", barb=("barb_d", "barb_tip_d"), slot_w="snap_slot", slot_down=SLOT_DOWN, flat=FLAT):
    """One-piece snap pin: head face at z_seat, barb shoulder BARB_UP past z_cap (the far face)."""
    s_ = -1 if down else 1
    z_sh = z_cap + s_ * BARB_UP
    z0 = z_seat - s_ * head_h
    top = z_sh + s_ * BARB_H
    cyl(head_d, min(z0, z_seat), head_h, p, "new", body, f"{body}_head")
    lo, hi = sorted((z_seat - s_ * 0.01, z_sh + s_ * SHANK_OVER))
    cyl(shank_d, lo, hi - lo, p, "join", body, f"{body}_shank")
    big, tip = barb
    if not down:
        c("solid.cone", diameter=big, top_diameter=tip, height=f"{BARB_H} mm", base=[fx(p[0]), fx(p[1]), fx(z_sh)],
          operation="join", targets=[body], name=f"{body}_barb")
    else:
        c("solid.cone", diameter=tip, top_diameter=big, height=f"{BARB_H} mm", base=[fx(p[0]), fx(p[1]), fx(top)],
          operation="join", targets=[body], name=f"{body}_barb")
    zl, zh = sorted((z0, top))
    two_flats(body, p, r, zl, zh, flat)
    sl = BARB_H + BARB_UP + slot_down
    c("solid.box", length=slot_w, width="20 mm", height=f"{fx(sl + 1)} mm",
      center=[fx(p[0]), fx(p[1]), fx(top - s_ * (sl / 2 - 0.5))], operation="cut", targets=[body], name=f"{body}_slot")
    return abs(z_sh - z_seat)


def press_pin(body, p, z_bot, z_head):
    """Headed pin pressed into the coupler (flush with its bottom), turning in the part above."""
    cyl("ppin_d", z_bot, z_head - z_bot + 0.01, p, "new", body, f"{body}_shank")
    cyl("ppin_head_d", z_head, PHEAD_H, p, "join", body, f"{body}_head")
    two_flats(body, p, PIN_R, z_bot, z_head + PHEAD_H)
    return z_head - z_bot


# ---------------------------------------------------------------------------- parts
ATTACH = []
COMPS = []          # (key, instance)


def frame():
    name = cname('frame', 'F')
    c("component.create", name=name, activate=True, grounded=True)
    COMPS.append(('frame', 'F'))
    discs = []
    for leg in LEGS:
        discs += [(JP[leg]['O'], 9.0), (JP[leg]['Q'], 7.0)]
    discs += [(XC[1], 6.0), (XC[2], 6.0)]
    poly("base", disc_hull(discs), 0.0, BASE_T, "new", name)
    # notch under the gripping slot, beyond the idler bosses
    x0 = XC[1][0] + 5.0
    poly("slot_notch", [(x0, YC - NOTCH_Y), (300, YC - NOTCH_Y), (300, YC + NOTCH_Y), (x0, YC + NOTCH_Y)],
         -0.5, BASE_T + 1, "cut", name)
    for leg in LEGS:
        o, q = JP[leg]['O'], JP[leg]['Q']
        cyl("post_d", BASE_T - 0.01, Z_L2 - GAP - BASE_T + 0.01, q, "join", name, f"fr_post_Q{leg}")
        cyl("journal_d", Z_L2 - GAP - 0.3, Z_L2T + GAP - (Z_L2 - GAP) + 0.3, q, "join", name, f"fr_journal_Q{leg}")
    for leg in LEGS:
        o, q = JP[leg]['O'], JP[leg]['Q']
        cyl("shaft_bore", -0.5, Z_GEAR + 1, o, "cut", name, f"fr_bore_O{leg}")
        cyl(SH_HEAD_D + 0.6, -0.5, SH_SEAT + 0.5, o, "cut", name, f"fr_cbore_O{leg}")
        cyl("pin_d", -0.5, Z_L2T + GAP + 1, q, "cut", name, f"fr_bore_Q{leg}")
        cyl("head_d", -0.5, 3.5, q, "cut", name, f"fr_cbore_Q{leg}")
    for f in (1, 2):
        if VARIANT == 'b':
            cyl("xpost_d", BASE_T - 0.3, XPOST_TOP - BASE_T + 0.3, XC[f], "join", name, f"fr_post_X{f}")
            cyl("pin_d", -0.5, XPOST_TOP + 1, XC[f], "cut", name, f"fr_bore_X{f}")
        else:
            cyl("pin_d", -0.5, Z_GEAR + 1, XC[f], "cut", name, f"fr_bore_X{f}")
        cyl("head_d", -0.5, 2.5, XC[f], "cut", name, f"fr_barb_recess_X{f}")
    deboss(name, "V8B" if VARIANT == 'b' else "V8", (D / 2, 12.0), 5.0, BASE_T, "label_frame")


def plate():
    name = cname('plate', 'F')
    new_component(name)
    COMPS.append(('plate', 'F'))
    discs = []
    for leg in LEGS:
        discs += [(JP[leg]['O'], 8.0), (JP[leg]['Q'], 7.0)]
    poly(name, disc_hull(discs), TP0, TP_T, "new", name)
    for leg in LEGS:
        o, q = JP[leg]['O'], JP[leg]['Q']
        cyl("o_stub_d", Z_L1T + GAP, TP0 - (Z_L1T + GAP) + 0.3, o, "join", name, f"tp_stub_O{leg}")
        cyl("post_d", Z_L2T + GAP, TP0 - (Z_L2T + GAP) + 0.3, q, "join", name, f"tp_stub_Q{leg}")
    poly("tp_window", [(8.0, YC - NOTCH_Y), (300, YC - NOTCH_Y), (300, YC + NOTCH_Y), (8.0, YC + NOTCH_Y)],
         TP0 - 0.5, TP_T + 1, "cut", name)
    for leg in LEGS:
        o, q = JP[leg]['O'], JP[leg]['Q']
        cyl("shaft_bore", Z_L1T, TP1 - Z_L1T + 0.5, o, "cut", name, f"tp_bore_O{leg}")
        cyl("pin_d", Z_L2T, TP1 - Z_L2T + 0.5, q, "cut", name, f"tp_bore_Q{leg}")
    deboss(name, "V8", (D / 2, 12.0), 5.0, TP1, "label_plate")
    ATTACH.append((occ('frame', 'F'), occ('plate', 'F')))


def key_bore(name, body, p, z0, h):
    """Double-D hole for the crank shaft: D5.3 clipped to 3.7 across the flats (0.15 per side)."""
    poly(name, circle_pts(p, SHAFT_D / 2 + CLEAR, 48, SHAFT_AF / 2 + CLEAR), z0, h, "cut", body)


def crank(leg):
    name = cname(('crank', leg), leg)
    new_component(name)
    COMPS.append((('crank', leg), leg))
    o, j1 = JP[leg]['O'], JP[leg]['J1']
    poly(f"gear_{leg}", gear_points(o, ZC, PH[leg]), Z_GEAR, GEAR_T, "new", name)
    cyl(2 * FLANGE_R, Z_GTOP - 0.3, Z_L1 - Z_GTOP + 0.3, j1, "join", name, f"flange_{leg}")
    cyl(2 * BOSS_R, Z_L1 - 0.3, Z_L1T - Z_L1 + 0.3, j1, "join", name, f"boss_{leg}")
    key_bore(f"key_{leg}", name, o, Z_GEAR - 0.5, Z_L1T - Z_GEAR + 1)
    ang = math.atan2(j1[1] - o[1], j1[0] - o[0]) + math.pi          # label opposite the boss
    deboss(name, leg, (o[0] + 13.5 * math.cos(ang), o[1] + 13.5 * math.sin(ang)), 4.0, Z_GTOP, f"label_{leg}",
           angle=math.degrees(ang) + 90)


def idler(f):
    name = cname('idler', f'X{f}')
    new_component(name)
    COMPS.append(('idler', f'X{f}'))
    x = XC[f]
    poly(f"gear_X{f}", gear_points(x, ZX, PH[f'X{f}']), Z_GEAR, IDLE_T, "new", name)
    if VARIANT == 'b':
        cyl("xpost_bore", Z_GEAR - 0.5, IDLE_T + 1, x, "cut", name, f"idler_bore_X{f}")
        cyl("xcap_bore", XPOST_TOP - XLIFT, Z_GEAR + IDLE_T - (XPOST_TOP - XLIFT) + 0.5, x, "cut", name, f"idler_cbore_X{f}")
    else:
        cyl("pin_d", Z_GEAR - 0.5, IDLE_T + 1, x, "cut", name, f"idler_bore_X{f}")
        cyl("head_d", Z_GEAR + IDLE_T - 1.6, 2.0, x, "cut", name, f"idler_cbore_X{f}")


def coupler(leg):
    name = cname('coupler', leg)
    new_component(name)
    COMPS.append(('coupler', leg))
    j = JP[leg]
    cyl(2 * RING_R, Z_L1, LINK_T, j['J1'], "new", name, f"ring_{leg}")
    for a, b in (('J1', 'B'), ('B', 'P'), ('J1', 'P')):
        slot(f"arm_{a}{b}_{leg}", j[a], j[b], BAR_W, Z_L1, LINK_T, "join", name)
    cyl("ring_bore", Z_L1 - 0.5, LINK_T + 1, j['J1'], "cut", name, f"bore_{leg}")
    for n in ('B', 'P'):
        cyl("press_d", Z_L1 - 0.5, LINK_T + 1, j[n], "cut", name, f"press_{n}_{leg}")
        # X2: 45 deg lead-in on both ends (finger 2's couplers are flipped, so the pin can enter either side)
        for z0, h, d0, d1, end in ((Z_L1 - 0.01, PRESS_CH + 0.01, f"press_d + {fx(2 * PRESS_CH + 0.02)} mm", "press_d", "bot"),
                                   (Z_L1 + LINK_T - PRESS_CH, PRESS_CH + 0.01, "press_d", f"press_d + {fx(2 * PRESS_CH + 0.02)} mm", "top")):
            c("solid.cone", diameter=d0, top_diameter=d1, height=f"{fx(h)} mm", base=[fx(j[n][0]), fx(j[n][1]), fx(z0)],
              operation="cut", targets=[name], name=f"press_{n}_{leg}_leadin_{end}")


def rocker(leg):
    name = cname('rocker', leg)
    new_component(name)
    COMPS.append(('rocker', leg))
    j = JP[leg]
    slot(f"bar_{leg}", j['Q'], j['B'], BAR_W, Z_L2, LINK_T, "new", name)
    cyl(EYE_Q, Z_L2, LINK_T, j['Q'], "join", name, f"eye_{leg}")
    cyl("journal_bore", Z_L2 - 0.5, LINK_T + 1, j['Q'], "cut", name, f"bore_Q_{leg}")
    cyl("pin_d", Z_L2 - 0.5, LINK_T + 1, j['B'], "cut", name, f"bore_B_{leg}")


def jaw(f):
    name = cname('jaw', f'F{f}')
    new_component(name)
    COMPS.append(('jaw', f'F{f}'))
    pa, pb = JP[f'A{f}']['P'], JP[f'B{f}']['P']
    assert abs(pa[1] - pb[1]) < 1e-9
    tip = (pb[0] + L_FREE, pb[1])
    slot(f"jaw_{f}", pa, tip, JAW_W, Z_L2, JAW_H, "new", name)
    cyl("pin_d", Z_L2 - 0.5, JAW_H + 1, pa, "cut", name, f"bore_A_{f}")
    cyl("head_d", Z_JAWT - 2.0, 2.5, pa, "cut", name, f"cbore_A_{f}")
    s0, s1 = (pb[0] - JAW_SLOT / 2, pb[1]), (pb[0] + JAW_SLOT / 2, pb[1])
    slot(f"slot_B_{f}", s0, s1, 3.4, Z_L2 - 0.5, JAW_H + 1, "cut", name)
    slot(f"cslot_B_{f}", s0, s1, 6.5, Z_JAWT - 2.0, 2.5, "cut", name)


def shaft(leg):
    key = 'shaft_knob' if leg == 'A1' else 'shaft'
    name = cname(key, leg)
    new_component(name)
    COMPS.append((key, leg))
    o = JP[leg]['O']
    cap = KNOB_T if leg == 'A1' else TP1
    snap_pin(name, o, SH_SEAT, cap, head_h=SH_HEAD_H, r=SHAFT_D / 2, head_d=f"{SH_HEAD_D} mm",
             shank_d="shaft_d", barb=(f"{SH_BARB_D} mm", f"{SH_BARB_TIP} mm"), slot_w=f"{SH_SLOT} mm",
             slot_down=SH_SLOT_DOWN, flat=SHAFT_D / 2 - SHAFT_AF / 2)
    ATTACH.append((occ(('crank', leg), leg), occ(key, leg)))


def knob():
    name = cname('knob', 'A1')
    new_component(name)
    COMPS.append(('knob', 'A1'))
    o = JP['A1']['O']
    pts = []
    for k in range(2 * KNURLS):
        r = KNOB_R if k % 2 == 0 else KNOB_R - 0.8
        a = math.pi * k / KNURLS
        pts.append((o[0] + r * math.cos(a), o[1] + r * math.sin(a)))
    poly("knob_rim", pts, KNOB_Z0, KNOB_H, "new", name)
    key_bore("knob_key", name, o, KNOB_Z0 - 0.5, KNOB_H + 1)
    ATTACH.append((occ('shaft_knob', 'A1'), occ('knob', 'A1')))


def pins():
    for leg in LEGS:
        j = JP[leg]
        n = cname('pin_q', leg)
        new_component(n)
        COMPS.append(('pin_q', leg))
        snap_pin(n, j['Q'], 3.0, TP1)
        ATTACH.append((occ('frame', 'F'), occ('pin_q', leg)))
        n = cname('pin_b', leg)
        new_component(n)
        COMPS.append(('pin_b', leg))
        press_pin(n, j['B'], Z_L1, Z_L2T + 0.2)
        ATTACH.append((occ('coupler', leg), occ('pin_b', leg)))
        n = cname('pin_p', leg)
        new_component(n)
        COMPS.append(('pin_p', leg))
        press_pin(n, j['P'], Z_L1, Z_JAWT - 2.0 + 0.2)
        ATTACH.append((occ('coupler', leg), occ('pin_p', leg)))
    for f in (1, 2):
        n = cname('pin_x', f'X{f}')
        new_component(n)
        COMPS.append(('pin_x', f'X{f}'))
        if VARIANT == 'b':      # head face on the post top, head top flush with the idler top
            snap_pin(n, XC[f], XPOST_TOP, 2.0, down=True, head_h=PHEAD_H, head_d="xcap_d")
        else:
            snap_pin(n, XC[f], Z_GEAR + IDLE_T - 1.6 + 0.2, 2.0, down=True, head_h=PHEAD_H)
        ATTACH.append((occ('frame', 'F'), occ('pin_x', f'X{f}')))


def rev(name, a, b, pt, z):
    c("joint.as_built", type="revolute", a=a, b=b, at={"point": [fx(pt[0]), fx(pt[1]), fx(z)], "z": [0, 0, 1]}, name=name)


def joints():
    c("component.activate", component=0)
    fr = occ('frame', 'F')
    for leg in LEGS:
        j = JP[leg]
        cr, co, ro = occ(('crank', leg), leg), occ('coupler', leg), occ('rocker', leg)
        rev(f"O_{leg}", fr, cr, j['O'], Z_GEAR)
        rev(f"J1_{leg}", cr, co, j['J1'], Z_L1)
        rev(f"B_{leg}", co, ro, j['B'], Z_L2)
        rev(f"Q_{leg}", fr, ro, j['Q'], Z_L2)
    for f in (1, 2):
        rev(f"X_{f}", fr, occ('idler', f'X{f}'), XC[f], Z_GEAR)
        ja = occ('jaw', f'F{f}')
        rev(f"PA_{f}", occ('coupler', f'A{f}'), ja, JP[f'A{f}']['P'], Z_L2)
        p = JP[f'B{f}']['P']
        c("joint.as_built", type="pin_slot", a=ja, b=occ('coupler', f'B{f}'),
          at={"point": [fx(p[0]), fx(p[1]), Z_L2], "z": [0, 0, 1], "x": [1, 0, 0]}, name=f"PB_{f}")
    for a, b, ra, rb in (("O_A1", "X_1", RC, RX), ("X_1", "O_B1", RX, RC), ("X_1", "X_2", RX, RX),
                         ("X_2", "O_A2", RX, RC), ("X_2", "O_B2", RX, RC)):
        c("joint.gear", a=a, b=b, ra=ra, rb=rb)
    for a, b in ATTACH:
        c("joint.as_built", type="rigid", a=a, b=b, name=f"fix_{b.split(':')[0]}")


def build():
    cmds.clear()
    ATTACH.clear()
    COMPS.clear()
    c("document.metadata.set", values={"part_number": ASSY, "description": parts.register()[ASSY]['Description'],
                                       "revision": REV(ASSY), "project": "strandbeest_gripper"})
    for name, expr, why in [
        ("pin_clear", f"{CLEAR} mm", "printed pin in printed hole, play per side (user rule 0.10-0.15)"),
        ("pin_d", "3.4 mm", "hole for the D3 printed pins"),
        ("ppin_d", "pin_d - 2 * pin_clear", "printed pin shank"),
        ("press_d", "ppin_d + 0.1 mm", "coupler bore, X3: drawn 0.05 mm per side loose; small vertical holes print ~0.1-0.2 small, so the printed hole (~Ø3.0-3.1) grips the Ø3.1 pin (X1 Ø2.9 and X2 Ø3.05 were too tight, user 2026-11-18 / 2026-11-22; NEEDS PRINT TEST)"),
        ("ppin_head_d", "5.5 mm", "printed pin head"),
        ("head_d", "6.5 mm", "counterbore for a pin head or barb"),
        ("barb_d", "4.0 mm", "snap barb: 0.3 mm catch per side over the D3.4 hole"),
        ("barb_tip_d", "2.8 mm", "barb lead-in"),
        ("snap_slot", f"{SLOT_W} mm", "slot that lets the two prongs close"),
        ("shaft_d", f"{SHAFT_D} mm", "crank shaft, turns in the base and the top plate"),
        ("shaft_bore", "shaft_d + 2 * pin_clear", "round bearing hole for the crank shaft"),
        ("journal_d", f"{JOURNAL_D} mm", "Q column journal the rocker turns on"),
        ("journal_bore", "journal_d + 2 * pin_clear", "rocker eye bore"),
        ("post_d", f"{POST_D} mm", "Q column post (frame) and stub (top plate)"),
        ("o_stub_d", f"{O_STUB_D} mm", "top-plate stub over the eccentric boss: second bearing of the crank shaft"),
        ("ring_bore", f"{fx(2 * RING_BORE_R)} mm", "coupler ring on the eccentric boss, 0.15 mm per side"),
    ] + ([
        ("xpost_d", f"{XPOST_D} mm", "v8b: solid frame post the Z24 idler turns on (replaces the D3 pin as bearing)"),
        ("xpost_bore", "xpost_d + 2 * pin_clear", "v8b: idler bore on the post, 0.15 mm per side"),
        ("xcap_d", f"{XCAP_D} mm", "v8b: cap-pin head, rests on the post top and covers the idler bore"),
        ("xcap_bore", "xcap_d + 0.6 mm", "v8b: counterbore in the idler top for the cap head"),
    ] if VARIANT == 'b' else []):
        c("parameters.add", name=name, expression=expr, comment=why)
    frame()
    plate()
    for leg in LEGS:
        crank(leg)
    for f in (1, 2):
        idler(f)
    for leg in LEGS:
        coupler(leg)
        rocker(leg)
    for f in (1, 2):
        jaw(f)
    for leg in LEGS:
        shaft(leg)
    knob()
    pins()
    joints()
    for key, i in COMPS:
        p = PN[key]
        c("component.metadata.set", component=cname(key, i), part_number=p,
          description=parts.register()[p]['Description'], revision=REV(p), bom_type="normal")
    done = set()
    for key, i in COMPS:
        p = PN[key]
        if p in done:
            continue
        done.add(p)
        for ext, cmd in (('step', 'file.export_step'), ('stl', 'file.export_stl'), ('3mf', 'file.export_3mf')):
            pr = dict(path=f"{VDIR}/exports/{parts.export(p, REV(p), ext)}", bodies=[cname(key, i)])
            if ext != 'step':
                pr["quality"] = "fine"
            c(cmd, **pr)
    return cmds


def write():
    for sub in ('cad', 'exports', 'docs'):
        os.makedirs(os.path.join(VDIR, sub), exist_ok=True)
    out = f"{VDIR}/cad/{parts.fname(ASSY)}.json"
    with open(out, 'w') as fh:
        fh.write('[\n' + ',\n'.join(' ' + json.dumps(x, separators=(',', ':')) for x in cmds) + '\n]\n')
    return out


if __name__ == '__main__':
    fb.check_against_jansen()
    build()
    out = write()
    print(f"v8: {out} {len(cmds)} steps; D {D:.3f}, YC {YC:.3f}, X1 {XC[1]}, ring R {RING_R:.2f}, boss R {BOSS_R:.2f}")
    print("phases", {k: round(v, 3) for k, v in PH.items()})
