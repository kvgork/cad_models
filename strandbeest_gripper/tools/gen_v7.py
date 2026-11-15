"""Generate v7_sandwich/cad/GRIP-9014_assy-sandwich.json: v6 with every fixed axis held top AND bottom.

v6 (GRIP-9012) let its axes bend: every fixed axle stood up from the base only, the crank gears
carried an 18 mm J1 hub, and the G posts were 24 mm tall. v7 sandwiches the mechanism between the
base frame and two top plates on pillars (user request 2026-11-15).

Why not one straight axle per joint: the K link sweeps right over the G pivot and the J and K links
sweep over the crank centre O, so no column can run from base to top plate there. Instead:
  - crank  = gear on the base (as before) + a crank ARM on top that turns in the top plate; the J1 pin
             is pressed into both, so J1 (and the links J and K on it) is held at both ends;
  - G      = two short fixed pivots on one axis: b-d-e on a post from the base, C on a stub that hangs
             from the top plate; K runs between them;
  - the links get a new layer order (layers.py with those rules): 6 link layers + the arm layer,
    instead of v6's 7 link layers, and the gear layer drops onto the base (no wheel rim under it);
  - thumb wheel: gear in the gear layer, its hub runs up through the top plate to a knob on top;
  - top plates: two identical plates (finger 2's is finger 1's turned 180 deg), each on 4 pillars
    outside every swept area; the jaws pass beside them.

gen_dual's layer globals are patched below for v7 only (layer order, gear height, zb/zt). Run v7 in
its own process: importing this module changes gen_dual for everything else in that process.

    python3 strandbeest_gripper/tools/gen_v7.py           (from the repo root)
    tools/build.sh strandbeest_gripper/v7_sandwich
    python3 strandbeest_gripper/tools/verify_v3.py 7
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_dual as g  # noqa: E402
import gen_v3 as v3  # noqa: E402
import layers  # noqa: E402
from gen_dual import c, cyl, new_component, occ, J, JL, W, fx  # noqa: E402

# ---------------------------------------------------------------------------- v7 layer plan (patches gen_dual)
OWN = {k: list(v) for k, v in layers.PINS.items()}       # real owners of each joint (G: b-d-e AND c)
V7_LAYER = {'crank': 0, 'bde': 1, 'f': 2, 'j': 2, 'k': 4, 'ghi': 5, 'c': 6}   # layers7 search: K between b-d-e and c
ARM_L = 7                                                  # crank arm layer, above every link
LOW_GAP = 2.5                                              # gear top -> first link: room for snap barbs (1.7) over the gears
TP_T = 4.0                                                 # top plate thickness

g.HORN_TOP = 5.0                                           # gears sit on 0.5 mm bosses on the 4 mm base plate
g.LAYER.clear()
g.LAYER.update(V7_LAYER)
g.NL = 7
layers.PINS['G'] = ['bde']                                 # G column from the base ends at b-d-e (no hub up to c)


def zb(layer):
    if layer == 0:
        return g.HORN_TOP
    return g.HORN_TOP + g.GEAR_T + LOW_GAP + (layer - 1) * (g.LINK_T + g.GAP)


def zt(layer):
    return zb(layer) + (g.GEAR_T if layer == 0 else g.LINK_T)


g.zb, g.zt = zb, zt
g.STACK_TOP = zt(6)
v3.TOP = g.STACK_TOP
v3.JAW_Z0 = zb(ARM_L)                                      # jaws beside the top plates, level with the arms
TP0 = zt(ARM_L) + g.GAP                                    # top plate underside
TP1 = TP0 + TP_T
HUB_D, KEY_AF, KEY_H = 10.0, 7.0, 6.0                      # wheel hub through the top plate, hex key for the knob
KNOB_H = 8.0
KNOB_Z0 = TP1 + g.GAP
KNOB_TOP = KNOB_Z0 + KNOB_H
PILLAR_D = 12.0
# link frame, finger 1; finger 2 = mirrored (= turned 180 deg: the set is symmetric about x = XM = 12)
PILLARS = [(-56.0, -8.0), (-34.0, 26.0), (58.0, 26.0), (80.0, -8.0)]
NOTCH = (-200.0, -18.0, -15.5, 2 * g.YM + 15.5)            # x0, x1, y0, y1: no base under the free jaw length

# snap pins: shank (head top -> barb shoulder) -> (key, part number); computed lengths are asserted against this
PIN_TABLE = {6.0: 'pin7_crank', 6.5: 'pin7_x', 6.7: 'pin7_j23', 7.7: 'pin7_gear_arm', 10.2: 'pin7_j4', 11.2: 'pin7_gtop',
             13.7: 'pin7_j5_gbot', 15.2: 'pin7_jaw', 39.2: 'pin7_pillar', 47.7: 'pin7_wheel'}
PIN_PN = {'pin7_crank': 'GRIP-0088', 'pin7_x': 'GRIP-0089', 'pin7_j23': 'GRIP-0090', 'pin7_gear_arm': 'GRIP-0091',
          'pin7_j4': 'GRIP-0092', 'pin7_gtop': 'GRIP-0093', 'pin7_j5_gbot': 'GRIP-0094', 'pin7_jaw': 'GRIP-0095',
          'pin7_pillar': 'GRIP-0096', 'pin7_wheel': 'GRIP-0097'}


def lmir(p, f):
    return p if f == 1 else g.mir(p)


def hex_pts(ctr, af, ang0=0.0):
    r = af / math.sqrt(3)
    return [[fx(ctr[0] + r * math.cos(math.radians(ang0 + 60 * k))), fx(ctr[1] + r * math.sin(math.radians(ang0 + 60 * k)))]
            for k in range(6)]


class V7(v3.V6):
    """v6 sandwiched: base frame + 2 top plates on pillars; crank arms on top; split G pivots."""
    assy_pn = "GRIP-9014"
    assy_desc = "ASSY, GRIPPER, SANDWICH FRAME, MIRRORED TWIN LEGS, STRANDBEEST V7"
    vdir = 'strandbeest_gripper/v7_sandwich'
    FRAME_TEXT = "V7"
    pn = {**v3.V6.pn, 'frame': 'GRIP-0070', 'topplate': 'GRIP-0071', 'arm': 'GRIP-0072', 'knob': 'GRIP-0073',
          'wheel': 'GRIP-0074', 'pin_j1': 'GRIP-0075', 'crank1': 'GRIP-0076', 'crank2': 'GRIP-0077',
          ('crankB', 1): 'GRIP-0078', ('crankB', 2): 'GRIP-0079', 'j': 'GRIP-0080', 'k': 'GRIP-0081',
          'c': 'GRIP-0082', 'f': 'GRIP-0083', ('bde', 1): 'GRIP-0084', ('bde', 2): 'GRIP-0085',
          ('ghi', 1): 'GRIP-0086', ('ghi', 2): 'GRIP-0087', **PIN_PN}
    revs = {'GRIP-0014': 'X2'}                     # Z33 idler: v5's labelled revision, unchanged
    SHANK = {k: s for s, k in PIN_TABLE.items()}

    def __init__(self):
        super().__init__()
        self.desc = {k: g.parts.register()[p]['Description'] for k, p in self.pn.items()
                     if isinstance(p, str) and p in g.parts.register()}
        self.WL2 = (2 * self.XM - self.WL[0], self.WL[1])     # twin bearing hole: keeps the top plate symmetric

    def params(self):
        return super().params() + [
            ("pillar_d", f"{PILLAR_D} mm", "frame pillar under the top plates, outside every swept area"),
            ("top_t", f"{TP_T} mm", "top plate: holds the crank arms, the C links at G and the wheel hub"),
            ("hub_d", f"{HUB_D} mm", "thumb-wheel hub, turns in the top plate"),
            ("hub_bore", "hub_d + 2 * 0.2 mm", "top-plate bearing for the wheel hub (0.2 mm per side)"),
            ("key_af", f"{KEY_AF} mm", "hex key on the hub top, drives the knob"),
            ("key_socket", "key_af + 0.3 mm", "hex socket in the knob (0.15 mm per side)"),
        ]

    # ------------------------------------------------------------------ frame: bosses, pillars, notch
    def frame_discs(self):
        d = super().frame_discs()
        for f in (1, 2):
            d += [(lmir(p, f), PILLAR_D / 2 + 1) for p in PILLARS]
        return d

    def frame_extra(self, fb):
        super().frame_extra(fb)
        z0, z1 = self.plate_z
        cyl(7, z1 - 0.01, g.HORN_TOP - g.GAP - z1 + 0.01, self.Wc, "join", fb, "boss_wheel")
        x0, x1, y0, y1 = NOTCH
        lab = self._link(self.frame_label[0])
        assert not (x0 <= lab[0] <= x1 and y1 <= lab[1] <= y0), ('frame label in the notch', lab)
        c("sketch.create", plane="XY", offset=f"{z0 - 0.5} mm", name="jaw_notch_sk")
        c("sketch.line", points=[list(W(p)) for p in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))], closed=True)
        c("sketch.finish")
        c("solid.extrude", distance=f"{z1 - z0 + 1} mm", operation="cut", targets=[fb], name="jaw_notch")
        for f in (1, 2):
            for i, p in enumerate(PILLARS):
                q = W(lmir(p, f))
                cyl("pillar_d", z1 - 0.01, TP0 - z1 + 0.01, q, "join", fb, f"pillar{f}_{i}")
                cyl("pin_d", z0 - 0.5, TP0 - z0 + 1, q, "cut", fb, f"pillar{f}_{i}_bore")
                cyl("head_d", z0 - 0.5, 3.5, q, "cut", fb, f"pillar{f}_{i}_cbore")

    @staticmethod
    def _link(p):
        nx, ny = math.cos(g.ROT), math.sin(g.ROT)
        return ((p[0] - g.A[0]) * nx + (p[1] - g.A[1]) * ny, -(p[0] - g.A[0]) * ny + (p[1] - g.A[1]) * nx)

    # ------------------------------------------------------------------ new parts
    def top_plate(self, f):
        name = g.comp_name('topplate', f)
        new_component(name)
        disc = [(p, 7) for p in PILLARS] + [(JL[1]['O'], 9), (self.JBL[1]['O'], 9), (JL[1]['G'], 8),
                                            (self.JBL[1]['G'], 8), (self.WL, 9), (self.WL2, 9)]
        cloud = [(p[0] + r * math.cos(a * math.pi / 18), p[1] + r * math.sin(a * math.pi / 18)) for p, r in disc for a in range(36)]
        outline = [list(W(lmir(p, f))) for p in g.hull(cloud)]
        c("sketch.create", plane="XY", offset=f"{fx(TP0)} mm", name=f"{name}_sk")
        c("sketch.line", points=outline, closed=True)
        c("sketch.finish")
        c("solid.extrude", distance="top_t", operation="new", body_name=name, name=name)
        Jf, JBf = J[f], self.JB[f]
        for tag, Gp in (('A', Jf['G']), ('B', JBf['G'])):          # stub down to the C link at G
            top_c = zt(V7_LAYER['c']) + g.GAP
            cyl(g.BAR_W, top_c, TP0 - top_c + 0.01, Gp, "join", name, f"{name}_stubG{tag}")
            cyl("pin_d", top_c - 0.5, TP1 - top_c + 1, Gp, "cut", name, f"{name}_boreG{tag}")
        for tag, Op in (('A', Jf['O']), ('B', JBf['O'])):
            cyl("pin_d", TP0 - 0.5, TP_T + 1, Op, "cut", name, f"{name}_boreO{tag}")
        for i, p in enumerate(PILLARS):
            cyl("pin_d", TP0 - 0.5, TP_T + 1, W(lmir(p, f)), "cut", name, f"{name}_boreP{i}")
        for i, p in enumerate((self.WL, self.WL2)):
            cyl("hub_bore", TP0 - 0.5, TP_T + 1, W(lmir(p, f)), "cut", name, f"{name}_hub{i}")
        # label between the cranks, turned 180 deg on finger 2 (same part, turned)
        ang = math.degrees(math.atan2(-self.UW[1], -self.UW[0])) + (0.0 if f == 1 else 180.0)
        v3.deboss(name, name, "TOP", W(lmir((self.XM, 15.0), f)), ang, 5.0, TP1, f"label_{name}", raw=True)
        c("component.activate", component=0)
        self.attach.append((occ('frame', 1), g.occ('topplate', f)))
        return [('topplate', f)]

    def arm(self, i, Jf, crank_occ):
        """Crank arm on top of the stack: turns on a snap pin in the top plate at O, J1 pin pressed in."""
        name = g.comp_name('arm', i)
        new_component(name)
        z0 = zb(ARM_L)
        g.slot(f"{name}_bar", Jf['O'], Jf['J1'], z0, name, "new")
        hub0 = zt(V7_LAYER['k']) + g.GAP
        cyl(g.BAR_W, hub0, z0 - hub0 + 0.01, Jf['J1'], "join", name, f"{name}_hubJ1")
        cyl("pin_d", z0 - 0.5, g.LINK_T + 1, Jf['O'], "cut", name, f"{name}_boreO")
        cyl("shoulder_d", hub0 - 0.5, z0 - hub0 + 0.5, Jf['J1'], "cut", name, f"{name}_shoulder")
        cyl("tap_d", z0 - 0.01, g.LINK_T + 0.51, Jf['J1'], "cut", name, f"{name}_tapJ1")
        self.attach.append((crank_occ, g.occ('arm', i)))
        return [('arm', i)]

    def wheel_part(self):
        name = g.comp_name('wheel', 1)
        new_component(name)
        c("sketch.create", plane="XY", offset=f"{fx(g.HORN_TOP)} mm", name="wheel_gear_sk")
        c("sketch.line", points=g.gear_points(self.WL, v3.ZW, self.phase), closed=True)
        c("sketch.finish")
        c("solid.extrude", distance=f"{g.IDLE_T} mm", operation="new", body_name=name, name="wheel_gear")
        top = g.HORN_TOP + g.IDLE_T
        cyl("hub_d", top - 0.01, KNOB_Z0 - top + 0.01, self.Wc, "join", name, "wheel_hub")
        c("sketch.create", plane="XY", offset=f"{fx(KNOB_Z0 - 0.01)} mm", name="wheel_key_sk")
        c("sketch.line", points=hex_pts(self.Wc, KEY_AF), closed=True)
        c("sketch.finish")
        c("solid.extrude", distance=f"{KEY_H + 0.01} mm", operation="join", targets=[name], name="wheel_key")
        cyl("pin_d", g.HORN_TOP - 0.5, KNOB_Z0 + KEY_H - g.HORN_TOP + 1, self.Wc, "cut", name, "wheel_bore")
        kn = g.comp_name('knob', 1)
        new_component(kn)
        pts = []
        for k in range(2 * v3.RIM_KNURLS):
            r = v3.RIM_R if k % 2 == 0 else v3.RIM_R - 0.8
            a = math.pi * k / v3.RIM_KNURLS
            pts.append(list(W((self.WL[0] + r * math.cos(a), self.WL[1] + r * math.sin(a)))))
        c("sketch.create", plane="XY", offset=f"{fx(KNOB_Z0)} mm", name="knob_sk")
        c("sketch.line", points=pts, closed=True)
        c("sketch.finish")
        c("solid.extrude", distance=f"{KNOB_H} mm", operation="new", body_name=kn, name="knob_rim")
        c("sketch.create", plane="XY", offset=f"{fx(KNOB_Z0 - 0.5)} mm", name="knob_socket_sk")
        c("sketch.line", points=hex_pts(self.Wc, KEY_AF + 0.3), closed=True)
        c("sketch.finish")
        c("solid.extrude", distance=f"{KEY_H + 1.0} mm", operation="cut", targets=[kn], name="knob_socket")
        cyl("pin_d", KNOB_Z0 - 0.5, KNOB_H + 1, self.Wc, "cut", kn, "knob_bore")
        self.attach.append((occ('wheel', 1), g.occ('knob', 1)))
        return [('wheel', 1), ('knob', 1)]

    def j1_pins(self, spots):
        """J1: pressed into the crank gear (bottom) and the crank arm (top); shoulder between; 2 flats."""
        parts = []
        for i, p, crank in spots:
            name = g.comp_name('pin_j1', i)
            new_component(name)
            gear_top = g.HORN_TOP + g.GEAR_T
            z_arm = zb(ARM_L)
            g.c("solid.cylinder", diameter="j1_tip_d", height=f"{fx(gear_top - g.HORN_TOP - 0.5 + 0.01)} mm",
                base=[fx(p[0]), fx(p[1]), fx(g.HORN_TOP + 0.5)], operation="new", body_name=name, name=f"{name}_tip")
            cyl("j1_shoulder", gear_top, z_arm - gear_top + 0.01, p, "join", name, f"{name}_shoulder")
            cyl("j1_tip_d", z_arm - 0.01, 2.51, p, "join", name, f"{name}_tip_top")
            self.two_flats(name, p, (4.2 - 2 * self.CLEAR) / 2, g.HORN_TOP + 0.5, z_arm + 2.5)
            parts.append(('pin_j1', i))
            self.attach.append((crank, g.occ('pin_j1', i)))
        return parts

    def two_flats(self, name, p, r, zl, zh):
        """User rule 2026-11-15: two parallel flats (+-y), FLAT deep: print lying on one."""
        off = r - self.FLAT
        for s_, tag in ((-1, 'flat'), (1, 'flat2')):
            c("solid.box", length="10 mm", width="5 mm", height=f"{fx(zh - zl + 2)} mm",
              center=[fx(p[0]), fx(p[1] + s_ * (off + 2.5)), fx((zl + zh) / 2)],
              operation="cut", targets=[name], name=f"{name}_{tag}")

    def snap_pins(self, locs, count):
        """v4b snap pins (split barbed tip), with the second flat of the 2026-11-15 rule."""
        parts = []
        for loc in locs:
            key, p, z_seat, z_cap, att = loc[:5]
            down = len(loc) > 5 and loc[5]
            s_ = -1 if down else 1
            z_sh = z_cap + s_ * self.BARB_UP
            assert abs(s_ * (z_sh - z_seat) - self.SHANK[key]) < 1e-6, (key, z_sh - z_seat)
            count[key] = count.get(key, 0) + 1
            name = g.comp_name(key, count[key])
            new_component(name)
            z0 = z_seat - self.HEAD_H if not down else z_seat + self.HEAD_H
            top = z_sh + s_ * self.BARB_H
            g.c("solid.cylinder", diameter="ppin_head_d", height=f"{fx(self.HEAD_H)} mm",
                base=[fx(p[0]), fx(p[1]), fx(min(z0, z_seat))], operation="new", body_name=name, name=f"{name}_head")
            lo_, hi_ = sorted((z_seat - s_ * 0.01, z_sh + s_ * self.SHANK_OVER))
            cyl("ppin_d", lo_, hi_ - lo_, p, "join", name, f"{name}_shank")
            if not down:
                c("solid.cone", diameter="barb_d", top_diameter="barb_tip_d", height=f"{fx(self.BARB_H)} mm",
                  base=[fx(p[0]), fx(p[1]), fx(z_sh)], operation="join", targets=[name], name=f"{name}_barb")
            else:
                c("solid.cone", diameter="barb_tip_d", top_diameter="barb_d", height=f"{fx(self.BARB_H)} mm",
                  base=[fx(p[0]), fx(p[1]), fx(top)], operation="join", targets=[name], name=f"{name}_barb")
            zl, zh = sorted((z0, top))
            self.two_flats(name, p, self.PIN_R, zl, zh)
            slot_len = self.BARB_H + self.BARB_UP + self.SLOT_DOWN
            c("solid.box", length="snap_slot", width="10 mm", height=f"{fx(slot_len + 1)} mm",
              center=[fx(p[0]), fx(p[1]), fx(top - s_ * (slot_len / 2 - 0.5))],
              operation="cut", targets=[name], name=f"{name}_slot")
            parts.append((key, count[key]))
            self.attach.append((att, g.occ(key, count[key])))
        return parts

    def locations(self):
        L = V7_LAYER
        seat = self.plate_z[0] - 0.5 + 3.5
        frame = occ('frame', 1)
        raw = []
        for f in (1, 2):
            tp = g.occ('topplate', f)
            for leg in ('A', 'B'):
                Jf = J[f] if leg == 'A' else self.JB[f]
                ob = (lambda k, f=f: occ(k, f)) if leg == 'A' else (lambda k, f=f: f"{self.legB_name(k, f)}:1")
                raw += [(Jf['O'], seat, g.HORN_TOP + g.GEAR_T - 2.2, frame, False),          # crank axle (barb in the recess)
                        (Jf['G'], seat, zt(L['bde']), frame, False),                          # G, lower pivot: b-d-e
                        (Jf['G'], TP1, zb(L['c']), tp, True),                                 # G, upper pivot: C
                        (Jf['O'], TP1, zb(ARM_L), tp, True),                                  # crank arm in the top plate
                        (Jf['F'], zb(L['ghi']), v3.JAW_Z0 + v3.JAW_H, ob('ghi'), False)]      # jaw (hole / slot)
                for n in ('J2', 'J3', 'J4', 'J5'):
                    own = OWN[n]
                    lo = min(own, key=lambda o: L[o])
                    hi = max(own, key=lambda o: L[o])
                    if L[lo] == 1:      # head would hang into the gear layer: head on top, barb under layer 1
                        raw.append((Jf[n], zt(L[hi]), zb(L[lo]), ob(lo), True))
                    else:
                        raw.append((Jf[n], zb(L[lo]), zt(L[hi]), ob(lo), False))
            raw += [(J[f]['I'], seat, g.HORN_TOP + g.IDLE_T, frame, False),
                    (self.X[f], seat, g.HORN_TOP + self.IDLER_X_T, frame, False)]
            raw += [(W(lmir(p, f)), seat, TP1, frame, False) for p in PILLARS]
        raw.append((self.Wc, seat, KNOB_TOP, frame, False))
        out = []
        for p, z_seat, z_cap, att, down in raw:
            sh = round(abs(z_cap + (-1 if down else 1) * self.BARB_UP - z_seat), 4)
            assert sh in PIN_TABLE, ('no pin part for shank', sh)
            out.append((PIN_TABLE[sh], p, z_seat, z_cap, att, down))
        return out

    def extra_parts(self):
        self.attach = []
        parts = []
        for f in (1, 2):
            name = g.comp_name('crankB', f)
            new_component(name)
            g.crank_gear(f, self.JB[f], name, self.JBL[f]['O'], self.ph[('B', f)], on_horn=False, tag=f"crankB{f}")
            name = g.comp_name('idlerX', f)
            new_component(name)
            g.gear_body(f"gear_idlerX{f}", self.XL[f], self.ZX, self.ph[('X', f)], name, thick=self.IDLER_X_T)
            cyl("pin_d", g.HORN_TOP - 0.5, g.GEAR_T + 1, self.X[f], "cut", name, f"idlerX{f}_bore")
            for key in g.LINK_KEYS:
                body = self.legB_name(key, f)
                new_component(body)
                z0 = zb(V7_LAYER[key])
                g.build_link(key, f, self.JB[f], z0, body, self, mark=None, tag=f"{key}{f}B")
                if key == 'ghi':
                    v3.ghi_hub(f, body, z0, self.JB[f], f"ghi{f}B")
                pnb = self.legB_pn(key, f)
                c("component.metadata.set", component=body, part_number=pnb, description=g.parts.register()[pnb]['Description'],
                  revision=g.rev_of(self, pnb), bom_type="normal")
            name = g.comp_name('jawt', f)
            new_component(name)
            self.long_jaw(name, f)
            parts += [('crankB', f), ('idlerX', f), ('jawt', f)]
        cranks = [(J[1], occ('crank1', 1)), (J[2], occ('crank2', 1)),
                  (self.JB[1], occ('crankB', 1)), (self.JB[2], occ('crankB', 2))]
        for i, (Jf, co) in enumerate(cranks, 1):
            parts += self.arm(i, Jf, co)
        for f in (1, 2):
            parts += self.top_plate(f)
        parts += self.wheel_part()
        parts += self.snap_pins(self.locations(), {})
        parts += self.j1_pins([(i, Jf['J1'], co) for i, (Jf, co) in enumerate(cranks, 1)])
        self.labels()
        return parts


VARIANTS = {'7': V7}

if __name__ == '__main__':
    g.check_reference()
    v = V7()
    cmds = g.build(v)
    g.write(v, cmds)
    print(f"v7: {v.out} {len(cmds)} steps; link layers {V7_LAYER}, arm z {zb(ARM_L)}..{zt(ARM_L)}, "
          f"top plate z {TP0}..{TP1}, knob top {KNOB_TOP}, jaw z {v3.JAW_Z0}..{v3.JAW_Z0 + v3.JAW_H}")
