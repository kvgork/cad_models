"""Generate cad/GRIP-9002.json: the Strandbeest (Jansen) finger v1 assembly.

Every link is its own component with its own part number (GRIP-0003..0010).
The script builds them at the theta = 0 pose from jansen.py, inserts the
STS3215 servo, adds the 10 revolute joints and exports each part.

Run from the repo root:
    python3 strandbeest_gripper/tools/gen_finger.py [--smoke]
    solidcraft-cli run strandbeest_gripper/cad/GRIP-9002.json --save strandbeest_gripper/cad/GRIP-9002.sc

World frame = the servo STEP's own frame (lib/sts3215/LIB-0009.step): output
axis at A = (12.5, 0) along +Z, horn top at z = 18.7. The linkage (link frame
of jansen.py) is turned +ROT about A so pivot G lands at +X, past the case.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jansen import pose, check_reference  # noqa: E402

S = 0.4                      # scale on the holy numbers
A = (12.5, 0.0)              # servo output axis (STEP frame)
HORN_TOP = 18.7              # horn disc top face z
THETA_MIN, THETA_MAX = -63.0, 66.0     # operating range (stance band, tip within 0.2 mm)
STOP_MIN, STOP_MAX = -65.25, 68.25     # hard-stop contact angles (tabs on the crank hit the G post)

P0 = pose(0.0, S)
ROT = -math.atan2(P0['G'][1], P0['G'][0])          # +168.4 deg: G onto +X
CR, SR = math.cos(ROT), math.sin(ROT)


def W(p):
    """Link frame -> world XY."""
    return (round(A[0] + CR * p[0] - SR * p[1], 4), round(A[1] + SR * p[0] + CR * p[1], 4))


J = {k: W(v) for k, v in P0.items()}               # joint centres, world, theta = 0
G = J['G']

# ---- layer stack (layers.py result for -70..+70, 4 layers) -------------------
CRANK_T = 6.0
BAR_W = 7.0                  # link width (slot width takes numbers only in 0.30.1); wall = (BAR_W - pin_d)/2
LAYER = {'crank': 0, 'k': 1, 'bde': 1, 'j': 2, 'c': 2, 'f': 2, 'ghi': 3}
CRANK_TOP = HORN_TOP + CRANK_T                     # 24.7


def zbot(layer):
    """Bottom z of a layer as an expression (layers 1..3 follow link_t / gap)."""
    if layer == 0:
        return f"{HORN_TOP} mm"
    return f"{CRANK_TOP} mm + gap + {layer - 1} * (link_t + gap)"


PN = {'frame': 'GRIP-0003', 'crank': 'GRIP-0004', 'j': 'GRIP-0005', 'k': 'GRIP-0006',
      'c': 'GRIP-0007', 'f': 'GRIP-0008', 'bde': 'GRIP-0009', 'ghi': 'GRIP-0010'}
DESC = {'frame': 'FRAME, FINGER, STRANDBEEST', 'crank': 'CRANK, FINGER, STRANDBEEST',
        'j': 'LINK, J, STRANDBEEST', 'k': 'LINK, K, STRANDBEEST', 'c': 'LINK, C, STRANDBEEST',
        'f': 'LINK, F, STRANDBEEST', 'bde': 'TRIANGLE, BDE, STRANDBEEST',
        'ghi': 'TRIANGLE, GHI, FINGERTIP, STRANDBEEST'}
BARS = {'j': ('J1', 'J2'), 'k': ('J1', 'J4'), 'c': ('G', 'J4'), 'f': ('J3', 'J5')}
TRIS = {'bde': ('G', 'J2', 'J3'), 'ghi': ('J4', 'J5', 'F')}
HOLES = {'j': ['J1', 'J2'], 'k': ['J1', 'J4'], 'c': ['G', 'J4'], 'f': ['J3', 'J5'],
         'bde': ['G', 'J2', 'J3'], 'ghi': ['J4', 'J5']}

cmds = []


def c(command, **params):
    cmds.append({"command": command, "params": params})


def fmt(v):
    return round(v, 4)


# ---------------------------------------------------------------- parameters
c("document.metadata.set", values={"part_number": "GRIP-9002", "description": "ASSY, FINGER, STRANDBEEST",
                                   "revision": "X1", "project": "strandbeest_gripper"})
for name, expr, why in [
    ("link_t", "3 mm", "link plate thickness (layers 1-3)"),
    ("gap", "0.5 mm", "axial gap between layers = M3 washer"),
    ("pin_d", "3.4 mm", "rotating M3 pin hole, ISO 273 medium; calibrate with a coupon"),
    ("head_d", "6.5 mm", "M3 socket head pocket/counterbore"),
    ("fit_clr", "0.2 mm", "servo sleeve clearance per side (FDM sliding fit)"),
    ("wall", "2.5 mm", "frame wall thickness"),
    ("pad_d", "10 mm", "fingertip pad diameter (round: contact stays on F as the foot turns)"),
]:
    c("parameters.add", name=name, expression=expr, comment=why)


def slot(name, p, q, z_expr, body, op):
    c("sketch.create", plane="XY", offset=z_expr, name=f"{name}_sk")
    c("sketch.slot.center_to_center", p0=list(p), p1=list(q), width=BAR_W)
    c("sketch.finish")
    params = dict(distance="link_t", operation=op, name=name)
    if op == "new":
        params["body_name"] = body
    else:
        params["targets"] = [body]
    c("solid.extrude", **params)


def pin_holes(body, names, z0, h):
    for n in names:
        x, y = J[n]
        c("solid.cylinder", diameter="pin_d", height=f"{h} mm", base=[fmt(x), fmt(y), z0],
          operation="cut", targets=[body], name=f"{body}_hole_{n}")


def component(key):
    c("component.activate", component=0)
    c("component.create", name=PN[key], activate=True)


# ---------------------------------------------------------------- frame GRIP-0003
fb = PN['frame']
c("component.create", name=fb, activate=True, grounded=True)
SX, SY = 22.7, 12.4                       # servo case half-extents
ZB, ZT = -21.4, 14.0                      # frame bottom (2 mm floor under z -19.4), sleeve top
c("solid.box", length=f"2 * ({SX} mm + fit_clr + wall)", width=f"2 * ({SY} mm + fit_clr + wall)",
  height=f"{ZT - ZB} mm", center=[A[0] - 12.5, 0, (ZB + ZT) / 2], operation="new", body_name=fb, name="sleeve_outer")
c("solid.box", length=f"2 * ({SX} mm + fit_clr)", width=f"2 * ({SY} mm + fit_clr)",
  height=f"{ZT - (-19.4) + 1} mm", center=[0, 0, (-19.4 + ZT + 1) / 2], operation="cut", targets=[fb], name="sleeve_pocket")
c("solid.box", length="6 mm", width="14 mm", height="26 mm", center=[-SX - 1.5, 0, ZT - 13 + 0.5],
  operation="cut", targets=[fb], name="cable_notch")
# G post: block merged into the +X end wall, Ø7 column to just under layer 1
c("solid.box", length="10 mm", width="10 mm", height=f"{ZT - ZB} mm", center=[fmt(G[0]), 0, (ZB + ZT) / 2],
  operation="join", targets=[fb], name="post_block")
c("solid.cylinder", diameter="7 mm", height=f"{CRANK_TOP - ZT} mm", base=[fmt(G[0]), fmt(G[1]), ZT],
  operation="join", targets=[fb], name="post")
c("solid.cylinder", diameter="pin_d", height=f"{CRANK_TOP - ZB + 1} mm", base=[fmt(G[0]), fmt(G[1]), ZB - 0.5],
  operation="cut", targets=[fb], name="post_hole")
G_SEAT = 10.0                             # G screw head seat: M3x30 from below reaches the c link + nyloc
c("solid.cylinder", diameter="head_d", height=f"{G_SEAT - ZB + 0.5} mm", base=[fmt(G[0]), fmt(G[1]), ZB - 0.5],
  operation="cut", targets=[fb], name="post_cbore")
# anvil column (link frame x 0..8, around the stance line) + arm to the sleeve
ytip = P0['F'][1]
an = [W(p) for p in [(0, ytip - 8), (8, ytip - 8), (8, ytip + 8), (0, ytip + 8)]]
AN_Z0, AN_Z1 = 4.0, 45.0
low = sorted(an, key=lambda p: p[1])[:2]
y_in = SY + 1.0                            # inside the sleeve wall
ov = 3.0                                   # reach 3 mm into the anvil so the join overlaps (face contact does not fuse)
up = [(p[0], p[1] + ov) for p in low]
arm = [up[0], up[1], (low[1][0], y_in), (low[0][0], y_in)]
c("sketch.create", plane="XY", offset=f"{AN_Z0} mm", name="arm_sk")
c("sketch.line", points=[list(p) for p in arm], closed=True)
c("sketch.finish")
c("solid.extrude", distance=f"{ZT - AN_Z0} mm", operation="join", targets=[fb], name="anvil_arm")
c("sketch.create", plane="XY", offset=f"{AN_Z0} mm", name="anvil_sk")
c("sketch.line", points=[list(p) for p in an], closed=True)
c("sketch.finish")
c("solid.extrude", distance=f"{AN_Z1 - AN_Z0} mm", operation="join", targets=[fb], name="anvil")

# ---------------------------------------------------------------- crank GRIP-0004
component('crank')
cb = PN['crank']
c("solid.cylinder", diameter="20 mm", height=f"{CRANK_T} mm", base=[A[0], A[1], HORN_TOP],
  operation="new", body_name=cb, name="crank_disc")


def tab_touch_bearing(r0=9.0, r1=11.5, hw=2.0, post_r=3.5, step=0.01):
    """Smallest bearing beta >= 0 (deg, from the post direction +X about A) at which a
    radial tab (slot from r0 to r1, half-width hw) touches the Ø7 post at G."""
    gx = math.hypot(G[0] - A[0], G[1] - A[1])
    beta = 0.0
    while beta < 90:
        a = math.radians(beta)
        ux, uy = math.cos(a), math.sin(a)
        s = max(r0, min(r1, gx * ux))
        if math.hypot(gx - s * ux, s * uy) - hw > post_r:
            return beta
        beta += step
    raise ValueError('tab never clears the post')


BETA = tab_touch_bearing()
# positive stop: tab bearing alpha turns by +t and touches at alpha + t = -BETA
TABS = {'stop_pos': -STOP_MAX - BETA, 'stop_neg': -STOP_MIN + BETA}
for nm, alpha in TABS.items():
    a = math.radians(alpha)
    mid = (A[0] + 11.5 * math.cos(a), A[1] + 11.5 * math.sin(a))
    c("sketch.create", plane="XY", offset=f"{HORN_TOP} mm", name=f"{nm}_sk")
    c("sketch.slot.center_to_center", p0=[fmt(A[0] + 9.0 * math.cos(a)), fmt(A[1] + 9.0 * math.sin(a))],
      p1=[fmt(A[0] + 11.5 * math.cos(a)), fmt(A[1] + 11.5 * math.sin(a))], width=4.0)
    c("sketch.finish")
    c("solid.extrude", distance=f"{CRANK_T} mm", operation="join", targets=[cb], name=nm)
# holes: J1 pin (head pocket from below), horn access, 2 horn screws far from J1
pin_holes(cb, ['J1'], HORN_TOP - 0.5, CRANK_T + 1)
c("solid.cylinder", diameter="head_d", height="3.2 mm", base=[fmt(J['J1'][0]), fmt(J['J1'][1]), HORN_TOP - 0.01],
  operation="cut", targets=[cb], name="J1_head_pocket")
c("solid.cylinder", diameter="5 mm", height=f"{CRANK_T + 1} mm", base=[A[0], A[1], HORN_TOP - 0.5],
  operation="cut", targets=[cb], name="horn_screw_access")
r_bc = 4.95
j1b = math.degrees(math.atan2(J['J1'][1] - A[1], J['J1'][0] - A[0]))
cands = sorted([45, 135, 225, 315], key=lambda b: -abs((b - j1b + 180) % 360 - 180))[:2]
for b in cands:
    x, y = A[0] + r_bc * math.cos(math.radians(b)), A[1] + r_bc * math.sin(math.radians(b))
    c("solid.cylinder", diameter="pin_d", height=f"{CRANK_T + 1} mm", base=[fmt(x), fmt(y), HORN_TOP - 0.5],
      operation="cut", targets=[cb], name=f"horn_screw_{b}")
    c("solid.cylinder", diameter="6 mm", height="3 mm", base=[fmt(x), fmt(y), CRANK_TOP - 3],
      operation="cut", targets=[cb], name=f"horn_cbore_{b}")

# ---------------------------------------------------------------- links
smoke = '--smoke' in sys.argv
links = ['k', 'c'] if smoke else ['j', 'k', 'c', 'f', 'bde', 'ghi']
for key in links:
    component(key)
    body = PN[key]
    z = zbot(LAYER[key])
    if key in BARS:
        p, q = BARS[key]
        slot(f"{key}_bar", J[p], J[q], z, body, "new")
    else:
        pts = TRIS[key]
        c("sketch.create", plane="XY", offset=z, name=f"{key}_plate_sk")
        c("sketch.line", points=[list(J[n]) for n in pts], closed=True)
        c("sketch.finish")
        c("solid.extrude", distance="link_t", operation="new", body_name=body, name=f"{key}_plate")
        for i in range(3):
            slot(f"{key}_edge{i}", J[pts[i]], J[pts[(i + 1) % 3]], z, body, "join")
    zc = LAYER[key]
    z0 = CRANK_TOP + 0.5 + (zc - 1) * 3.5
    pin_holes(body, HOLES[key], round(z0 - 0.5, 3), 4)
    if key == 'ghi':
        fx, fy = J['F']
        c("solid.cylinder", diameter="pad_d", height=f"{45.0 - 25.2} mm", base=[fmt(fx), fmt(fy), 25.2],
          operation="join", targets=[body], name="fingertip_pad")
    if key == 'bde':
        cx = sum(J[n][0] for n in pts) / 3
        cy = sum(J[n][1] for n in pts) / 3
        c("sketch.create", plane="XY", offset=f"{z0 + 3 - 0.6} mm", name="up_mark_sk")
        c("sketch.text", text="UP", at=[fmt(cx - 3.2), fmt(cy - 1.6)], height=3.5)
        c("sketch.finish")
        c("solid.extrude", distance="0.7 mm", operation="cut", targets=[body], name="up_mark")

# ---------------------------------------------------------------- servo + joints
c("component.activate", component=0)
c("file.insert_step", path="lib/sts3215/LIB-0009.step", name="LIB-0009")


def occ(key):
    return f"{PN[key]}:1"


def rev(name, a, b, pt, z, limits=None):
    params = dict(type="revolute", a=a, b=b, at={"point": [fmt(pt[0]), fmt(pt[1]), z], "z": [0, 0, 1]}, name=name)
    if limits:
        params["limits"] = limits
    c("joint.as_built", **params)


c("joint.as_built", type="rigid", a=occ('frame'), b="LIB-0009:1", name="servo_in_frame")
rev("O_crank", occ('frame'), occ('crank'), A, HORN_TOP, [[STOP_MIN, STOP_MAX]])
JOINTS = [("J1_crank_k", 'crank', 'k', 'J1'), ("J4_k_c", 'k', 'c', 'J4'), ("G_frame_c", 'frame', 'c', 'G')]
if not smoke:
    JOINTS = [("J1_crank_j", 'crank', 'j', 'J1'), ("J1_crank_k", 'crank', 'k', 'J1'),
              ("G_frame_bde", 'frame', 'bde', 'G'), ("G_frame_c", 'frame', 'c', 'G'),
              ("J2_j_bde", 'j', 'bde', 'J2'), ("J3_bde_f", 'bde', 'f', 'J3'),
              ("J4_k_c", 'k', 'c', 'J4'), ("J4_c_ghi", 'c', 'ghi', 'J4'), ("J5_f_ghi", 'f', 'ghi', 'J5')]
for name, a, b, n in JOINTS:
    rev(name, occ(a), occ(b), J[n], 30.0)

# ---------------------------------------------------------------- metadata + exports
for key in ['frame', 'crank'] + links:
    c("component.metadata.set", component=PN[key], part_number=PN[key], description=DESC[key],
      revision="X1", bom_type="normal")
c("component.metadata.set", component="LIB-0009", part_number="LIB-0009", description="SERVO, STS3215",
  bom_type="purchased")
if not smoke:
    for key in ['frame', 'crank'] + links:
        for ext, cmd in (('step', 'file.export_step'), ('stl', 'file.export_stl'), ('3mf', 'file.export_3mf')):
            params = dict(path=f"strandbeest_gripper/exports/{PN[key]}_X1.{ext}", bodies=[PN[key]])
            if ext != 'step':
                params["quality"] = "fine"
            c(cmd, **params)

if __name__ == '__main__':
    check_reference()
    out = 'strandbeest_gripper/cad/' + ('smoke.json' if smoke else 'GRIP-9002.json')
    with open(out, 'w') as fh:
        fh.write('[\n' + ',\n'.join(' ' + json.dumps(x, separators=(',', ':')) for x in cmds) + '\n]\n')
    print(out, len(cmds), 'steps; ROT %.2f deg; G world (%.2f, %.2f); tabs %s' %
          (math.degrees(ROT), G[0], G[1], {k: round(v, 2) for k, v in TABS.items()}))
    print('joints world (theta=0):', {k: v for k, v in J.items()})
