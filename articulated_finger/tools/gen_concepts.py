"""Massing models for six articulated-finger concepts (concept stage: no part numbers, no exports).

    python3 articulated_finger/tools/gen_concepts.py            -> articulated_finger/concepts/cad/C<n>_<name>.json
    solidcraft-cli run <json> --save <sc>                        (tools/run_concepts.sh does all six + checks)

Every concept shares one base: the GRIP-0002 dovetail (34 -> 28 wide, 6 tall, 40 long along X, same numbers)
plus a tower that holds a Feetech SCS0009 (base/feetech_scs0009, LIB-0010) with its output axis along -Y.
The finger stands up along +Z and flexes in the XZ plane, palm side = -X. It is centred on y = 0 (width 18).

Frame of the servo: SOURCE.md's Z-up placement, turned +90 deg about X (output axis -> -Y), moved by
(0, OFF, ZS). In this frame the tab underside (mounting face) is the plane y = OFF, the case hangs to +Y
(y OFF .. OFF + 16.8), the spline top is at y = OFF - 11.65 and the case spans z ZS - 17.35 .. ZS + 5.95.

These are massing models: phalanges are blocks with their joint axes, mechanism parts are drawn as simple
solids so the layout, the servo envelope and the size can be checked. No fits, no print orientation.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'concepts', 'cad')

# ---------------------------------------------------------------- shared numbers (mm)
DT = dict(dt_len=40.0, dt_bot=34.0, dt_top=28.0, dt_h=6.0, head_h=4.0)   # copied from GRIP-0002
Z_HEAD = DT['dt_h'] + DT['head_h']          # 10: top of the dovetail head
W = 18.0                                    # finger width (Y)
T = 16.0                                    # phalanx thickness (X), palm face x = -T/2
L = (45.0, 25.0, 22.0)                      # proximal, middle, distal (92 total, human index ~ 91)
ZS = 34.5                                   # servo output axis: tab tips 0.5 over a 2 mm plinth
CASE = dict(x=6.05, y_out=-11.65, y_in=16.8, z0=-17.35, z1=5.95, tab_z0=-21.95, tab_z1=10.55, tab_t=1.6)
SERVO_CLR = 0.5                             # SOURCE.md: keep 0.5 around the case
DRV_GAP = 0.1                               # spool / crank / horn drawn 0.1 off the spline top (check gap)
TOWER_X = 10.0                              # tower half-width (X)

cmds = []


def c(command, **params):
    cmds.append({"command": command, "params": params})


def fx(v):
    return round(v, 4)


def box(x, y, z, op, body, name):
    p = dict(length=f"{fx(x[1] - x[0])} mm", width=f"{fx(y[1] - y[0])} mm", height=f"{fx(z[1] - z[0])} mm",
             center=[fx((x[0] + x[1]) / 2), fx((y[0] + y[1]) / 2), fx((z[0] + z[1]) / 2)], operation=op, name=name)
    p.update({"body_name": body} if op == "new" else {"targets": [body]})
    c("solid.box", **p)


def cyl_y(d, x, z, y0, y1, op, body, name):
    p = dict(diameter=f"{fx(d)} mm", height=f"{fx(y1 - y0)} mm", base=[fx(x), fx(y0), fx(z)], axis=[0, 1, 0],
             operation=op, name=name)
    p.update({"body_name": body} if op == "new" else {"targets": [body]})
    c("solid.cylinder", **p)


def cyl_z(d, x, y, z0, z1, op, body, name):
    p = dict(diameter=f"{fx(d)} mm", height=f"{fx(z1 - z0)} mm", base=[fx(x), fx(y), fx(z0)], axis=[0, 0, 1],
             operation=op, name=name)
    p.update({"body_name": body} if op == "new" else {"targets": [body]})
    c("solid.cylinder", **p)


# ---------------------------------------------------------------- shared base
def base(off, z_mcp, fork):
    """Dovetail + servo tower. fork=2 adds a fork post that carries the MCP axis at z_mcp above the servo."""
    for k, v in DT.items():
        c("parameters.add", name=k, expression=f"{v} mm", comment="copied from GRIP-0002 (tester dovetail)")
    c("sketch.create", plane="YZ", offset="-dt_len/2", name="DovetailSketch")
    c("sketch.line", points=[["-dt_bot/2", 0], ["dt_bot/2", 0], ["dt_top/2", "dt_h"], ["dt_top/2", "dt_h + head_h"],
                             ["-dt_top/2", "dt_h + head_h"], ["-dt_top/2", "dt_h"]], closed=True)
    c("sketch.finish")
    c("solid.extrude", distance="dt_len", operation="new", body_name="base", name="Dovetail")
    # plinth on the dovetail head (under the servo case), then a cradle around the hanging case (y >= OFF)
    z_case0 = ZS + CASE['z0'] - SERVO_CLR
    z_plinth = ZS + CASE['tab_z0'] - SERVO_CLR      # tabs reach lower than the case: plinth stays under them
    y_end = off + CASE['y_in'] + SERVO_CLR + 2.0
    z_top = ZS + CASE['tab_z1'] + 2.0
    box((-TOWER_X, TOWER_X), (-DT['dt_top'] / 2, y_end), (Z_HEAD - 0.3, z_plinth), "join", "base", "Plinth")
    box((-TOWER_X, TOWER_X), (off, y_end), (Z_HEAD - 0.3, z_top), "join", "base", "Cradle")
    box((-CASE['x'] - SERVO_CLR, CASE['x'] + SERVO_CLR), (off - 0.1, off + CASE['y_in'] + SERVO_CLR),
        (z_case0, ZS + CASE['z1'] + SERVO_CLR), "cut", "base", "ServoPocket")
    if fork:
        # -Y cheek stands on the plinth; the +Y cheek hangs off the cradle top (it must clear the servo top case)
        box((-T / 2, T / 2), (-W / 2 - 3.3, -W / 2 - 0.3), (Z_HEAD - 0.3, z_mcp + 6.0), "join", "base", "ForkCheek_b")
        if fork == 2:
            box((-T / 2, T / 2), (W / 2 + 0.3, off + 3.0), (z_top - 0.3, z_mcp + 6.0), "join", "base", "ForkCheek_a")
        cyl_y(3.4, 0, z_mcp, -W / 2 - 3.4, W / 2 + 3.4, "cut", "base", "MCPAxleHole")
    return z_top


OFFS = {}


def servo(off):
    OFFS['last'] = off
    c("file.insert_step", path="base/feetech_scs0009/LIB-0010_servo-scs0009.step", name="LIB-0010_servo-scs0009")
    c("occurrence.move", occurrence="LIB-0010_servo-scs0009:1", move_grounded=True,
      matrix=servo_matrix(off))


def phalanges(z_mcp, gap=0.6, root=-T / 2):
    """Three straight phalanges standing on the MCP axis; joint axes along Y at the segment ends."""
    z = z_mcp
    names = []
    for i, (n, l) in enumerate(zip(("proximal", "middle", "distal"), L)):
        z0, z1 = z + (gap / 2 if i else root), z + l - (gap / 2 if i < 2 else 0)
        box((-T / 2, T / 2), (-W / 2, W / 2), (z0, z1 - (T / 2 if i == 2 else 0)), "new", n, f"{n}_block")
        if i == 2:  # rounded tip, ends at z1
            cyl_y(T, 0, z1 - T / 2, -W / 2, W / 2, "join", n, "tip_round")
        names.append((n, z, z + l))
        z += l
    return names   # (body, z of its base joint, z of its tip joint)


def finish(cid):
    c("document.metadata.set", values={"part_number": f"CONCEPT-{cid}", "description": "MASSING, ARTICULATED FINGER",
                                       "revision": "-", "project": "articulated_finger"})


# ---------------------------------------------------------------- the six concepts
def n1_geared():
    """N1: servo spline IS the MCP. Idler-gear chains in the phalanges couple PIP and DIP 1:1 to the MCP."""
    off = W / 2 + 0.6 + 11.65        # hub of the proximal sits on the spline end face
    base(off, ZS, fork=False)
    servo(off)
    ph = phalanges(ZS)
    # MCP sun gear fixed to the base (around the servo collar), pitch d 8.5 (m0.5 z17)
    box((CASE["x"] + SERVO_CLR + 0.2, TOWER_X), (W / 2 + 0.6, off + 0.5), (ZS - 3.0, ZS + 3.0), "join", "base", "MCP_gear_arm")
    box((4.0, TOWER_X), (W / 2 + 0.6, W / 2 + 3.0), (ZS - 3.0, ZS + 3.0), "join", "base", "MCP_gear_arm_inner")
    cyl_y(9.5, 0, ZS, W / 2 + 0.6, W / 2 + 3.0, "join", "base", "MCP_fixed_gear")
    cyl_y(7.0, 0, ZS, W / 2 + 0.5, W / 2 + 3.1, "cut", "base", "MCP_gear_bore")
    # idler-gear chain pockets on the +Y face of proximal and middle (pitch spacing 8.5 = m0.5 z17)
    for body, z0, z1 in ph[:2]:
        k = 1
        while z0 + k * 8.5 <= z1 + 0.01:
            cyl_y(9.5, 0, z0 + k * 8.5, W / 2 - 3.0, W / 2 + 0.01, "cut", body, f"{body}_gear_pocket_{k}")
            k += 1
    cyl_y(4.0, 0, ZS, -W / 2, W / 2, "join", "proximal", "hub_on_spline")


def n2_spine():
    """N2: push-pull spine. A PETG/TPU band in a palm-side channel; the servo crank pushes (extend) and pulls (curl)."""
    off = 4.0 + 11.65 + DRV_GAP      # crank disc centred on y = 0
    z_mcp = ZS + 26.0
    base(off, z_mcp, fork=2)
    servo(off)
    ph = phalanges(z_mcp)
    for body, z0, z1 in ph:
        box((-T / 2 - 0.1, -T / 2 + 2.6), (-4.0, 4.0), (z0 - 10, z1 + 10), "cut", body, f"{body}_spine_channel")
    cyl_y(20.0, 0, ZS, -4.0, 4.0, "new", "crank", "crank_disc")
    box((-T / 2 + 0.3, -T / 2 + 1.5), (-3.5, 3.5), (ZS + 8.0, ph[2][2] - 4.0), "new", "spine", "spine_band")


def n3_rolling():
    """N3: rolling-contact (Hillberry-style) joints held by crossed straps; one tendon + dorsal elastic."""
    off = 4.0 + 11.65 + DRV_GAP
    z_mcp = ZS + 26.0
    base(off, z_mcp, fork=2)
    servo(off)
    R = T / 2
    ph, z = [], z_mcp
    for i, (n, l) in enumerate(zip(("proximal", "middle", "distal"), L)):
        z0 = z - R if i == 0 else z + 0.1          # proximal root wraps the MCP pin
        z1 = z + l - 0.1
        lo = z0 if i == 0 else z0 + R
        box((-T / 2, T / 2), (-W / 2, W / 2), (lo, z1 - R), "new", n, f"{n}_block")
        if i:
            cyl_y(T, 0, z0 + R, -W / 2, W / 2, "join", n, f"{n}_rolling_low")
        cyl_y(T, 0, z1 - R, -W / 2, W / 2, "join", n, f"{n}_rolling_high")
        ph.append((n, z, z + l))
        z += l
    for body, z0, z1 in ph[:2]:
        box((T / 2 + 0.1, T / 2 + 0.9), (-W / 2 + 1, W / 2 - 1), (z1 - 6.0, z1 + 6.0), "new", f"strap_{body}",
            f"strap_{body}")
    for body, z0, z1 in ph:
        box((-T / 2 + 1.5, -T / 2 + 3.5), (-1.0, 1.0), (z0 - 10, z1 + 10), "cut", body, f"{body}_tendon_hole")
    cyl_y(12.0, 0, ZS, -4.0, 4.0, "new", "spool", "spool")


def r1_flexure():
    """R1 (Yale OpenHand T42 principle): rigid segments joined by TPU flexure strips; one tendon to the tip."""
    off = 4.0 + 11.65 + DRV_GAP
    z_mcp = ZS + 26.0
    z_top = base(off, z_mcp, fork=False)
    box((-T / 2, T / 2), (-W / 2, -4.6), (Z_HEAD - 0.3, z_top), "join", "base", "RootColumn")
    box((-T / 2, T / 2), (-W / 2, off + 3.0), (z_top - 0.3, z_mcp), "join", "base", "RootBlock")
    servo(off)
    ph = phalanges(z_mcp, gap=6.0, root=1.0)
    fl = ((T / 2 - 4.5, T / 2 - 3.0), (-W / 2 + 1, W / 2 - 1), (z_mcp - 5.0, ph[2][2] - 6.0))
    for body in ("base",) + tuple(p[0] for p in ph):   # slots 0.1 bigger all round (check gap; TPU is pressed in)
        box((fl[0][0] - 0.1, fl[0][1] + 0.1), (fl[1][0] - 0.1, fl[1][1] + 0.1), (fl[2][0] - 0.1, fl[2][1] + 0.1),
            "cut", body, f"{body}_flexure_slot")
    box(*fl, "new", "flexure", "tpu_flexure_strip")
    for body, z0, z1 in ph:
        box((-T / 2 + 1.5, -T / 2 + 3.5), (-1.0, 1.0), (z0 - 10, z1 + 10), "cut", body, f"{body}_tendon_hole")
    cyl_y(12.0, 0, ZS, -4.0, 4.0, "new", "spool", "spool")


def r2_raptor():
    """R2 (e-NABLE Raptor principle): pin joints, palm-side cord, dorsal elastic return; hand slider or spool."""
    off = 4.0 + 11.65 + DRV_GAP
    z_mcp = ZS + 26.0
    base(off, z_mcp, fork=2)
    servo(off)
    ph = phalanges(z_mcp)
    for body, z0, z1 in ph:
        cyl_y(3.4, 0, z0, -W / 2 - 1, W / 2 + 1, "cut", body, f"{body}_pin_hole")
        box((-T / 2 + 1.5, -T / 2 + 3.5), (-1.0, 1.0), (z0 - 10, z1 + 10), "cut", body, f"{body}_cord_hole")
        box((T / 2 - 3.5, T / 2 - 1.5), (-1.0, 1.0), (z0 - 10, z1 + 10), "cut", body, f"{body}_elastic_hole")
    cyl_y(12.0, 0, ZS, -4.0, 4.0, "new", "spool", "spool")


def r3_rod_fourbar():
    """R3 (Amazing Hand drive + BiDexHand DIP coupling): servo horn -> push rod -> MCP lever; crossed four-bar
    links couple DIP to PIP; a second rod from the base couples PIP to MCP (one servo curls all three)."""
    off = W / 2 + 3.0 + DRV_GAP + 11.65   # horn between finger (+Y face) and spline top
    z_mcp = ZS + 26.0
    base(off, z_mcp, fork=1)         # -Y cheek only: the +Y side is the rod/lever plane
    servo(off)
    ph = phalanges(z_mcp)
    y_rod = (W / 2 + 0.6, W / 2 + 3.0)
    box((-8.0, 8.0), y_rod, (ZS - 2.0, ZS + 2.0), "new", "horn", "servo_horn")
    box((6.0, 8.0), y_rod, (ZS + 2.3, z_mcp - 2.3), "new", "rod_mcp", "push_rod_mcp")
    box((-2.0, 9.0), (W / 2 - 0.5, y_rod[1]), (z_mcp - 2.0, z_mcp + 2.0), "join", "proximal", "mcp_lever")
    yl = (-W / 2 - 2.6, -W / 2 - 0.4)
    box((-7.0, -5.0), yl, (z_mcp + 6.5, ph[1][1] + 3.0), "new", "link_pip", "pip_coupler")
    box((5.0, 7.0), yl, (ph[1][1] - 3.0, ph[2][1] + 3.0), "new", "link_dip", "dip_crossed_link")


def prism_xz(pts, y0, length, op, body, name):
    """Profile in (x, z), extruded along +Y from y0 (XZ sketch: sketch x = +X, sketch y = -Z, normal +Y)."""
    c("sketch.create", plane="XZ", offset=f"{fx(y0)} mm", name=f"{name}_sk")
    c("sketch.line", points=[[fx(x), fx(-z)] for x, z in pts], closed=True)
    c("sketch.finish")
    p = dict(distance=f"{fx(length)} mm", operation=op, name=name)
    p.update({"body_name": body} if op == "new" else {"targets": [body]})
    c("solid.extrude", **p)


def clip(poly, a, b, k):
    """Keep the part of poly with a*x + b*z >= k (Sutherland-Hodgman, one half-plane)."""
    out = []
    for i, p in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        fp, fq = a * p[0] + b * p[1] - k, a * q[0] + b * q[1] - k
        if fp >= 0:
            out.append(p)
        if (fp >= 0) != (fq >= 0):
            t = fp / (fp - fq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


# ---------------------------------------------------------------- TPU fin-ray pads (C7)
# One pad per phalanx on the palm face (-X). Fin-ray section in XZ: a back flank on the phalanx, a front flank
# that touches the object, ribs between them leaning toward the tip. Pushing the front flank makes it wrap the
# object (fin-ray effect), which is what gives the flesh-like contact area.
# Swap: the pad clips on like a phone case. Side lips run back along the phalanx sides in a 1.1 mm recess
# (flush with the 18 mm width) and end in hook teeth that drop into side grooves. The recess ends stop the pad
# along the finger. Peel the lips off to remove; press on to fit. No tools, the joints stay assembled.
PAD = dict(depth=6.0, back=1.0, front=1.0, rib=0.8, pitch=4.0, lean=15.0, end_chamfer=3.0, gap=0.1,
           lip=1.1, lip_x=-4.2, tooth=(-5.0, -4.2), tooth_in=0.6, half_w=W / 2)


def pad_fin_ray(body, za, zb):
    """TPU pad on the palm face between za and zb, plus the matching recess and grooves in the phalanx."""
    import math
    P, g = PAD, PAD['gap']
    xb = -T / 2 - g                      # pad back face (0.1 off the palm face)
    xf = xb - P['depth']                 # contact face
    a = P['end_chamfer']
    yi = P['half_w'] - P['lip']          # recessed side of the phalanx (|y|)
    name = f"pad_{body}"
    outline = [(xb, za), (xb, zb), (xf, zb - a), (xf, za + a)]
    prism_xz(outline, -P['half_w'], 2 * P['half_w'], "new", name, f"{name}_section")
    # cells between the ribs: band inside the flanks, between the slanted end walls, between rib k and k+1
    x_in, x_out = xb - P['back'], xf + P['front']
    m = math.tan(math.radians(P['lean']))
    slope = a / P['depth']
    n = max(2, round((zb - za - 2 * a) / P['pitch']) + 1)
    c0, c1 = za + 1.0, zb - a - 1.0
    for k in range(n):
        lo = c0 + k * (c1 - c0) / n + P['rib'] / 2 if k else c0
        hi = c0 + (k + 1) * (c1 - c0) / n - P['rib'] / 2
        cell = [(x_in, lo - 5), (x_in, hi + 9), (x_out, hi + 9), (x_out, lo - 5)]
        for (aa, bb, kk) in ((0, 1, lo), (0, -1, -hi)):              # rib lines z - m*u, u = x_in - x
            cell = clip(cell, aa + bb * m, bb, kk + bb * m * x_in)
        # end walls (1.0 thick, parallel to the chamfered ends)
        cell = clip(cell, slope, 1, za + 1.0 + P['back'] + slope * xb)
        cell = clip(cell, slope, -1, -(zb - 1.0) + slope * xb)
        if len(cell) >= 3:
            prism_xz(cell, -P['half_w'] - 1, 2 * P['half_w'] + 2, "cut", name, f"{name}_cell_{k}")
    # side lips with hook teeth (into the phalanx side grooves)
    for s, sg in (("p", 1), ("n", -1)):
        ylo, yhi = sorted((sg * (yi + g), sg * P['half_w']))
        box((xb - 0.5, P['lip_x']), (ylo, yhi), (za, zb), "join", name, f"{name}_lip_{s}")  # 0.5 into the back flank
        ylo, yhi = sorted((sg * (yi + g - P['tooth_in']), sg * (yi + g + 0.01)))
        box(P['tooth'], (ylo, yhi), (za, zb), "join", name, f"{name}_tooth_{s}")
        # phalanx: recess (lip seat) and groove (tooth seat), 0.1 bigger; the recess ends are the axial stops
        ylo, yhi = sorted((sg * yi, sg * (P['half_w'] + 0.01)))
        box((-T / 2 - 0.01, P['lip_x'] + 0.2), (ylo, yhi), (za - g, zb + g), "cut", body, f"{body}_lip_recess_{s}")
        ylo, yhi = sorted((sg * (yi - P['tooth_in'] - g), sg * (yi + 0.01)))
        box((P['tooth'][0] - g, P['tooth'][1] + g), (ylo, yhi), (za - g, zb + g), "cut", body, f"{body}_tooth_groove_{s}")


def r2_raptor_finray():
    """C7: C5 (Raptor cord + elastic) with a swappable TPU fin-ray pad on every phalanx."""
    r2_raptor()
    z_mcp = ZS + 26.0
    zj = [z_mcp, z_mcp + L[0], z_mcp + L[0] + L[1], z_mcp + sum(L)]
    pad_fin_ray("proximal", zj[0] + 3.0, zj[1] - 1.5)
    pad_fin_ray("middle", zj[1] + 1.5, zj[2] - 1.5)
    pad_fin_ray("distal", zj[2] + 1.5, zj[3] - T / 2)


CONCEPTS = {
    'C1_geared-coupled': n1_geared,
    'C2_push-pull-spine': n2_spine,
    'C3_rolling-contact': n3_rolling,
    'C4_openhand-flexure': r1_flexure,
    'C5_raptor-cord-elastic': r2_raptor,
    'C6_amazing-rod-fourbar': r3_rod_fourbar,
    'C7_raptor-finray-pads': r2_raptor_finray,
}


def build(key):
    cmds.clear()
    finish(key.split('_')[0])
    CONCEPTS[key]()
    OFFS[key] = OFFS['last']
    return list(cmds)


def servo_matrix(off, dy=0.0):
    return [[1, 0, 0, 0], [0, -1, 0, fx(15.35 + off + dy)], [0, 0, -1, fx(ZS - 5.7)]]


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for k in CONCEPTS:
        cl = build(k)
        p = os.path.join(OUT, f"{k}.json")
        with open(p, 'w') as fh:
            fh.write('[\n' + ',\n'.join(' ' + json.dumps(x, separators=(',', ':')) for x in cl) + '\n]\n')
        print(os.path.relpath(p), len(cl), 'steps')
