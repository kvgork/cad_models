"""Generate v2_dual-finger/cad/GRIP-9003_assy-dual-finger.json: Strandbeest gripper v2, two mirrored fingers (feeder).

Two Jansen legs (holy numbers x0.4) are mirrored across a horizontal line in
the link frame. Their feet meet at the bottom of the loop: the flat stroke
clamps an item and carries it ~20 mm along x, the lift (~9 mm per foot)
releases it. The crank turns continuously.

One STS3215 drives crank 1. Crank 2 is driven 1:1 in the opposite sense
through two idlers (3 meshes): module 1, crank gears z20, idlers z33.
Centre distance between the cranks = m (zc + 2 zi) = 86 mm.

Run from the repo root:
    python3 strandbeest_gripper/tools/gen_dual.py
    tools/build.sh strandbeest_gripper/v2_dual-finger

v1 (single finger + anvil, GRIP-9002) is built by gen_finger.py and is not touched.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))
import parts  # noqa: E402
from jansen import pose, check_reference  # noqa: E402
import layers  # noqa: E402

S = 0.4
A = (12.5, 0.0)              # servo output axis (STEP frame of lib/sts3215/LIB-0009_servo-sts3215.step)
HORN_TOP = 18.7
GEAR_T = 6.0                 # gear / crank layer thickness (layer 0)
LINK_T, GAP = 3.0, 0.5
BAR_W = 7.0                  # slot width takes numbers only in SolidCraft 0.30.1
PLATE_Z0, PLATE_Z1 = 12.0, 16.0

# gears
MOD, ZC, ZI = 1.0, 20, 33          # z >= 17: no undercut on the crank gears (z16 interfered)
BACKLASH = 0.3               # total, on the pitch circle (FDM)
RC, RI = MOD * ZC / 2, MOD * ZI / 2
D_CRANKS = MOD * (ZC + 2 * ZI)            # 86.0
YM = -D_CRANKS / 2                        # mirror line in the link frame

P0 = pose(0.0, S)
YMIN_ABS = abs(min(pose(math.radians(t), S)['F'][1] for t in range(360)))
PAD_D = 11.0
CLAMP_GAP = 2 * (abs(YM) - YMIN_ABS) - PAD_D
ROT = -math.atan2(P0['G'][1], P0['G'][0])  # +168.4 deg, as v1: G1 lands past the servo case end
CR, SR = math.cos(ROT), math.sin(ROT)


def W(p):
    """Link frame -> world XY (servo STEP frame)."""
    return (round(A[0] + CR * p[0] - SR * p[1], 4), round(A[1] + SR * p[0] + CR * p[1], 4))


def mir(p):
    return (p[0], 2 * YM - p[1])


# joint centres in the link frame, theta = 0
JL = {1: dict(P0), 2: {k: mir(v) for k, v in P0.items()}}
JL[1]['I'] = (0.0, -(RC + RI))
JL[2]['I'] = mir(JL[1]['I'])
J = {f: {k: W(v) for k, v in JL[f].items()} for f in (1, 2)}

# ---- layers: computed for the full turn with Ø7 hubs, screw heads and nuts ----
layers.SPACER_R = BAR_W / 2
_conf, _near = layers.analyse([float(t) for t in range(360)], S)
NL, LAYER = layers.solve(_conf, _near)


def zb(layer):
    """Bottom z of a layer: layer 0 is the gear layer on the horn, then LINK_T plates with GAP."""
    return HORN_TOP if layer == 0 else HORN_TOP + GEAR_T + GAP + (layer - 1) * (LINK_T + GAP)


def zt(layer):
    return zb(layer) + (GEAR_T if layer == 0 else LINK_T)


STACK_TOP = zt(NL - 1)

BARS = {'j': ('J1', 'J2'), 'k': ('J1', 'J4'), 'c': ('G', 'J4'), 'f': ('J3', 'J5')}
TRIS = {'bde': ('G', 'J2', 'J3'), 'ghi': ('J4', 'J5', 'F')}
HOLES = {'j': ['J1', 'J2'], 'k': ['J1', 'J4'], 'c': ['G', 'J4'], 'f': ['J3', 'J5'],
         'bde': ['G', 'J2', 'J3'], 'ghi': ['J4', 'J5']}
PINS = layers.PINS

PN = {'frame': 'GRIP-0011', 'crank1': 'GRIP-0012', 'crank2': 'GRIP-0013', 'idler': 'GRIP-0014',
      'j': 'GRIP-0015', 'k': 'GRIP-0016', 'c': 'GRIP-0017', 'f': 'GRIP-0018',
      ('bde', 1): 'GRIP-0019', ('ghi', 1): 'GRIP-0020', ('bde', 2): 'GRIP-0021', ('ghi', 2): 'GRIP-0022'}
DESC = {'frame': 'FRAME, DUAL FINGER, STRANDBEEST', 'crank1': 'GEAR, CRANK, SERVO SIDE, Z20 M1',
        'crank2': 'GEAR, CRANK, IDLE SIDE, Z20 M1', 'idler': 'GEAR, IDLER, Z33 M1',
        'j': 'LINK, J, HUB, STRANDBEEST V2', 'k': 'LINK, K, STRANDBEEST V2', 'c': 'LINK, C, STRANDBEEST V2',
        'f': 'LINK, F, HUB, STRANDBEEST V2', ('bde', 1): 'TRIANGLE, BDE, FINGER 1, STRANDBEEST V2',
        ('ghi', 1): 'TRIANGLE, GHI, PAD, FINGER 1, STRANDBEEST V2',
        ('bde', 2): 'TRIANGLE, BDE, FINGER 2 (MIRROR), STRANDBEEST V2',
        ('ghi', 2): 'TRIANGLE, GHI, PAD, FINGER 2 (MIRROR), STRANDBEEST V2'}


def pn(key, f):
    return PN[(key, f)] if (key, f) in PN else PN[key]


def comp_name(key, f):
    """Component (and body) name: <PN>_<name> + which finger/instance."""
    return f"{parts.fname(pn(key, f))}_F{f}"


cmds = []


def c(command, **params):
    cmds.append({"command": command, "params": params})


def fx(v):
    return round(v, 4)


# ------------------------------------------------------------------ gears
def inv(a):
    return math.tan(a) - a


def gear_points(center_link, z, phase_deg, mod=MOD, backlash=BACKLASH, n_flank=7):
    """Involute spur gear outline (link frame -> world), a tooth centred at phase_deg."""
    r = mod * z / 2
    rb = r * math.cos(math.radians(20))
    ra = r + mod
    rf = r - 1.25 * mod
    s = math.pi * mod / 2 - backlash / 2              # tooth thickness on the pitch circle
    psi_p = s / (2 * r)
    a_p = math.radians(20)

    def half(R):
        R = max(R, rb)
        return psi_p + inv(a_p) - inv(math.acos(rb / R))

    r0 = max(rb, rf)
    radii = [r0 + (ra - r0) * i / (n_flank - 1) for i in range(n_flank)]
    pts = []
    for k in range(z):
        phi = math.radians(phase_deg) + 2 * math.pi * k / z
        flank = []
        if rf < rb:
            flank.append((rf, half(rb)))
        flank += [(R, half(R)) for R in radii]
        # right flank (clockwise side) root -> tip, then left flank tip -> root
        for R, h in flank:
            pts.append((R, phi - h))
        for R, h in reversed(flank):
            pts.append((R, phi + h))
        # root land to the next tooth
        nxt = phi + 2 * math.pi / z
        h0 = flank[0][1]
        a0, a1 = phi + h0, nxt - h0
        for i in range(1, 3):
            pts.append((rf, a0 + (a1 - a0) * i / 3))
    out = []
    for R, a in pts:
        p = (center_link[0] + R * math.cos(a), center_link[1] + R * math.sin(a))
        out.append(list(W(p)))
    return out


IDLE_T = GEAR_T - GAP   # driven gears (idlers, wheel) stop 0.5 under the crank tops: the J1 hub on each crank
                        # sweeps over their tooth tips (flush tops would rub)


def gear_body(name, center_link, z, phase, body, op="new", thick=GEAR_T):
    c("sketch.create", plane="XY", offset=f"{HORN_TOP} mm", name=f"{name}_sk")
    c("sketch.line", points=gear_points(center_link, z, phase), closed=True)
    c("sketch.finish")
    params = dict(distance=f"{thick} mm", operation=op, name=name)
    if op == "new":
        params["body_name"] = body
    else:
        params["targets"] = [body]
    c("solid.extrude", **params)


def cyl(d, z0, h, pt, op, body, name):
    c("solid.cylinder", diameter=d if isinstance(d, str) else f"{d} mm", height=f"{fx(h)} mm",
      base=[fx(pt[0]), fx(pt[1]), fx(z0)], operation=op, targets=[body], name=name)


def slot(name, p, q, z0, body, op, h=LINK_T):
    c("sketch.create", plane="XY", offset=f"{fx(z0)} mm", name=f"{name}_sk")
    c("sketch.slot.center_to_center", p0=list(p), p1=list(q), width=BAR_W)
    c("sketch.finish")
    params = dict(distance=f"{h} mm", operation=op, name=name)
    if op == "new":
        params["body_name"] = body
    else:
        params["targets"] = [body]
    c("solid.extrude", **params)


def new_component(name, grounded=False):
    c("component.activate", component=0)
    c("component.create", name=name, activate=True, grounded=grounded)


def hull(points):
    pts = sorted(set(points))

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


def _phases():
    """Tooth phase (link-frame angle of a tooth centre) for each gear along the O1 -> O2 line (-90 deg).
    Crank 1 has a tooth pointing at idler 1; every partner needs a gap where the other has a tooth.
    For a gear with z teeth the opposite direction (180 deg = z/2 pitches) shows the same state if z is even."""
    chain = [('crank1', ZC), ('idler1', ZI), ('idler2', ZI), ('crank2', ZC)]
    ph, tooth_down = {}, True          # crank 1: tooth toward the next gear (down, -90)
    ph['crank1'] = -90.0
    for name, z in chain[1:]:
        up_is_tooth = not tooth_down   # mesh with the gear above: opposite state
        ph[name] = 90.0 if up_is_tooth else 90.0 + 180.0 / z
        tooth_down = up_is_tooth if z % 2 == 0 else not up_is_tooth
    return ph


PH = _phases()
SX, SY = 22.7, 12.4
ZB = -21.4
LINK_KEYS = ('j', 'k', 'c', 'f', 'bde', 'ghi')
LEG_JOINTS = [("J1_j", 'crank', 'j', 'J1'), ("J1_k", 'crank', 'k', 'J1'), ("G_bde", 'frame', 'bde', 'G'),
              ("G_c", 'frame', 'c', 'G'), ("J2_j_bde", 'j', 'bde', 'J2'), ("J3_bde_f", 'bde', 'f', 'J3'),
              ("J4_k_c", 'k', 'c', 'J4'), ("J4_c_ghi", 'c', 'ghi', 'J4'), ("J5_f_ghi", 'f', 'ghi', 'J5')]


def occ(key, f):
    return f"{comp_name(key, f)}:1"


def rev(name, a, b, pt, z):
    c("joint.as_built", type="revolute", a=a, b=b, at={"point": [fx(pt[0]), fx(pt[1]), z], "z": [0, 0, 1]}, name=name)


class Variant:
    """v2 behaviour; subclasses (gen_v3.py) override the hooks."""
    assy_pn = "GRIP-9003"
    assy_desc = "ASSY, GRIPPER, DUAL FINGER, STRANDBEEST V2"
    vdir = 'strandbeest_gripper/v2_dual-finger'

    @property
    def out(self):
        return f"{self.vdir}/cad/{parts.fname(self.assy_pn)}.json"
    pn = {}                      # part-number overrides {(key, f) or key: PN}
    desc = {}
    has_servo = True             # False: no servo sleeve / model; crank 1 runs on an M3 axle like crank 2
    plate_z = (PLATE_Z0, PLATE_Z1)
    drive = ("O1_crank", 1.0)    # joint you turn, and its angle per degree of crank 1 (verifiers use it)

    def params(self):
        return []

    def frame_discs(self):
        return []

    def frame_extra(self, fb):
        pass

    def ghi_tip(self, f, body, z0):
        mid = z0 + LINK_T / 2
        cyl("pad_d", mid - 7.5, 15, J[f]['F'], "join", body, f"pad{f}")

    def extra_parts(self):
        """Build extra components; return [(key, f), ...] for metadata/exports."""
        return []

    def extra_joints(self):
        pass


def build_link(key, f, Jf, z0, body, variant, mark=None, tag=None, mark_name=None):
    tag = tag or body
    if key in BARS:
        p, q = BARS[key]
        slot(f"{tag}_bar", Jf[p], Jf[q], z0, body, "new")
    else:
        pts = TRIS[key]
        c("sketch.create", plane="XY", offset=f"{fx(z0)} mm", name=f"{tag}_plate_sk")
        c("sketch.line", points=[list(Jf[n]) for n in pts], closed=True)
        c("sketch.finish")
        c("solid.extrude", distance=f"{LINK_T} mm", operation="new", body_name=body, name=f"{tag}_plate")
        for i in range(3):
            slot(f"{tag}_edge{i}", Jf[pts[i]], Jf[pts[(i + 1) % 3]], z0, body, "join")
    # hubs: this link is the lower member of a column with empty layers above it
    for P, owners in PINS.items():
        if key not in owners:
            continue
        ls = sorted(LAYER[o] for o in owners)
        i = ls.index(LAYER[key])
        if i + 1 < len(ls) and ls[i + 1] > LAYER[key] + 1:
            top = zb(ls[i + 1]) - GAP
            cyl(BAR_W, zt(LAYER[key]) - 0.01, top - zt(LAYER[key]) + 0.01, Jf[P], "join", body, f"{tag}_hub_{P}")
    for n in HOLES[key]:
        d = "shoulder_d" if n == 'J1' else "pin_d"
        cyl(d, z0 - 0.5, 30, Jf[n], "cut", body, f"{tag}_hole_{n}")
    if key == 'bde' and mark:
        pts = TRIS[key]
        cx = sum(Jf[n][0] for n in pts) / 3
        cy = sum(Jf[n][1] for n in pts) / 3
        mark_name = mark_name or f"{tag}_mark"
        c("sketch.create", plane="XY", offset=f"{fx(z0 + LINK_T - 0.6)} mm", name=f"{mark_name}_sk")
        c("sketch.text", text=mark, at=[fx(cx - 4.5), fx(cy - 1.6)], height=3.2)
        c("sketch.finish")
        c("solid.extrude", distance="0.7 mm", operation="cut", targets=[body], name=mark_name)


def crank_gear(f, Jf, body, center_link, phase, on_horn, tag=None):
    gear_body(f"gear_{tag or body}", center_link, ZC, phase, body)
    if on_horn:   # on the servo horn: centre access, 2 horn screws away from J1
        cyl(5, HORN_TOP - 0.5, GEAR_T + 1, Jf['O'], "cut", body, "horn_screw_access")
        j1b = math.degrees(math.atan2(Jf['J1'][1] - A[1], Jf['J1'][0] - A[0]))
        for b in sorted([45, 135, 225, 315], key=lambda b: -abs((b - j1b + 180) % 360 - 180))[:2]:
            p = (A[0] + 4.95 * math.cos(math.radians(b)), A[1] + 4.95 * math.sin(math.radians(b)))
            cyl("pin_d", HORN_TOP - 0.5, GEAR_T + 1, p, "cut", body, f"horn_screw_{b}")
            cyl(6, HORN_TOP + GEAR_T - 3, 3.5, p, "cut", body, f"horn_cbore_{b}")
    else:        # on an M3 axle; thin nut recessed in the top (j passes over this axis)
        cyl("pin_d", HORN_TOP - 0.5, GEAR_T + 1, Jf['O'], "cut", body, "axle_bore")
        cyl("thin_nut_d", HORN_TOP + GEAR_T - 2.2, 3, Jf['O'], "cut", body, "thin_nut_recess")
    # J1: hub up to the first link above, bore for the shoulder, tapped into the gear
    above = sorted(LAYER[o] for o in PINS['J1'] if o != 'crank')[0]
    hub_top = zb(above) - GAP
    cyl(BAR_W, HORN_TOP + GEAR_T - 0.01, hub_top - (HORN_TOP + GEAR_T) + 0.01, Jf['J1'], "join", body, "J1_hub")
    cyl("shoulder_d", HORN_TOP + GEAR_T, hub_top - HORN_TOP - GEAR_T + 0.5, Jf['J1'], "cut", body, "J1_shoulder_bore")
    cyl("tap_d", HORN_TOP - 0.5, GEAR_T + 0.6, Jf['J1'], "cut", body, "J1_tap")


def frame_post_and_axles(fb, pts, tag, pz=None):
    """G post + axle bosses for one leg: pts = {'G': world, 'I': world or None, 'O': world or None}."""
    PLATE_Z0, PLATE_Z1 = pz or (globals()['PLATE_Z0'], globals()['PLATE_Z1'])
    g_lo = min(LAYER[o] for o in PINS['G'])
    for key in ('I', 'O'):
        if pts.get(key):
            cyl(7, PLATE_Z1 - 0.01, HORN_TOP - GAP - PLATE_Z1 + 0.01, pts[key], "join", fb, f"boss_{key}{tag}")
    cyl(7, PLATE_Z1 - 0.01, zb(g_lo) - GAP - PLATE_Z1 + 0.01, pts['G'], "join", fb, f"post_G{tag}")
    for key in ('G', 'I', 'O'):
        if not pts.get(key):
            continue
        top = zb(g_lo) - GAP if key == 'G' else HORN_TOP - GAP
        cyl("pin_d", PLATE_Z0 - 0.5, top - PLATE_Z0 + 1, pts[key], "cut", fb, f"axle_{key}{tag}")
        cyl("head_d", PLATE_Z0 - 0.5, 3.5, pts[key], "cut", fb, f"axle_cbore_{key}{tag}")


def leg_joints(f, crank_occ, link_occ, Jf, suffix):
    for name, a, b, n in LEG_JOINTS:
        oa = {'frame': occ('frame', 1), 'crank': crank_occ}.get(a) or link_occ(a)
        rev(f"{name}_{suffix}", oa, link_occ(b), Jf[n], 40.0)


SERVO = parts.fname('LIB-0009')
PARTS = []
BASE_PN, BASE_DESC = dict(PN), dict(DESC)


def rev_of(v, p):
    """Revision of part p in variant v (X1 unless the variant raises it, e.g. v5's labelled parts)."""
    return getattr(v, 'revs', {}).get(p, 'X1')


def build(variant=None):
    v = variant or Variant()
    cmds.clear()
    PN.clear(); PN.update(BASE_PN); PN.update(v.pn)
    DESC.clear(); DESC.update(BASE_DESC); DESC.update(v.desc)
    # ------------------------------------------------------------ parameters (documented values)
    c("document.metadata.set", values={"part_number": v.assy_pn, "description": v.assy_desc,
                                       "revision": "X1", "project": "strandbeest_gripper"})
    for name, expr, why in [
        ("pin_d", "3.4 mm", "rotating M3 pin hole, ISO 273 medium"),
        ("shoulder_d", "4.2 mm", "J1 runs on an ISO 7379 shoulder screw, shoulder 4 mm"),
        ("tap_d", "2.5 mm", "M3 thread-forming hole (shoulder screw into the crank gear)"),
        ("head_d", "6.5 mm", "M3 socket head counterbore"),
        ("thin_nut_d", "7 mm", "recess for an M3 thin nut (DIN 439) on crank 2"),
        ("fit_clr", "0.2 mm", "servo sleeve clearance per side"),
        ("wall", "2.5 mm", "frame wall"),
        ("pad_d", f"{PAD_D} mm", f"fingertip pad diameter; clamp gap = {2 * (abs(YM) - YMIN_ABS):.2f} mm - pad_d"),
    ] + v.params():
        c("parameters.add", name=name, expression=expr, comment=why)

    # ------------------------------------------------------------ frame GRIP-0011
    fb = comp_name('frame', 1)
    c("component.create", name=fb, activate=True, grounded=True)
    pz0, pz1 = v.plate_z
    if v.has_servo:
        c("solid.box", length=f"2 * ({SX} mm + fit_clr + wall)", width=f"2 * ({SY} mm + fit_clr + wall)",
          height=f"{pz1 - ZB} mm", center=[0, 0, (ZB + pz1) / 2], operation="new", body_name=fb, name="sleeve")
    # base plate: hull of discs around every axle / post, in the link frame
    disc = [(JL[1]['O'], 13), (JL[1]['G'], 7), (JL[1]['I'], 8), (JL[2]['I'], 8), (JL[2]['O'], 13), (JL[2]['G'], 7)]
    disc += v.frame_discs()
    cloud = [(p[0] + r * math.cos(a * math.pi / 18), p[1] + r * math.sin(a * math.pi / 18)) for p, r in disc for a in range(36)]
    plate = [list(W(p)) for p in hull(cloud)]
    c("sketch.create", plane="XY", offset=f"{pz0} mm", name="plate_sk")
    c("sketch.line", points=plate, closed=True)
    c("sketch.finish")
    if v.has_servo:
        c("solid.extrude", distance=f"{pz1 - pz0} mm", operation="join", targets=[fb], name="plate")
        c("solid.box", length=f"2 * ({SX} mm + fit_clr)", width=f"2 * ({SY} mm + fit_clr)", height=f"{17.5 + 19.4} mm",
          center=[0, 0, (17.5 - 19.4) / 2], operation="cut", targets=[fb], name="servo_pocket")
        c("solid.box", length="6 mm", width="14 mm", height="26 mm", center=[-SX - 1.5, 0, 1.5],
          operation="cut", targets=[fb], name="cable_notch")
    else:
        c("solid.extrude", distance=f"{pz1 - pz0} mm", operation="new", body_name=fb, name="plate")
    # bosses under the idlers and crank 2 (top 0.5 under the gears), G posts up to the lowest G link
    for f in (1, 2):
        frame_post_and_axles(fb, {'G': J[f]['G'], 'I': J[f]['I'],
                                  'O': J[f]['O'] if (f == 2 or not v.has_servo) else None}, f, v.plate_z)
    v.frame_extra(fb)

    # ------------------------------------------------------------ gears
    for f in (1, 2):
        key = f'crank{f}'
        body = comp_name(key, 1)
        new_component(body)
        crank_gear(f, J[f], body, JL[f]['O'], PH[key], on_horn=(f == 1 and v.has_servo), tag=key)
    for f in (1, 2):
        body = comp_name('idler', f)
        new_component(body)
        gear_body(f"gear_idler{f}", JL[f]['I'], ZI, PH[f'idler{f}'], body, thick=IDLE_T)
        cyl("pin_d", HORN_TOP - 0.5, GEAR_T + 1, J[f]['I'], "cut", body, f"idler{f}_bore")

    # ------------------------------------------------------------ links (both fingers)
    for f in (1, 2):
        for key in LINK_KEYS:
            body = comp_name(key, f)
            new_component(body)
            z0 = zb(LAYER[key])
            build_link(key, f, J[f], z0, body, v, mark=f"UP{f}", tag=f"{key}{f}", mark_name=f"mark{f}")
            if key == 'ghi':
                v.ghi_tip(f, body, z0)
    extra = v.extra_parts()

    # ------------------------------------------------------------ servo, joints, gear links
    c("component.activate", component=0)
    if v.has_servo:
        c("file.insert_step", path=f"lib/sts3215/{SERVO}.step", name=SERVO)
        c("joint.as_built", type="rigid", a=occ('frame', 1), b=SERVO + ":1", name="servo_in_frame")
    rev("O1_crank", occ('frame', 1), occ('crank1', 1), J[1]['O'], HORN_TOP)
    rev("O2_crank", occ('frame', 1), occ('crank2', 1), J[2]['O'], HORN_TOP)
    for f in (1, 2):
        rev(f"I{f}_idler", occ('frame', 1), occ('idler', f), J[f]['I'], HORN_TOP)
        leg_joints(f, occ(f'crank{f}', 1), lambda k, f=f: occ(k, f), J[f], f)
    c("joint.gear", a="O1_crank", b="I1_idler", ra=RC, rb=RI)
    c("joint.gear", a="I1_idler", b="I2_idler", ra=RI, rb=RI)
    c("joint.gear", a="I2_idler", b="O2_crank", ra=RI, rb=RC)
    v.extra_joints()

    # ------------------------------------------------------------ metadata + exports
    PARTS[:] = [('frame', 1), ('crank1', 1), ('crank2', 1), ('idler', 1), ('idler', 2)] + \
        [(k, f) for f in (1, 2) for k in LINK_KEYS] + extra
    for key, f in PARTS:
        c("component.metadata.set", component=comp_name(key, f), part_number=pn(key, f),
          description=DESC[(key, f)] if (key, f) in DESC else DESC[key], revision=rev_of(v, pn(key, f)),
          bom_type="normal")
    if v.has_servo:
        c("component.metadata.set", component=SERVO, part_number="LIB-0009", description="SERVO, STS3215",
          bom_type="purchased")
    exported = set()
    for key, f in PARTS:
        p = pn(key, f)
        if p in exported:
            continue
        exported.add(p)
        for ext, cmd in (('step', 'file.export_step'), ('stl', 'file.export_stl'), ('3mf', 'file.export_3mf')):
            params = dict(path=f"{v.vdir}/exports/{parts.export(p, rev_of(v, p), ext)}", bodies=[comp_name(key, f)])
            if ext != 'step':
                params["quality"] = "fine"
            c(cmd, **params)
    return cmds


def write(v, cmd_list):
    for sub in ('cad', 'exports', 'docs'):
        os.makedirs(os.path.join(v.vdir, sub), exist_ok=True)
    with open(v.out, 'w') as fh:
        fh.write('[\n' + ',\n'.join(' ' + json.dumps(x, separators=(',', ':')) for x in cmd_list) + '\n]\n')


build()          # v2 by default (verify_dual imports PARTS from here)

if __name__ == '__main__':
    check_reference()
    write(Variant(), build())
    print(Variant().out, len(cmds), 'steps; layers', NL, LAYER, 'stack top %.1f' % STACK_TOP)
    print('crank distance %.1f, mirror y %.2f, clamp gap at pad_d %.0f: %.2f mm' % (D_CRANKS, YM, PAD_D, CLAMP_GAP))
