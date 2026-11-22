"""Generate v2_rod-fourbar/cad/GRIP-9021_assy-finger-rod-fourbar.json: concept C6 made printable.

Concept C6 (Pollen Amazing Hand drive + BiDexHand-style coupling; user pick 2026-11-22 "working prototypes,
C5 + C6 only"): one DOF. The SCS0009 horn pushes a rod up to a lever on the proximal (MCP flexes); a crossed
link from a base lug (B0) to an ear on the middle (M1) makes the PIP follow; a crossed link from an ear on the
proximal (P1) to an ear on the distal (D1) makes the DIP follow. Link lengths: fingerlinks.py (asserted here).
Hand first: a printed dummy servo (GRIP-0156) slides into the cradle, the horn turns on its stub, and you turn
the horn by its lever. Servo stage: the SCS0009 replaces the dummy, the same horn goes on its spline.

Layers in Y (mm; the finger is |y| <= 9, base cheeks 9.3 .. 12.3 each side):
  -Y: PIP link -17.3 .. -14.3 | M1 ear / B0 lug + boss -14.0 .. -9.3
  +Y: lever arm 2 .. 9, L boss 9 .. 12.3 | P1 / D1 ears 9.3 .. 14.0 | rod 12.6 .. 16.6 | DIP link 14.3 .. 17.3 |
      horn 16.9 .. 22.45 (gear collar at 22.75)
Every ear may cover its own joint's pin end: it has a pocket round that axis. Ear pins have their barb
recessed in the ear's inner face, so nothing pokes into the finger's own width.

Print: proximal on its palm (-X down: the lever arm grows up), middle and distal on their back (+X down),
links / rod / horn flat, base dovetail down, dummy on its back face, pins on a flat.

    python3 articulated_finger/tools/gen_v2.py
    tools/build.sh articulated_finger/v2_rod-fourbar
    python3 articulated_finger/tools/verify_v2.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import finger_common as f  # noqa: E402
import fingerlinks as fl  # noqa: E402
from finger_common import c, box, cyl_y, fx, prism_xz, teardrop_y  # noqa: E402

VDIR = 'articulated_finger/v2_rod-fourbar'
ASSY = 'GRIP-9021'
PN = {'base': 'GRIP-0148', 'proximal': 'GRIP-0149', 'middle': 'GRIP-0150', 'distal': 'GRIP-0151',
      'horn': 'GRIP-0152', 'rod': 'GRIP-0153', 'link1': 'GRIP-0154', 'link2': 'GRIP-0155', 'dummy': 'GRIP-0156',
      'pin_ear': 'GRIP-0157', 'pin_b0': 'GRIP-0158', 'pin_l': 'GRIP-0159',
      'pin_mcp': 'GRIP-0144', 'pin_k': 'GRIP-0145'}          # MCP / knuckle pins: the v1 parts, they fit as is
A = f.Assy(VDIR, ASSY, PN)
Q = fl.P

# y layers
EAR = (9.3, 14.0)             # ear plate (+Y; -Y mirrored)
WEB = 8.7                     # ears join their phalanx 0.3 into it, only over its own footprint (the pad)
ROD = (12.6, 16.6)
LINK1 = (-17.3, -14.3)
LINK2 = (14.3, 17.3)
HORN = (16.9, 22.45)
ARM = (2.0, 9.0)              # MCP lever arm on the proximal (inside the finger's width)
LBOSS = (8.7, 12.3)           # boss round L only (shares y with the +Y base cheek: kept off it in x / radius)
COLLAR_GAP = 0.3
OFF = HORN[1] + COLLAR_GAP + 8.75      # servo tab plane (gear collar 8.75 in front of it): 31.5
SPLINE_TOP = OFF - 11.65
BAR_W = 7.0
EAR_R = fl.EAR_R
CB_D, CB_DEPTH = 6.5, 1.9     # barb counterbore in an ear's inner face (barb top 0.2 inside it)
HEAD_CB = 1.85                # pin-head counterbore in the rod (H end): head 1.5 sits 0.1 off its floor, 0.25 inside
POCKET_HEAD, POCKET_BARB = 6.3, 5.2   # pockets round a knuckle pin end that an ear covers (head D5.5, barb D4)
HUB_D, HORN_SCREW, HORN_HEAD_D, HORN_HEAD_H, HORN_PLATE = 10.0, 2.4, 4.4, 1.6, 1.0
HANDLE = dict(r=22.0, w=7.0, pad=10.0, angle=200.0)    # hand lever on the horn (deg at horn 0)
DUMMY_CLR, STUB_D = 0.1, 3.7

MCP_W = fl.MCP
PIP_W = (0.0, f.ZJ[1])
DIP_W = (0.0, f.ZJ[2])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


B0 = Q['B0']
M1 = add(PIP_W, Q['M1'])
P1 = add(PIP_W, Q['P1'])
D1 = add(DIP_W, Q['D1'])
LW = add(MCP_W, Q['L'])
H = fl.horn_pt(0.0)


def circle(p, r, n=24):
    return [(p[0] + r * math.cos(2 * math.pi * k / n), p[1] + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def hull(pts):
    return fl._hull([(round(x, 4), round(z, 4)) for x, z in pts])


def stadium(a, b, w, n=12):
    """Slot outline round segment a-b, width w, in (x, z)."""
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    out = []
    for p, a0 in ((b, ang - math.pi / 2), (a, ang + math.pi / 2)):
        out += [(p[0] + w / 2 * math.cos(a0 + math.pi * k / n), p[1] + w / 2 * math.sin(a0 + math.pi * k / n))
                for k in range(n + 1)]
    return out


def yr(rng, s):
    """A +Y range mirrored to -Y when s < 0."""
    return rng if s > 0 else (-rng[1], -rng[0])


def ear(body, pin, joint, pad, s, pocket_d, apex):
    """Ear plate (y EAR, mirrored by s) round pin, joined on pad (world rect, inside the body's own footprint),
    with a pocket round the joint axis it may cover and the pin hole + barb counterbore."""
    (x0, z0), (x1, z1) = pad
    poly = hull(circle(pin, EAR_R) + [(x0, z0), (x1, z0), (x1, z1), (x0, z1)])
    box((x0, x1), yr((WEB, EAR[0] + 0.3), s), (z0, z1), "join", body, f"{body}_ear_web")
    prism_xz(poly, *yr(EAR, s), "join", body, f"{body}_ear")
    pd = pocket_d
    teardrop_y(pd, joint[0], joint[1], *yr((EAR[0] - 0.01, EAR[0] + 2.2), s), body, f"{body}_ear_axis_pocket", apex=apex)
    teardrop_y(f.PIN_HOLE, pin[0], pin[1], *yr((EAR[0] - 0.5, EAR[1] + 0.5), s), body, f"{body}_ear_pin_hole", apex=apex)
    teardrop_y(CB_D, pin[0], pin[1], *yr((EAR[0] - 0.5, EAR[0] + CB_DEPTH), s), body, f"{body}_ear_barb_cb", apex=apex)


def base():
    b = A.new('base', 'F', grounded=True)
    info = f.base(b, OFF, bars=False, centre_dovetail=True)
    # B0 lug on the -Y cheek (dorsal, beside the MCP), 45 deg underside down onto the dorsal post
    lo = (B0[0], B0[1] - EAR_R - 0.5)
    qz = lo[1] - (B0[0] - f.TOWER_X)
    poly = hull(circle(B0, EAR_R + 0.5) + [(f.POST_X0 + 0.4, qz), (f.POST_X0 + 0.4, B0[1] + EAR_R + 0.5),
                                          (f.TOWER_X, qz - 0.01)])
    prism_xz(poly, -f.CHEEK_Y1, -f.CHEEK_Y0, "join", b, "B0Lug")
    cyl_y(2 * EAR_R, B0[0], B0[1], EAR[1] * -1, -f.CHEEK_Y1 + 0.3, "join", b, "B0Boss")
    teardrop_y(f.PIN_HOLE, B0[0], B0[1], -EAR[1] - 0.5, -f.CHEEK_Y0 + 0.5, b, "B0PinHole", apex=(0, 1))
    return info


def proximal():
    n = A.new('proximal', 'P')
    f.phalanx(n, 0, ch=False, apex=(1, 0))
    # MCP lever arm (dorsal): from the back face to L, kept 0.5 off the +Y cheek's round top
    poly = hull(circle(LW, EAR_R - 0.4) + [(f.R - 0.5, MCP_W[1] + 4.5), (f.R - 0.5, MCP_W[1] + 18.0)])
    prism_xz(poly, *ARM, "join", n, f"{n}_lever_arm")
    cyl_y(2 * EAR_R, LW[0], LW[1], *LBOSS, "join", n, f"{n}_lever_boss")
    teardrop_y(f.PIN_HOLE, LW[0], LW[1], ARM[0] - 0.5, LBOSS[1] + 0.5, n, f"{n}_lever_pin_hole", apex=(1, 0))
    ear(n, P1, PIP_W, ((-f.R, PIP_W[1] - 20.0), (f.R, PIP_W[1] - 9.5)), 1, POCKET_BARB, (1, 0))


def middle():
    n = A.new('middle', 'M')
    f.phalanx(n, 1, ch=False)
    ear(n, M1, PIP_W, ((-f.R, PIP_W[1] + 9.5), (f.R, PIP_W[1] + 20.0)), -1, POCKET_HEAD, (-1, 0))


def distal():
    n = A.new('distal', 'D')
    f.phalanx(n, 2, ch=False)
    ear(n, D1, DIP_W, ((-f.R, DIP_W[1] + 9.5), (f.R, DIP_W[1] + 14.0)), 1, POCKET_BARB, (-1, 0))


def bar(key, inst, a, b, yrng, cb_at=None, cb_side=None):
    n = A.new(key, inst)
    prism_xz(stadium(a, b, BAR_W), *yrng, "new", n, f"{n}_bar")
    for k, p in (("a", a), ("b", b)):
        cyl_y(f.PIN_HOLE, p[0], p[1], yrng[0] - 0.5, yrng[1] + 0.5, "cut", n, f"{n}_hole_{k}")
    if cb_at is not None:
        y0 = yrng[0] - 0.5 if cb_side < 0 else yrng[1] - HEAD_CB
        y1 = yrng[0] + HEAD_CB if cb_side < 0 else yrng[1] + 0.5
        cyl_y(CB_D, cb_at[0], cb_at[1], y0, y1, "cut", n, f"{n}_head_cb")
    return n


def horn():
    n = A.new('horn', 'S')
    sv = fl.SERVO
    ha = math.radians(Q['phi0'] + HANDLE['angle'])
    tip = (sv[0] + HANDLE['r'] * math.cos(ha), sv[1] + HANDLE['r'] * math.sin(ha))
    poly = hull(circle(sv, HUB_D / 2) + circle(H, EAR_R))
    prism_xz(poly, *HORN, "new", n, f"{n}_arm")
    prism_xz(stadium(sv, tip, HANDLE['w']), *HORN, "join", n, f"{n}_handle")
    cyl_y(HANDLE['pad'], tip[0], tip[1], HORN[0], HORN[1], "join", n, f"{n}_handle_pad")
    # spline press bore (D4.0 spline, drawn +0.1), M2 screw through a 1.0 plate, head counterbore on the -Y face
    bore0 = HORN[0] + HORN_HEAD_H + HORN_PLATE
    cyl_y(4.0 + 0.1, sv[0], sv[1], bore0, HORN[1] + 0.5, "cut", n, f"{n}_spline_bore")
    cyl_y(HORN_SCREW, sv[0], sv[1], HORN[0] - 0.5, bore0 + 0.01, "cut", n, f"{n}_screw_hole")
    cyl_y(HORN_HEAD_D, sv[0], sv[1], HORN[0] - 0.5, HORN[0] + HORN_HEAD_H, "cut", n, f"{n}_screw_head")
    cyl_y(f.PIN_HOLE, H[0], H[1], HORN[0] - 0.5, HORN[1] + 0.5, "cut", n, f"{n}_pin_hole")
    cyl_y(CB_D, H[0], H[1], HORN[1] - CB_DEPTH, HORN[1] + 0.5, "cut", n, f"{n}_barb_cb")
    return n


def dummy():
    """Hand-operation stand-in for the servo: fills the cradle pocket (0.1 per side), carries a D3.7 stub where
    the spline is (the horn turns on it). Parked beside the base in the assembly (it shares the servo's place)."""
    n = A.new('dummy', 'X')
    dx = 60.0                                  # parked +X of the base
    cx, sx = f.CASE['x'] + f.SERVO_CLR - DUMMY_CLR, f.ZS
    z0, z1 = f.ZS + f.CASE['z0'] - f.SERVO_CLR + DUMMY_CLR, f.ZS + f.CASE['z1'] + f.SERVO_CLR - DUMMY_CLR
    y1 = OFF + f.CASE['y_in'] + f.SERVO_CLR - 0.15
    box((dx - cx, dx + cx), (OFF, y1), (z0, z1), "new", n, f"{n}_case")
    box((dx - 5.9, dx + 5.9), (OFF - 8.45, OFF + 0.3), (sx - 5.5, sx + 5.5), "join", n, f"{n}_front")
    cyl_y(STUB_D, dx, sx, SPLINE_TOP, OFF - 8.45 + 0.3, "join", n, f"{n}_stub")
    cyl_y(1.6, dx, sx, SPLINE_TOP - 0.5, SPLINE_TOP + 5.0, "cut", n, f"{n}_screw_pilot")
    return n


def build():
    A.comps.clear()
    A.header()
    fl.check()
    for name, expr, why in [
        ("pin_clear", f"{f.CLEAR} mm", "printed pin in printed hole, play per side (user rule 0.10-0.15)"),
        ("pin_hole", f"{f.PIN_HOLE} mm", "knuckle / link pin hole, D3.1 snap pins"),
        ("side_gap", f"{f.SG} mm", "tongue / cheek, finger / base cheek, layer to layer"),
        ("knuckle_gap", f"{f.RG} mm", "radial gap around the rounded knuckle ends"),
        ("bar_w", f"{BAR_W} mm", "rod and link width"),
        ("ear_r", f"{EAR_R} mm", "boss radius round a link pin on an ear / lug / horn"),
    ]:
        c("parameters.add", name=name, expression=expr, comment=why)
    base()
    proximal()
    middle()
    distal()
    horn()
    bar('rod', 'R', H, LW, ROD, cb_at=H, cb_side=-1)
    bar('link1', 'L1', B0, M1, LINK1)
    bar('link2', 'L2', P1, D1, LINK2)
    dummy()
    # pins
    n = A.new('pin_mcp', 'MCP')
    f.snap_pin_y(n, 0, f.Z_MCP, -f.CHEEK_Y1 - f.HEAD_GAP, f.CHEEK_Y1)
    for j, inst in ((1, 'PIP'), (2, 'DIP')):
        n = A.new('pin_k', inst)
        f.snap_pin_y(n, 0, f.ZJ[j], -f.W / 2 - f.HEAD_GAP, f.W / 2)
    n = A.new('pin_b0', 'B0')
    f.snap_pin_y(n, B0[0], B0[1], LINK1[0] - f.HEAD_GAP, -f.CHEEK_Y0)
    cap_in = EAR[0] + CB_DEPTH                            # ear barb counterbore floor
    n = A.new('pin_ear', 'M1')
    f.snap_pin_y(n, M1[0], M1[1], LINK1[0] - f.HEAD_GAP, -cap_in)
    for inst, p in (('P1', P1), ('D1', D1)):
        n = A.new('pin_ear', inst)
        f.snap_pin_y(n, p[0], p[1], LINK2[1] + f.HEAD_GAP, cap_in, head_pos=True)
    n = A.new('pin_ear', 'H')
    f.snap_pin_y(n, H[0], H[1], ROD[0] + HEAD_CB - f.HEAD_GAP, HORN[1] - CB_DEPTH)
    n = A.new('pin_l', 'L')
    f.snap_pin_y(n, LW[0], LW[1], ROD[1] + f.HEAD_GAP, ARM[0], head_pos=True)
    A.servo(OFF)
    # joints
    c("component.activate", component=0)
    o = A.occ
    fr = o('base', 'F')
    f.rev_y("MCP", fr, o('proximal', 'P'), f.ZJ[0])
    f.rev_y("PIP", o('proximal', 'P'), o('middle', 'M'), f.ZJ[1])
    f.rev_y("DIP", o('middle', 'M'), o('distal', 'D'), f.ZJ[2])
    f.rev_y("HORN", fr, o('horn', 'S'), fl.SERVO[1], x=fl.SERVO[0])
    f.rev_y("H", o('horn', 'S'), o('rod', 'R'), H[1], x=H[0])
    f.rev_y("L", o('rod', 'R'), o('proximal', 'P'), LW[1], x=LW[0])
    f.rev_y("B0", fr, o('link1', 'L1'), B0[1], x=B0[0])
    f.rev_y("M1", o('link1', 'L1'), o('middle', 'M'), M1[1], x=M1[0])
    f.rev_y("P1", o('proximal', 'P'), o('link2', 'L2'), P1[1], x=P1[0])
    f.rev_y("D1", o('link2', 'L2'), o('distal', 'D'), D1[1], x=D1[0])
    for a, b in ((fr, o('pin_mcp', 'MCP')), (o('proximal', 'P'), o('pin_k', 'PIP')), (o('middle', 'M'), o('pin_k', 'DIP')),
                 (fr, o('pin_b0', 'B0')), (o('middle', 'M'), o('pin_ear', 'M1')), (o('proximal', 'P'), o('pin_ear', 'P1')),
                 (o('distal', 'D'), o('pin_ear', 'D1')), (o('horn', 'S'), o('pin_ear', 'H')),
                 (o('proximal', 'P'), o('pin_l', 'L')), (fr, o('dummy', 'X'))):
        f.rigid(a, b)
    A.finish()
    return f.cmds


if __name__ == '__main__':
    build()
    print(A.write(), len(f.cmds), 'steps; OFF', OFF, 'lengths', {k: round(v, 3) for k, v in fl.lengths().items()})
