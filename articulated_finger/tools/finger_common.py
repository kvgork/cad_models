"""Shared geometry for the printable articulated-finger versions (v1 Raptor cord, v2 rod + four-bar).

Frame (same as the concepts, gen_concepts.py): the dovetail runs along X on the tester baseplate, the finger
stands up along +Z at y = 0 and flexes in the XZ plane toward the palm (-X). Joint axes run along Y.
A joint angle is positive for flexion: the revolute axis is -Y, so +angle turns +Z toward -X.

Knuckle (PIP, DIP; the MCP uses the same child end between the base cheeks):
  - parent end: two cheeks (|y| 4.3 .. 9) rounded with R = T/2 about the axis; the tongue slot between them
    is cleared to R + 0.4 around the axis and everything above it, plus a pocket for the stop spur.
  - child end: a tongue (|y| <= 4.0) rounded with R below the axis; beside the tongue the child is cleared
    to R + 0.4 around the axis; its palm side is cleared up to R + 0.4 above the axis (the crease), so it can
    flex ~90 deg before its palm corner meets the parent (a natural flex stop).
  - extension stop: a spur on the tongue (sector 10.6, -80 .. -42 deg from +X) sits in the parent pocket; at
    0 deg its -80 deg face meets the pocket wall (-82 deg), so the elastic holds the finger straight.
Pins: one-piece snap pins along Y (v4b/v8 type, two flats with normals +-X, slot thin in Z), heads proud.
Holes are teardrops: the phalanges print lying on their back (dorsal face +X on the bed), so the teardrop
points to -X (up in the print); the base prints dovetail down, its MCP teardrop points +Z.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import parts  # noqa: E402

REV = lambda pn: parts.register()[pn]['Rev']  # noqa: E731

# ---------------------------------------------------------------- shared numbers (mm), as the concepts
DT = dict(dt_len=40.0, dt_bot=34.0, dt_top=28.0, dt_h=6.0, head_h=4.0)   # copied from GRIP-0002
Z_HEAD = DT['dt_h'] + DT['head_h']          # 10
W, T = 18.0, 16.0                           # finger width (Y), thickness (X)
R = T / 2                                   # knuckle radius
L = (45.0, 25.0, 22.0)                      # proximal, middle, distal
ZS = 34.5                                   # servo output axis height
CASE = dict(x=6.05, y_out=-11.65, y_in=16.8, z0=-17.35, z1=5.95, tab_z0=-21.95, tab_z1=10.55, tab_t=1.6)
SERVO_CLR = 0.5
TOWER_X = 10.0
Z_MCP = ZS + 26.0                           # 60.5
ZJ = (Z_MCP, Z_MCP + L[0], Z_MCP + L[0] + L[1], Z_MCP + sum(L))   # MCP, PIP, DIP, tip

# knuckle
TW = 4.0              # tongue half width
SG = 0.3              # side gap tongue / cheek, and finger / base cheek
RG = 0.4              # radial gap around the knuckle
RS = 10.6             # stop spur radius
SPUR = (-80.0, -42.0)  # spur sector (deg from +X, CCW toward +Z)
POCKET0 = -82.0       # pocket wall: the extension stop
SPUR_PRINT_END = -30.0  # spur arc drawn on to here, then clipped at x = R (flush with the back face)
# base fork
CHEEK_T = 3.0
CHEEK_Y0 = W / 2 + SG                       # 9.3
CHEEK_Y1 = CHEEK_Y0 + CHEEK_T               # 12.3
POST_X0 = CASE['x'] + 0.55                  # 6.6: the servo (case x 6.05) slides in between the posts
Z_CHEEK0 = ZS + CASE['tab_z1'] + 1.15       # 46.2: cheeks start above the servo tab tips (45.05)
# pins
CLEAR = 0.15
PIN_HOLE = 3.4
PIN_D = PIN_HOLE - 2 * CLEAR                # 3.1
PIN_R = PIN_D / 2
FLAT = 0.25
HEAD_D, HEAD_H = 5.5, 1.5
BARB_D, BARB_TIP, BARB_H, BARB_UP = 4.0, 2.8, 1.5, 0.2
SLOT_W, SLOT_DOWN = 0.8, 4.0
HEAD_GAP = 0.1                              # pin head drawn 0.1 off the face it bears on (check gap)
# cord / elastic channels (along Z through the phalanges)
CH = 2.2                                    # square channel
CH_X = 5.5                                  # palm channel at x = -5.5, dorsal at +5.5


def fx(v):
    return round(v, 4)


cmds = []


def c(command, **params):
    cmds.append({"command": command, "params": params})


def _op(p, op, body):
    p.update({"body_name": body} if op == "new" else {"targets": [body]})
    return p


def box(x, y, z, op, body, name):
    c("solid.box", **_op(dict(length=f"{fx(x[1] - x[0])} mm", width=f"{fx(y[1] - y[0])} mm",
                              height=f"{fx(z[1] - z[0])} mm",
                              center=[fx((x[0] + x[1]) / 2), fx((y[0] + y[1]) / 2), fx((z[0] + z[1]) / 2)],
                              operation=op, name=name), op, body))


def cyl_y(d, x, z, y0, y1, op, body, name):
    c("solid.cylinder", **_op(dict(diameter=f"{fx(d)} mm", height=f"{fx(y1 - y0)} mm", base=[fx(x), fx(y0), fx(z)],
                                   axis=[0, 1, 0], operation=op, name=name), op, body))


def cyl_z(d, x, y, z0, z1, op, body, name):
    c("solid.cylinder", **_op(dict(diameter=f"{fx(d)} mm", height=f"{fx(z1 - z0)} mm", base=[fx(x), fx(y), fx(z0)],
                                   axis=[0, 0, 1], operation=op, name=name), op, body))


def prism_xz(pts, y0, y1, op, body, name):
    """Profile in (x, z) extruded from y0 to y1 (XZ sketch: sketch x = +X, sketch y = -Z, normal +Y)."""
    c("sketch.create", plane="XZ", offset=f"{fx(y0)} mm", name=f"{name}_sk")
    c("sketch.line", points=[[fx(x), fx(-z)] for x, z in pts], closed=True)
    c("sketch.finish")
    c("solid.extrude", **_op(dict(distance=f"{fx(y1 - y0)} mm", operation=op, name=name), op, body))


def sector(cx, cz, r0, r1, a0, a1, n=12):
    """Annular sector polygon in (x, z); angles in deg from +X toward +Z."""
    out = [(cx + r1 * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cz + r1 * math.sin(math.radians(a0 + (a1 - a0) * k / n)))
           for k in range(n + 1)]
    if r0 <= 0:
        return out + [(cx, cz)]
    return out + [(cx + r0 * math.cos(math.radians(a1 - (a1 - a0) * k / n)), cz + r0 * math.sin(math.radians(a1 - (a1 - a0) * k / n)))
                  for k in range(n + 1)]


def teardrop_y(d, x, z, y0, y1, body, name, apex=(-1, 0)):
    """Horizontal hole along Y with a 45 deg teardrop point toward apex (unit (dx, dz)): prints round."""
    cyl_y(d, x, z, y0, y1, "cut", body, name)
    r = d / 2
    ax, az = apex
    px, pz = -az, ax                                  # perpendicular
    s = r / math.sqrt(2)
    pts = [(x + s * (ax + px), z + s * (az + pz)), (x + r * math.sqrt(2) * ax, z + r * math.sqrt(2) * az),
           (x + s * (ax - px), z + s * (az - pz)), (x, z)]
    prism_xz(pts, y0, y1, "cut", body, f"{name}_tear")


# ---------------------------------------------------------------- knuckles
def knuckle_parent(body, zj, slot_half=TW + SG, apex=(-1, 0)):
    """Rounded cheeks at the top of a phalanx (its block must reach zj) and the tongue slot."""
    cyl_y(T, 0, zj, -W / 2, W / 2, "join", body, f"{body}_cheeks_round")
    box((-R - 1, R + 1), (-slot_half, slot_half), (zj, zj + R + 1), "cut", body, f"{body}_tongue_slot")
    cyl_y(T + 2 * RG, 0, zj, -slot_half, slot_half, "cut", body, f"{body}_tongue_clear")
    prism_xz(sector(0, zj, 0, RS + RG, POCKET0, 0.0), -slot_half, slot_half, "cut", body, f"{body}_spur_pocket")
    teardrop_y(PIN_HOLE, 0, zj, -W / 2 - 1, W / 2 + 1, body, f"{body}_pin_hole_top", apex=apex)


def knuckle_child(body, zj, tongue_half=TW, z_top=None, apex=(-1, 0)):
    """Bottom end of a phalanx whose block starts at zj: crease, cleared cheek bands, round tongue, spur, pin hole."""
    box((-R - 1, 0.0), (-W / 2 - 1, W / 2 + 1), (zj - 0.5, zj + R + RG), "cut", body, f"{body}_crease")
    if tongue_half < W / 2:
        for s, (a, b) in (("p", (tongue_half, W / 2 + 1)), ("n", (-W / 2 - 1, -tongue_half))):
            cyl_y(T + 2 * RG, 0, zj, a, b, "cut", body, f"{body}_cheek_clear_{s}")
    cyl_y(T, 0, zj, -tongue_half, tongue_half, "join", body, f"{body}_tongue_round")
    # the spur runs out flush with the dorsal face (x = R): it then stands on the bed when the phalanx prints on
    # its back (a tip 0.12 under that face was a floating region in the slicer)
    sp = [(min(x, R), z) for x, z in sector(0, zj, R - 0.5, RS, SPUR[0], SPUR_PRINT_END)]
    prism_xz(sp, -tongue_half, tongue_half, "join", body, f"{body}_spur")
    teardrop_y(PIN_HOLE, 0, zj, -W / 2 - 1, W / 2 + 1, body, f"{body}_pin_hole_root", apex=apex)


def channels(body, z0, z1, palm=True, dorsal=True):
    for on, s, n in ((palm, -1, 'cord'), (dorsal, 1, 'elastic')):
        if on:
            box((s * CH_X - CH / 2, s * CH_X + CH / 2), (-CH / 2, CH / 2), (z0, z1), "cut", body, f"{body}_{n}_channel")


def phalanx(body, i, parent_top=True, ch=True, apex=(-1, 0)):
    """Phalanx i (0 proximal, 1 middle, 2 distal) in the straight pose. apex: teardrop point of the pin holes
    (default -X: printed on its back; v2's proximal prints on its palm, apex +X)."""
    z0, z1 = ZJ[i], ZJ[i + 1]
    if i == 2:
        box((-R, R), (-W / 2, W / 2), (z0, z1 - R), "new", body, f"{body}_block")
        cyl_y(T, 0, z1 - R, -W / 2, W / 2, "join", body, f"{body}_tip_round")
    else:
        box((-R, R), (-W / 2, W / 2), (z0, z1), "new", body, f"{body}_block")
    knuckle_child(body, z0, tongue_half=(W / 2 if i == 0 else TW), apex=apex)
    if i < 2 and parent_top:
        knuckle_parent(body, z1, apex=apex)
    if ch:
        channels(body, z0 - RS - 1, z1 + R + 1)


# ---------------------------------------------------------------- base
RAIL_TOP = DT['dt_h'] + 0.2                   # tester rails reach z dt_h beside the head: printed overhangs start 0.2 above


def prism_yz(pts, x0, x1, op, body, name):
    """Profile in (y, z) extruded from x0 to x1 (YZ sketch: sketch x = +Y, sketch y = +Z, normal +X)."""
    c("sketch.create", plane="YZ", offset=f"{fx(x0)} mm", name=f"{name}_sk")
    c("sketch.line", points=[[fx(y), fx(z)] for y, z in pts], closed=True)
    c("sketch.finish")
    c("solid.extrude", **_op(dict(distance=f"{fx(x1 - x0)} mm", operation=op, name=name), op, body))


def base(body, off, bars=True, centre_dovetail=False):
    """Dovetail + servo cradle (concept base) + MCP fork: two cheeks on posts with the servo path between them,
    an extension-stop sector bridging the cheeks under the proximal, cord-guide and elastic-anchor bars.

    centre_dovetail (v1, 2026-11-22: the slicer flagged the cradle, 21 mm past the head at z 9.7, as a floating
    cantilever): the dovetail moves to the middle of the footprint (y -12.3 .. cradle back) and everything past
    the head on either side gets a 45 deg underside starting 0.2 above the tester rails, so the base prints
    dovetail down without supports. Feet under the posts (|x| >= 6.6) carry the -Y cheeks down that slope; the
    servo path between them stays open."""
    y_end = off + CASE['y_in'] + SERVO_CLR + 2.0
    dt_y = fx((-CHEEK_Y1 + y_end) / 2) if centre_dovetail else 0.0
    for k, v in DT.items():
        c("parameters.add", name=k, expression=f"{v} mm", comment="copied from GRIP-0002 (tester dovetail)")
    c("parameters.add", name="dt_y", expression=f"{dt_y} mm",
      comment="dovetail centre in Y: under the middle of the footprint, so both overhangs can be 45 deg")
    c("sketch.create", plane="YZ", offset="-dt_len/2", name="DovetailSketch")
    c("sketch.line", points=[["dt_y - dt_bot/2", 0], ["dt_y + dt_bot/2", 0], ["dt_y + dt_top/2", "dt_h"],
                             ["dt_y + dt_top/2", "dt_h + head_h"], ["dt_y - dt_top/2", "dt_h + head_h"],
                             ["dt_y - dt_top/2", "dt_h"]], closed=True)
    c("sketch.finish")
    c("solid.extrude", distance="dt_len", operation="new", body_name=body, name="Dovetail")
    z_case0 = ZS + CASE['z0'] - SERVO_CLR
    z_plinth = ZS + CASE['tab_z0'] - SERVO_CLR
    z_top = ZS + CASE['tab_z1'] + 2.0
    y_lo = -CHEEK_Y1 - 0.5 if centre_dovetail else -DT['dt_top'] / 2
    box((-TOWER_X, TOWER_X), (y_lo, y_end), (Z_HEAD - 0.3, z_plinth), "join", body, "Plinth")
    box((-TOWER_X, TOWER_X), (off, y_end), (Z_HEAD - 0.3, z_top), "join", body, "Cradle")
    box((-CASE['x'] - SERVO_CLR, CASE['x'] + SERVO_CLR), (off - 0.1, off + CASE['y_in'] + SERVO_CLR),
        (z_case0, ZS + CASE['z1'] + SERVO_CLR), "cut", body, "ServoPocket")
    # servo tab screws (M2 self-tapping, supplied with the servo): pilot holes into the cradle face
    for k, dz in (("lo", -19.95), ("hi", 8.55)):
        c("solid.cylinder", diameter="1.6 mm", height="7 mm", base=[0, fx(off - 0.1), fx(ZS + dz)], axis=[0, 1, 0],
          operation="cut", targets=[body], name=f"ServoTabPilot_{k}")
    for s, (y0, y1) in (("n", (-CHEEK_Y1, -CHEEK_Y0)), ("p", (CHEEK_Y0, CHEEK_Y1))):
        for sx, (x0, x1) in (("palm", (-TOWER_X, -POST_X0)), ("back", (POST_X0, TOWER_X))):
            box((x0, x1), (y0, y1), (z_plinth - 0.3, Z_CHEEK0 + 0.5), "join", body, f"Post_{s}_{sx}")
        box((-TOWER_X, TOWER_X), (y0, y1), (Z_CHEEK0, Z_MCP), "join", body, f"Cheek_{s}")
        cyl_y(T, 0, Z_MCP, y0, y1, "join", body, f"Cheek_{s}_round")
    # extension stop under the proximal (its spur meets the -82 deg face), bridging the two cheeks
    prism_xz(sector(0, Z_MCP, R + RG, 12.0, -112.0, POCKET0), -CHEEK_Y0 - 0.3, CHEEK_Y0 + 0.3, "join", body, "MCPStop")
    if bars:
        # hand pull: the cord runs down the palm side and out under this bar (servo stage: onto the spool)
        box((-TOWER_X, -7.0), (-CHEEK_Y1, CHEEK_Y1), (z_plinth + 2.0, z_plinth + 5.0), "join", body, "CordGuideBar")
        # elastic loops round this bar on the back, under the cheeks (clear of the servo path and the spool)
        box((7.0, TOWER_X), (-CHEEK_Y0 - 0.3, CHEEK_Y0 + 0.3), (Z_CHEEK0 - 3.0, Z_CHEEK0 + 0.5), "join", body,
            "ElasticAnchorBar")
    if centre_dovetail:
        hw = DT['dt_top'] / 2
        for s_, n in ((-1, "n"), (1, "p")):
            yh = dt_y + s_ * hw                                # head side face
            far = (y_lo - 1.0) if s_ < 0 else (y_end + 1.0)
            if s_ < 0:      # feet under the -Y posts, down to the slope (cut below)
                z_ft = RAIL_TOP + (yh + CHEEK_Y1) + 1.0      # 1 mm over the slope under the outer post face
                for sx, (x0, x1) in (("palm", (-TOWER_X, -POST_X0)), ("back", (POST_X0, TOWER_X))):
                    box((x0, x1), (-CHEEK_Y1, yh + 0.3), (RAIL_TOP, z_ft), "join", body, f"PostFoot_{sx}")
            # 45 deg underside: remove everything past the head below z = RAIL_TOP + |y - yh|
            prism_yz([(yh, RAIL_TOP), (far, RAIL_TOP + abs(far - yh)), (far, DT['dt_h']), (yh, DT['dt_h'])],
                     -TOWER_X - 1, TOWER_X + 1, "cut", body, f"Underside45_{n}")
            # fill from the head side up the slope to the plinth bottom
            prism_yz([(yh - s_ * 0.3, RAIL_TOP - 0.3), (yh + s_ * (Z_HEAD - RAIL_TOP), Z_HEAD), (yh - s_ * 0.3, Z_HEAD)],
                     -TOWER_X, TOWER_X, "join", body, f"HeadFillet45_{n}")
    teardrop_y(PIN_HOLE, 0, Z_MCP, -CHEEK_Y1 - 1, CHEEK_Y1 + 1, body, "MCPPinHole", apex=(0, 1))
    return dict(z_plinth=z_plinth, z_top=z_top, y_end=y_end, dt_y=dt_y)


# ---------------------------------------------------------------- pins
def snap_pin_y(body, x, z, y_seat, y_cap, flat=FLAT, head_pos=False):
    """One-piece snap pin along +Y: head face on y_seat (head toward -Y), barb shoulder BARB_UP past y_cap.
    Two flats with normals +-X (it prints lying on one); the slot is thin in Z, so the barb catch (+-Z) stays.
    head_pos: the same pin turned round (head toward +Y, y_seat > y_cap)."""
    if head_pos:
        return _snap_pin_y_rev(body, x, z, y_seat, y_cap, flat)
    y_sh = y_cap + BARB_UP
    y0 = y_seat - HEAD_H
    top = y_sh + BARB_H
    cyl_y(HEAD_D, x, z, y0, y_seat, "new", body, f"{body}_head")
    cyl_y(PIN_D, x, z, y_seat - 0.01, y_sh + 0.3, "join", body, f"{body}_shank")
    c("solid.cone", diameter=f"{BARB_D} mm", top_diameter=f"{BARB_TIP} mm", height=f"{BARB_H} mm",
      base=[fx(x), fx(y_sh), fx(z)], axis=[0, 1, 0], operation="join", targets=[body], name=f"{body}_barb")
    for s in (1, -1):
        e = PIN_R - flat
        box((x + s * e, x + s * (HEAD_D / 2 + 1)) if s > 0 else (x - HEAD_D / 2 - 1, x - e), (y0 - 0.5, top + 0.5),
            (z - HEAD_D / 2 - 1, z + HEAD_D / 2 + 1), "cut", body, f"{body}_flat_{'p' if s > 0 else 'n'}")
    sl = BARB_H + BARB_UP + SLOT_DOWN
    box((x - 5, x + 5), (top - sl, top + 0.5), (z - SLOT_W / 2, z + SLOT_W / 2), "cut", body, f"{body}_slot")
    return y_sh - y_seat


def _snap_pin_y_rev(body, x, z, y_seat, y_cap, flat=FLAT):
    """snap_pin_y mirrored in Y: head toward +Y from y_seat, barb shoulder BARB_UP below y_cap (v2 ear pins)."""
    y_sh = y_cap - BARB_UP
    y1 = y_seat + HEAD_H
    top = y_sh - BARB_H
    cyl_y(HEAD_D, x, z, y_seat, y1, "new", body, f"{body}_head")
    cyl_y(PIN_D, x, z, y_sh - 0.3, y_seat + 0.01, "join", body, f"{body}_shank")
    c("solid.cone", diameter=f"{BARB_D} mm", top_diameter=f"{BARB_TIP} mm", height=f"{BARB_H} mm",
      base=[fx(x), fx(y_sh), fx(z)], axis=[0, -1, 0], operation="join", targets=[body], name=f"{body}_barb")
    for s in (1, -1):
        e = PIN_R - flat
        box((x + s * e, x + s * (HEAD_D / 2 + 1)) if s > 0 else (x - HEAD_D / 2 - 1, x - e), (top - 0.5, y1 + 0.5),
            (z - HEAD_D / 2 - 1, z + HEAD_D / 2 + 1), "cut", body, f"{body}_flat_{'p' if s > 0 else 'n'}")
    sl = BARB_H + BARB_UP + SLOT_DOWN
    box((x - 5, x + 5), (top - 0.5, top + sl), (z - SLOT_W / 2, z + SLOT_W / 2), "cut", body, f"{body}_slot")
    return y_seat - y_sh


# ---------------------------------------------------------------- assembly bookkeeping
class Assy:
    def __init__(self, vdir, assy, pn, project="articulated_finger"):
        self.vdir, self.assy, self.pn, self.project = vdir, assy, pn, project
        self.comps = []     # (key, inst)

    def cname(self, key, i):
        return f"{parts.fname(self.pn[key])}_{i}"

    def occ(self, key, i):
        return f"{self.cname(key, i)}:1"

    def new(self, key, i, grounded=False):
        c("component.activate", component=0)
        c("component.create", name=self.cname(key, i), activate=True, grounded=grounded)
        self.comps.append((key, i))
        return self.cname(key, i)

    def header(self):
        cmds.clear()
        c("document.metadata.set", values={"part_number": self.assy, "description": parts.register()[self.assy]['Description'],
                                           "revision": REV(self.assy), "project": self.project})

    def servo(self, off):
        c("component.activate", component=0)
        c("file.insert_step", path="base/feetech_scs0009/LIB-0010_servo-scs0009.step", name="LIB-0010_servo-scs0009")
        c("occurrence.move", occurrence="LIB-0010_servo-scs0009:1", move_grounded=True, matrix=servo_matrix(off))

    def finish(self):
        for key, i in self.comps:
            p = self.pn[key]
            c("component.metadata.set", component=self.cname(key, i), part_number=p,
              description=parts.register()[p]['Description'], revision=REV(p), bom_type="normal")
        done = set()
        for key, i in self.comps:
            p = self.pn[key]
            if p in done:
                continue
            done.add(p)
            for ext, cmd in (('step', 'file.export_step'), ('stl', 'file.export_stl'), ('3mf', 'file.export_3mf')):
                pr = dict(path=f"{self.vdir}/exports/{parts.export(p, REV(p), ext)}", bodies=[self.cname(key, i)])
                if ext != 'step':
                    pr["quality"] = "fine"
                c(cmd, **pr)

    def write(self):
        for sub in ('cad', 'exports', 'docs'):
            os.makedirs(os.path.join(ROOT, self.vdir, sub), exist_ok=True)
        out = f"{self.vdir}/cad/{parts.fname(self.assy)}.json"
        with open(os.path.join(ROOT, out), 'w') as fh:
            fh.write('[\n' + ',\n'.join(' ' + json.dumps(x, separators=(',', ':')) for x in cmds) + '\n]\n')
        return out


def servo_matrix(off, dy=0.0):
    return [[1, 0, 0, 0], [0, -1, 0, fx(15.35 + off + dy)], [0, 0, -1, fx(ZS - 5.7)]]


def rev_y(name, a, b, z, x=0.0):
    """Revolute about -Y through (x, 0, z): +angle = flexion (turns +Z toward -X)."""
    c("joint.as_built", type="revolute", a=a, b=b, at={"point": [fx(x), 0, fx(z)], "z": [0, -1, 0], "x": [0, 0, 1]},
      name=name)


def rigid(a, b):
    c("joint.as_built", type="rigid", a=a, b=b, name=f"fix_{b.split(':')[0]}")
