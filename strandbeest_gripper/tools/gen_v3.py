"""Strandbeest gripper v3: three ways to give the v2 feeder long jaws along its stroke axis.

The foot triangle (g-h-i) turns ~30 deg while the pads are clamped, so a rigid jaw sticking
out along the stroke would swing its tip into the other jaw. Three answers, each its own
assembly on the v2 base (gen_dual.py, GRIP-9003 unchanged):

    v3a  GRIP-9004  pivoting jaws: a jaw on a pin at the foot point F of each finger.
                    In the real part the jaws self-align on the item; in CAD a parallel
                    relation to a frame reference stands in for that contact.
    v3b  GRIP-9005  parallel twin legs: a second, identical leg per finger, offset
                    TWIN_D along the stroke and geared to the same crank angle. A jaw
                    pinned to both feet translates without turning (parallelogram).
    v3c  GRIP-9006  short rigid nose on the v2 pad, recessed so the noses never collide.

"+x" for the jaws is the gripper's own stroke axis (link -x): it is mirror-invariant, so the
two jaws stay parallel to each other. It is 11.6 deg off the servo/world x axis.

    python3 strandbeest_gripper/tools/gen_v3.py [a|b|c ...]      (from the repo root; default all)
    then: tools/build.sh strandbeest_gripper/v3a_pivot-jaws   (… v3b_twin-legs, v3c_rigid-nose)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_dual as g  # noqa: E402
from gen_dual import c, cyl, slot, new_component, occ, rev, J, JL, W, fx, PINS, LAYER  # noqa: E402
from jansen import pose  # noqa: E402

U = (-1.0, 0.0)                         # jaw direction in the link frame (stroke axis, toward world +x)
TOP = g.STACK_TOP                       # 49.2: top of k
JAW_Z0 = TOP + 0.5 + 4.0 + 0.5          # above the J4 nyloc on k (and the J1 shoulder head)
JAW_H = 8.0
JAW_W = g.PAD_D                         # jaw thickness across the clamp = pad diameter (faces on the clamp line)
F_HUB_D = g.PAD_D


def lk(p, d):
    return (p[0] + d * U[0], p[1] + d * U[1])


def ghi_hub(f, body, z0, Jf, tag):
    """g-h-i without the pad: a Ø11 hub at F from the plate up to just under the jaw, pin bore."""
    cyl(F_HUB_D, z0 + g.LINK_T - 0.01, JAW_Z0 - g.GAP - (z0 + g.LINK_T) + 0.01, Jf['F'], "join", body, f"{tag}_F_hub")
    cyl("pin_d", z0 - 0.5, JAW_Z0 - z0, Jf['F'], "cut", body, f"{tag}_F_bore")


SLOT_L = 2.0          # parallelogram jaw: the B-end bore is a short slot along the jaw (no binding)


def jaw_body(name, p, q, bores, slot_end=None):
    c("sketch.create", plane="XY", offset=f"{fx(JAW_Z0)} mm", name=f"{name}_sk")
    c("sketch.slot.center_to_center", p0=list(p), p1=list(q), width=JAW_W)
    c("sketch.finish")
    c("solid.extrude", distance=f"{JAW_H} mm", operation="new", body_name=name, name=name)
    for i, b in enumerate(bores):
        cyl("pin_d", JAW_Z0 - 0.5, JAW_H + 1, b, "cut", name, f"{name}_bore{i}")
    if slot_end:
        b, d = slot_end                # centre and unit direction (world) of the slot
        a0 = (b[0] - d[0] * SLOT_L / 2, b[1] - d[1] * SLOT_L / 2)
        a1 = (b[0] + d[0] * SLOT_L / 2, b[1] + d[1] * SLOT_L / 2)
        c("sketch.create", plane="XY", offset=f"{fx(JAW_Z0 - 0.5)} mm", name=f"{name}_slot_sk")
        c("sketch.slot.center_to_center", p0=[fx(a0[0]), fx(a0[1])], p1=[fx(a1[0]), fx(a1[1])], width=3.4)
        c("sketch.finish")
        c("solid.extrude", distance=f"{JAW_H + 1} mm", operation="cut", targets=[name], name=f"{name}_slot")


# ---------------------------------------------------------------------------- v3a pivoting jaws
class Pivot(g.Variant):
    assy_pn = "GRIP-9004"
    assy_desc = "ASSY, GRIPPER, DUAL FINGER, PIVOT JAWS, STRANDBEEST V3A"
    vdir = 'strandbeest_gripper/v3a_pivot-jaws'
    JAW_L = 25.0
    pn = {('ghi', 1): 'GRIP-0023', ('ghi', 2): 'GRIP-0024', 'jawp': 'GRIP-0025'}
    desc = {('ghi', 1): 'TRIANGLE, GHI, F HUB, FINGER 1, STRANDBEEST V3',
            ('ghi', 2): 'TRIANGLE, GHI, F HUB, FINGER 2 (MIRROR), STRANDBEEST V3',
            'jawp': 'JAW, PIVOT, 25 MM, STRANDBEEST V3A'}

    def ghi_tip(self, f, body, z0):
        ghi_hub(f, body, z0, J[f], f"ghi{f}")

    def extra_parts(self):
        for f in (1, 2):
            name = g.comp_name('jawp', f)
            new_component(name)
            tip = W(lk(JL[f]['F'], self.JAW_L))
            jaw_body(name, J[f]['F'], tip, [J[f]['F']])
        # hidden reference in the frame component: a thin plate whose long faces run along the
        # stroke axis; the jaws are held parallel to it (stand-in for self-alignment on the item)
        c("component.activate", component=g.comp_name('frame', 1))
        a, b = W(lk(JL[1]['O'], 5)), W(lk(JL[1]['O'], 25))
        c("sketch.create", plane="XY", offset=f"{fx(self.plate_z[0] - 3)} mm", name="jaw_ref_sk")
        c("sketch.slot.center_to_center", p0=list(a), p1=list(b), width=2.0)
        c("sketch.finish")
        c("solid.extrude", distance="1 mm", operation="new", body_name="jaw_ref", name="jaw_ref")
        c("browser.visibility", items=["jaw_ref"], visible=False)
        return [('jawp', 1), ('jawp', 2)]

    def extra_joints(self):
        for f in (1, 2):
            rev(f"F_jaw_{f}", occ('ghi', f), occ('jawp', f), J[f]['F'], JAW_Z0)
            # long side face of the jaw: offset from the F-tip line by half the jaw width
            mid = lk(JL[f]['F'], self.JAW_L / 2)
            side = W((mid[0], mid[1] + JAW_W / 2))
            ref_mid = lk(JL[1]['O'], 15)
            ref_side = W((ref_mid[0], ref_mid[1] + 1.0))
            c("joint.create", type="parallel",
              a={"occurrence": occ('frame', 1), "face": [fx(ref_side[0]), fx(ref_side[1]), fx(self.plate_z[0] - 2.5)]},
              b={"occurrence": occ('jawp', f), "face": [fx(side[0]), fx(side[1]), fx(JAW_Z0 + JAW_H / 2)]},
              flip=True, name=f"jaw_parallel_{f}")


# ---------------------------------------------------------------------------- v3c short rigid nose
class Tip(g.Variant):
    assy_pn = "GRIP-9006"
    assy_desc = "ASSY, GRIPPER, DUAL FINGER, RIGID NOSE, STRANDBEEST V3C"
    vdir = 'strandbeest_gripper/v3c_rigid-nose'
    NOSE_L = 5.0          # nose tip centre beyond F, along the stroke axis (longer needs more recess: see README)
    NOSE_R = 3.0          # nose tip radius
    MIN_GAP = 0.5         # nose-to-nose clearance over the full turn
    pn = {('ghi', 1): 'GRIP-0026', ('ghi', 2): 'GRIP-0027'}
    desc = {('ghi', 1): 'TRIANGLE, GHI, PAD + NOSE, FINGER 1, STRANDBEEST V3C',
            ('ghi', 2): 'TRIANGLE, GHI, PAD + NOSE, FINGER 2 (MIRROR), STRANDBEEST V3C'}

    def __init__(self):
        self.inset = self.solve_inset()

    def nose_tip(self, p, inset, f=1):
        """Nose tip centre (link frame) of finger 1 at pose p: rotates with the foot (J4->F)."""
        a = math.atan2(p['F'][1] - p['J4'][1], p['F'][0] - p['J4'][0]) - A0
        # at theta = 0: along U; its inner edge on the pad's clamp line, then moved away by `inset`
        v = (self.NOSE_L * U[0], self.NOSE_L * U[1] - (g.PAD_D / 2 - self.NOSE_R) + inset)   # inner edge on the clamp line
        return (p['F'][0] + v[0] * math.cos(a) - v[1] * math.sin(a), p['F'][1] + v[0] * math.sin(a) + v[1] * math.cos(a))

    def gaps(self, inset):
        out = []
        for t in range(360):
            p = pose(math.radians(t), g.S)
            n1 = self.nose_tip(p, inset)
            n2 = g.mir(n1)
            f1, f2 = p['F'], g.mir(p['F'])
            # tapered capsule (pad circle -> nose circle) vs its mirror: sample along the axes
            best = 1e9
            for i in range(11):
                s = i / 10
                c1 = (f1[0] + (n1[0] - f1[0]) * s, f1[1] + (n1[1] - f1[1]) * s)
                r1 = g.PAD_D / 2 + (self.NOSE_R - g.PAD_D / 2) * s
                for k in range(11):
                    u = k / 10
                    c2 = (f2[0] + (n2[0] - f2[0]) * u, f2[1] + (n2[1] - f2[1]) * u)
                    r2 = g.PAD_D / 2 + (self.NOSE_R - g.PAD_D / 2) * u
                    best = min(best, math.hypot(c1[0] - c2[0], c1[1] - c2[1]) - r1 - r2)
            out.append((t, best))
        return out

    def solve_inset(self):
        inset = 0.0
        while min(gp for _, gp in self.gaps(inset)) < self.MIN_GAP:
            inset += 0.1
        return round(inset, 2)

    def ghi_tip(self, f, body, z0):
        mid = z0 + g.LINK_T / 2
        cyl("pad_d", mid - 7.5, 15, J[f]['F'], "join", body, f"pad{f}")
        sgn = 1 if f == 1 else -1       # away from the clamp line, in the link frame
        tipl = (JL[f]['F'][0] + self.NOSE_L * U[0], JL[f]['F'][1] + sgn * (self.inset - (g.PAD_D / 2 - self.NOSE_R)))
        tip = W(tipl)
        # nose: hull of the pad circle and the tip circle, same height as the pad
        pts = []
        for k in range(48):
            a = 2 * math.pi * k / 48
            rp = g.PAD_D / 2 - 0.3      # inside the pad cylinder: coincident faces break the union
            pts.append((JL[f]['F'][0] + rp * math.cos(a), JL[f]['F'][1] + rp * math.sin(a)))
            pts.append((tipl[0] + self.NOSE_R * math.cos(a), tipl[1] + self.NOSE_R * math.sin(a)))
        c("sketch.create", plane="XY", offset=f"{fx(mid - 7.5)} mm", name=f"nose{f}_sk")
        c("sketch.line", points=[list(W(p)) for p in g.hull(pts)], closed=True)
        c("sketch.finish")
        c("solid.extrude", distance="15 mm", operation="join", targets=[body], name=f"nose{f}")


P0 = pose(0.0, g.S)
A0 = math.atan2(P0['F'][1] - P0['J4'][1], P0['F'][0] - P0['J4'][0])


# ---------------------------------------------------------------------------- v3b parallel twin legs
TWIN_D = 50.0                       # leg B = leg A shifted along the stroke (>= 46 mm clears every part)
ZX = 60                             # big idler between crank A and crank B (clears both G posts)
RX = g.MOD * ZX / 2


def mesh_phase(ph_a, z_a, c_a, c_b, z_b):
    """Tooth phase of gear b (link-frame angle) so it meshes with gear a (centres in the link frame)."""
    ra, rb = g.MOD * z_a / 2, g.MOD * z_b / 2
    alpha = math.degrees(math.atan2(c_b[1] - c_a[1], c_b[0] - c_a[0]))
    pa = 360.0 / z_a
    d = ((alpha - ph_a + pa / 2) % pa) - pa / 2                # line of centres, measured from a's nearest tooth
    s = -ra * math.radians(d)                                  # that tooth's arc offset from the line (CCW +)
    p_arc = math.pi * g.MOD                                    # circular pitch
    # b sees the same point clockwise from its own line (alpha + 180); it needs a gap there
    return alpha + 180.0 - math.degrees((s - p_arc / 2) / rb)


class Twin(g.Variant):
    assy_pn = "GRIP-9005"
    assy_desc = "ASSY, GRIPPER, DUAL FINGER, TWIN LEG PARALLEL JAWS, STRANDBEEST V3B"
    vdir = 'strandbeest_gripper/v3b_twin-legs'
    OVERHANG = 30.0          # jaw beyond leg B's foot (leg B reaches ~26 mm past it along the stroke)
    pn = {('ghi', 1): 'GRIP-0023', ('ghi', 2): 'GRIP-0024', 'frame': 'GRIP-0028', ('crankB', 1): 'GRIP-0029',
          ('crankB', 2): 'GRIP-0032', 'idlerX': 'GRIP-0030', 'jawt': 'GRIP-0031'}   # crank B gears: tooth phase to J1 differs per finger
    desc = {('ghi', 1): 'TRIANGLE, GHI, F HUB, FINGER 1, STRANDBEEST V3',
            ('ghi', 2): 'TRIANGLE, GHI, F HUB, FINGER 2 (MIRROR), STRANDBEEST V3',
            'frame': 'FRAME, TWIN LEG, STRANDBEEST V3B', ('crankB', 1): 'GEAR, CRANK, TWIN LEG, FINGER 1, Z20 M1',
            ('crankB', 2): 'GEAR, CRANK, TWIN LEG, FINGER 2, Z20 M1',
            'idlerX': 'GEAR, IDLER, Z60 M1', 'jawt': 'JAW, TWIN LEG, 91 MM, STRANDBEEST V3B'}

    def __init__(self):
        self.JB, self.JBL, self.X, self.XL, self.ph = {}, {}, {}, {}, {}
        w0, w1 = W((0, 0)), W(U)
        self.UW = (w1[0] - w0[0], w1[1] - w0[1])          # stroke axis in world
        for f in (1, 2):
            self.JBL[f] = {k: lk(v, TWIN_D) for k, v in JL[f].items() if k != 'I'}
            self.JB[f] = {k: W(v) for k, v in self.JBL[f].items()}
            mid = lk(JL[f]['O'], TWIN_D / 2)
            h = math.sqrt((g.RC + RX) ** 2 - (TWIN_D / 2) ** 2)
            sgn = 1 if f == 1 else -1           # away from the mirror line
            self.XL[f] = (mid[0], mid[1] + sgn * h)
            self.X[f] = W(self.XL[f])
            ph_a = g.PH[f'crank{f}']
            self.ph[('X', f)] = mesh_phase(ph_a, g.ZC, JL[f]['O'], self.XL[f], ZX)
            self.ph[('B', f)] = mesh_phase(self.ph[('X', f)], ZX, self.XL[f], self.JBL[f]['O'], g.ZC)

    def frame_discs(self):
        d = []
        for f in (1, 2):
            d += [(self.JBL[f]['O'], 13), (self.JBL[f]['G'], 7), (self.XL[f], 8)]
        return d

    def frame_extra(self, fb):
        for f in (1, 2):
            g.frame_post_and_axles(fb, {'G': self.JB[f]['G'], 'I': self.X[f], 'O': self.JB[f]['O']}, f"B{f}")

    def ghi_tip(self, f, body, z0):
        ghi_hub(f, body, z0, J[f], f"ghi{f}")

    def extra_parts(self):
        parts = []
        for f in (1, 2):
            name = g.comp_name('crankB', f)
            new_component(name)
            g.crank_gear(f, self.JB[f], name, self.JBL[f]['O'], self.ph[('B', f)], on_horn=False, tag=f"crankB{f}")
            name = g.comp_name('idlerX', f)
            new_component(name)
            g.gear_body(f"gear_idlerX{f}", self.XL[f], ZX, self.ph[('X', f)], name, thick=g.IDLE_T)
            cyl("pin_d", g.HORN_TOP - 0.5, g.GEAR_T + 1, self.X[f], "cut", name, f"idlerX{f}_bore")
            for key in g.LINK_KEYS:
                body = f"{g.parts.fname(g.pn(key, f))}_F{f}B"
                new_component(body)
                z0 = g.zb(LAYER[key])
                g.build_link(key, f, self.JB[f], z0, body, self, mark=f"UP{f}", tag=f"{key}{f}B")
                if key == 'ghi':
                    ghi_hub(f, body, z0, self.JB[f], f"ghi{f}B")
                c("component.metadata.set", component=body, part_number=g.pn(key, f),
                  description=g.DESC[(key, f)] if (key, f) in g.DESC else g.DESC[key], revision="X1", bom_type="normal")
            name = g.comp_name('jawt', f)
            new_component(name)
            tip = W(lk(self.JBL[f]['F'], self.OVERHANG))       # overhang past leg B so the jaw reaches out in +x
            jaw_body(name, J[f]['F'], tip, [J[f]['F']], slot_end=(self.JB[f]['F'], self.UW))
            parts += [('crankB', f), ('idlerX', f), ('jawt', f)]
        return parts

    def extra_joints(self):
        for f in (1, 2):
            rev(f"OB{f}_crank", occ('frame', 1), occ('crankB', f), self.JB[f]['O'], g.HORN_TOP)
            rev(f"X{f}_idler", occ('frame', 1), occ('idlerX', f), self.X[f], g.HORN_TOP)
            g.leg_joints(f, occ('crankB', f), lambda k, f=f: f"{g.parts.fname(g.pn(k, f))}_F{f}B:1", self.JB[f], f"{f}B")
            c("joint.gear", a=f"O{f}_crank", b=f"X{f}_idler", ra=g.RC, rb=RX)
            c("joint.gear", a=f"X{f}_idler", b=f"OB{f}_crank", ra=RX, rb=g.RC)
            rev(f"FA_jaw_{f}", occ('ghi', f), occ('jawt', f), J[f]['F'], JAW_Z0)
            p = self.JB[f]['F']
            c("joint.as_built", type="pin_slot", a=f"{g.parts.fname(g.pn('ghi', f))}_F{f}B:1", b=occ('jawt', f),
              at={"point": [fx(p[0]), fx(p[1]), JAW_Z0], "z": [0, 0, 1], "x": [fx(self.UW[0]), fx(self.UW[1]), 0]},
              name=f"FB_jaw_{f}")


# ---------------------------------------------------------------------------- v4 thumb wheel (hand drive)
ZW = 40                              # thumb-wheel gear: crank turns ZW/ZC = 2 x per wheel turn
RW = g.MOD * ZW / 2
WHEEL_ANGLE = 40.0                   # link-frame bearing of the wheel from crank 1 (free sector 0..70 deg)
RIM_R, RIM_KNURLS = 25.0, 48


class Thumb(Pivot):
    """v3a (pivot jaws) without the servo: a knurled thumb wheel geared to crank 1 drives everything."""
    assy_pn = "GRIP-9007"
    assy_desc = "ASSY, GRIPPER, DUAL FINGER, PIVOT JAWS, THUMB WHEEL, STRANDBEEST V4"
    vdir = 'strandbeest_gripper/v4_thumb-wheel'
    has_servo = False
    plate_z = (0.0, 4.0)
    drive = ("W_wheel", -g.RC / RW)          # wheel degrees per crank degree (opposite sense)
    pn = dict(Pivot.pn, frame='GRIP-0033', crank1='GRIP-0034', wheel='GRIP-0035')
    desc = dict(Pivot.desc, frame='FRAME, DUAL FINGER, HAND DRIVE, STRANDBEEST V4',
                crank1='GEAR, CRANK, ON AXLE, Z20 M1', wheel='WHEEL, THUMB, KNURLED D50, GEAR Z40 M1')

    def __init__(self):
        a = math.radians(WHEEL_ANGLE)
        self.WL = (JL[1]['O'][0] + (g.RC + RW) * math.cos(a), JL[1]['O'][1] + (g.RC + RW) * math.sin(a))
        self.Wc = W(self.WL)
        self.phase = mesh_phase(g.PH['crank1'], g.ZC, JL[1]['O'], self.WL, ZW)

    def frame_discs(self):
        return [(self.WL, 9)]

    def frame_extra(self, fb):
        z0, z1 = self.plate_z
        cyl("pin_d", z0 - 0.5, z1 - z0 + 1, self.Wc, "cut", fb, "axle_wheel")
        cyl("head_d", z0 - 0.5, 3.5, self.Wc, "cut", fb, "axle_cbore_wheel")

    def extra_parts(self):
        parts = super().extra_parts()
        name = g.comp_name('wheel', 1)
        new_component(name)
        rim_z0, gear_z0 = self.plate_z[1] + 0.5, g.HORN_TOP - g.GAP
        # knurled rim under the gear layer (it overhangs the base edge: roll it with a thumb)
        pts = []
        for k in range(2 * RIM_KNURLS):
            r = RIM_R if k % 2 == 0 else RIM_R - 0.8
            a = math.pi * k / RIM_KNURLS
            pts.append(list(W((self.WL[0] + r * math.cos(a), self.WL[1] + r * math.sin(a)))))
        c("sketch.create", plane="XY", offset=f"{fx(rim_z0)} mm", name="wheel_rim_sk")
        c("sketch.line", points=pts, closed=True)
        c("sketch.finish")
        c("solid.extrude", distance=f"{fx(gear_z0 - rim_z0)} mm", operation="new", body_name=name, name="wheel_rim")
        # gear on top of the rim, in the gear layer, meshing with crank 1
        c("sketch.create", plane="XY", offset=f"{fx(gear_z0)} mm", name="wheel_gear_sk")
        c("sketch.line", points=g.gear_points(self.WL, ZW, self.phase), closed=True)
        c("sketch.finish")
        c("solid.extrude", distance=f"{fx(g.HORN_TOP + g.IDLE_T - gear_z0)} mm", operation="join", targets=[name],
          name="wheel_gear")
        cyl("pin_d", rim_z0 - 0.5, g.HORN_TOP + g.GEAR_T - rim_z0 + 1, self.Wc, "cut", name, "wheel_bore")
        return parts + [('wheel', 1)]

    def extra_joints(self):
        super().extra_joints()
        rev("W_wheel", occ('frame', 1), occ('wheel', 1), self.Wc, g.HORN_TOP)
        c("joint.gear", a="W_wheel", b="O1_crank", ra=RW, rb=g.RC)


# ---------------------------------------------------------------------------- v4a printed pins
def new_cyl(d, z0, h, pt, body, name):
    c("solid.cylinder", diameter=d, height=f"{fx(h)} mm", base=[fx(pt[0]), fx(pt[1]), fx(z0)],
      operation="new", body_name=body, name=name)


class PrintedPins(Thumb):
    """v4 with every fastener printed: D3 pins (head + D-flat for printing on its side) in the
    unchanged D3.4 holes, held by press-on caps; a printed D4 shoulder pin with a press tip at J1.
    No washers (functional test). Pins and caps sit inside the envelope v4's screws, nuts and
    heads were laid out for (layers.py), so the v4 parts are reused unchanged."""
    assy_pn = "GRIP-9008"
    assy_desc = "ASSY, GRIPPER, THUMB WHEEL, PRINTED PINS, STRANDBEEST V4A"
    vdir = 'strandbeest_gripper/v4a_printed-pins'
    HEAD_H, CAP_H, PIN_R, FLAT = 3.0, 2.0, 1.5, 0.25
    # pin key -> part number (one PN per shank length)
    PINS = {'pin_j3': 'GRIP-0036', 'pin_j4': 'GRIP-0037', 'pin_j25': 'GRIP-0038', 'pin_crank': 'GRIP-0039',
            'pin_gear': 'GRIP-0040', 'pin_jaw': 'GRIP-0041', 'pin_g': 'GRIP-0042'}
    pn = dict(Thumb.pn, **PINS, pin_j1='GRIP-0043', cap='GRIP-0044')
    desc = dict(Thumb.desc, pin_j3='PIN, PRINTED, D3, SHANK 8.5, J3', pin_j4='PIN, PRINTED, D3, SHANK 15.5, J4',
                pin_j25='PIN, PRINTED, D3, SHANK 19, J2 + J5', pin_crank='PIN, PRINTED, D3, SHANK 21.5, CRANK AXLE',
                pin_gear='PIN, PRINTED, D3, SHANK 23.5, IDLER + WHEEL AXLE', pin_jaw='PIN, PRINTED, D3, SHANK 25, JAW PIVOT',
                pin_g='PIN, PRINTED, D3, SHANK 38, G', pin_j1='PIN, PRINTED, SHOULDER D4 X 24.5, PRESS TIP, J1',
                cap='CAP, PRESS-ON, FOR D3 PRINTED PIN')
    SHANK = {'pin_j3': 8.5, 'pin_j4': 15.5, 'pin_j25': 19.0, 'pin_crank': 21.5, 'pin_gear': 23.5,
             'pin_jaw': 25.0, 'pin_g': 38.0}

    def params(self):
        return super().params() + [
            ("ppin_d", "3.0 mm", "printed pin shank: 0.2 mm radial play in the D3.4 holes"),
            ("ppin_head_d", "5.5 mm", "printed pin head = M3 socket head (fits the D6.5 counterbores)"),
            ("ppin_flat", f"{self.FLAT} mm", "D-flat depth on pin + head: print the pin lying on it"),
            ("cap_d", "6.0 mm", "press-on cap, inside the M3 nyloc envelope (6.4) the layers allow for"),
            ("cap_bore", "2.8 mm", "cap hole: 0.2 mm interference on the D3 pin (press fit, NEEDS PRINT TEST)"),
            ("j1_shoulder", "4.0 mm", "J1 shoulder in the D4.2 bores (replaces ISO 7379 D4)"),
            ("j1_head_d", "7.0 mm", "J1 pin head"),
            ("j1_tip_d", "2.7 mm", "J1 press tip into the D2.5 tap hole in the crank gear (NEEDS PRINT TEST)"),
        ]

    def locations(self):
        """(pin key, xy, z_seat = top of head / start of shank, z_cap = cap bottom, attach occurrence)."""
        L, zb, zt = g.LAYER, g.zb, g.zt
        seat = self.plate_z[0] - 0.5 + 3.5          # head top in the base counterbore
        frame = occ('frame', 1)
        locs = [('pin_gear', self.Wc, seat, g.HORN_TOP + g.IDLE_T, frame)]
        for f in (1, 2):
            locs += [('pin_crank', J[f]['O'], seat, g.HORN_TOP + g.GEAR_T - 2.2, frame),
                     ('pin_gear', J[f]['I'], seat, g.HORN_TOP + g.IDLE_T, frame),
                     ('pin_g', J[f]['G'], seat, zt(max(L[o] for o in PINS['G'])), frame),
                     ('pin_jaw', J[f]['F'], zb(L['ghi']), JAW_Z0 + JAW_H, occ('ghi', f))]
            for n, key in (('J2', 'pin_j25'), ('J3', 'pin_j3'), ('J4', 'pin_j4'), ('J5', 'pin_j25')):
                own = PINS[n]
                low = min(own, key=lambda o: L[o])
                locs.append((key, J[f][n], zb(L[low]), zt(max(L[o] for o in own)), occ(low, f)))
        return locs

    def extra_parts(self):
        parts = super().extra_parts()
        count = {}
        self.attach = []
        for key, p, z_seat, z_cap, att in self.locations():
            need = z_cap + self.CAP_H - z_seat
            assert self.SHANK[key] - 0.5 < need <= self.SHANK[key] + 1e-6, (key, need)
            count[key] = count.get(key, 0) + 1
            name = g.comp_name(key, count[key])
            new_component(name)
            z0 = z_seat - self.HEAD_H
            new_cyl("ppin_head_d", z0, self.HEAD_H, p, name, f"{name}_head")
            cyl("ppin_d", z_seat - 0.01, self.SHANK[key] + 0.01, p, "join", name, f"{name}_shank")
            off = self.PIN_R - self.FLAT                # D-flat plane, -y side of the axis
            c("solid.box", length="10 mm", width="5 mm", height=f"{fx(self.HEAD_H + self.SHANK[key] + 2)} mm",
              center=[fx(p[0]), fx(p[1] - off - 2.5), fx(z0 + (self.HEAD_H + self.SHANK[key]) / 2)],
              operation="cut", targets=[name], name=f"{name}_flat")
            parts.append((key, count[key]))
            self.attach.append((att, g.occ(key, count[key])))
            count['cap'] = count.get('cap', 0) + 1
            cname = g.comp_name('cap', count['cap'])
            new_component(cname)
            new_cyl("cap_d", z_cap, self.CAP_H, p, cname, f"{cname}_disc")
            cyl("cap_bore", z_cap - 0.5, self.CAP_H + 1, p, "cut", cname, f"{cname}_bore")
            parts.append(('cap', count['cap']))
            self.attach.append((att, g.occ('cap', count['cap'])))
        # J1: shoulder pin, head on top of k, press tip into the crank gear's tap hole
        for f in (1, 2):
            name = g.comp_name('pin_j1', f)
            new_component(name)
            gear_top = g.HORN_TOP + g.GEAR_T
            top = g.zt(max(g.LAYER[o] for o in PINS['J1'] if o != 'crank'))
            new_cyl("j1_tip_d", g.HORN_TOP + 0.5, gear_top - g.HORN_TOP - 0.5 + 0.01, J[f]['J1'], name, f"{name}_tip")
            cyl("j1_shoulder", gear_top, top - gear_top + 0.01, J[f]['J1'], "join", name, f"{name}_shoulder")
            cyl("j1_head_d", top, self.HEAD_H, J[f]['J1'], "join", name, f"{name}_head")
            parts.append(('pin_j1', f))
            self.attach.append((occ(f'crank{f}', 1), g.occ('pin_j1', f)))
        return parts

    def extra_joints(self):
        super().extra_joints()
        for i, (a, b) in enumerate(self.attach):
            c("joint.as_built", type="rigid", a=a, b=b, name=f"fix_{b.split(':')[0]}")


VARIANTS = {'a': Pivot, 'b': Twin, 'c': Tip, 'h': Thumb, 'p': PrintedPins}

if __name__ == '__main__':
    g.check_reference()
    for key in (sys.argv[1:] or ['a', 'b', 'c', 'h', 'p']):
        v = VARIANTS[key]()
        cmds = g.build(v)
        g.write(v, cmds)
        extra = f", nose inset {v.inset} mm" if key == 'c' else ""
        print(f"v3{key}: {v.out} {len(cmds)} steps{extra}")
