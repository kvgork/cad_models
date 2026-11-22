"""Generate storage_drawers: a stackable shelf with a slide-out Gridfinity drawer.

    python3 storage_drawers/tools/gen_storage.py [assy|check] [out.json] [--ver v1|v2]   (default v1)

  v1     storage_drawers/v1_gridfinity (STOR-9001, drawer STOR-0002)
  v2     storage_drawers/v2_loose-fit (STOR-9002, drawer STOR-0005): the same shelf, spacer and bin; a narrower
         drawer with more slide clearance and a hook handle (v1 drawers got stuck, the handle had too little grip)
  assy   <version>/cad/<ASSY>.json (committed): shelf, spacer, shelf
         stacked; the drawer closed in the bottom shelf; a test bin in one grid cell. Exports every part.
  check  the same stack plus check-only bodies (a Manta case dummy in the drawer), no exports; the verify script
         builds it in a scratch folder.

Frame: X = width, Y = depth (+Y = to the back, shelf front face at y = 0), Z = up. The bottom shelf's wall
bottoms are at z = 0. Each shelf (STOR-0001) is a top (the drawer's lid) on two side walls and a back wall, no
floor. The next shelf's walls stand on a 3 mm rim on top of the walls below; their 3 mm skirt reaches down over
the outside of that rim (pitch P = ZL + RIM_H). The drawer (STOR-0002) hangs by two top flanges on 45 deg rails
just under the lid, so it does not touch the shelf below, its walls end 0.4 mm under the lid (nothing falls in or
out over them), and a drawer of any height uses the same rails: a spacer frame (STOR-0003, walls + rim + skirt,
no top) under a shelf makes room for a taller drawer.
Closing: the front panel stops on the shelf front; a bump on a cantilever arm in each drawer side wall clicks
into a pocket in a pad on the shelf wall (detent).
Floor: Gridfinity 5 x 4 (42 mm pitch) baseplate profile; bins (STOR-0004 test bin) drop in.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import parts  # noqa: E402


# ----------------------------------------------------------------------------- design numbers (mm)
MANTA = (216.0, 178.0, 38.0)    # iFixit Manta Driver Kit case (iFixit product page, 2026-11-18)
GF = 42.0                       # Gridfinity pitch
GF_NX, GF_NY = 5, 4
GF_H = 4.65                     # baseplate profile height: 0.7 @45 + 1.8 + 2.15 @45
GF_STEPS = (2.15, 1.8, 0.7)     # from the cell floor up
GF_R_TOP = 4.0                  # cell corner radius at the top (42 x 42)
BIN_W, BIN_R = 41.5, 3.75       # bin base outline at its widest, corner radius
BIN_STEPS = (0.8, 1.8, 2.15)    # bin foot from its bottom up (4.75)
BIN_U = 3                       # test bin height units (7 mm)
BIN_WALL = 1.2

T_DW = 2.0                      # drawer walls
T_DF = 1.6                      # drawer floor under the grid slab
YD = MANTA[1] + 2 * 1.5 + 2 * T_DW   # 185: drawer body depth (front wall at y 0..2), case 1.5 clear front/back
FL_LAND = 1.5                   # flat land under the flange tip (rests on the rail); then 45 deg back to the wall
T_SW = 3.0                      # shelf side and back walls
# The shelf never changes (user 2026-11-18): its numbers are frozen at the v1 drawer they were drawn around.
XD_V1, FL_W_V1, FL_EDGE_V1 = 111.5, 3.0, 1.0
XW = XD_V1 + FL_W_V1 + 0.5 + T_SW   # 118: shelf outer half width
XWI = XW - T_SW                 # 115: shelf side wall inner face
Y_BACK_IN = YD + 1.0            # 186: shelf back wall inner face
YS = Y_BACK_IN + T_SW           # 189: shelf depth
T_LID = 2.4
LID_GAP = 0.5                   # v1 drawer wall / flange top to the lid underside as built (+ RAIL_DROP seated = 0.6)
RIM_H = 3.0                     # rim on the walls' top; the next shelf's skirt reaches over it
SKIRT_T = 1.4                   # skirt = outer part of the wall continued down
SKIRT_CLR = 0.2                 # skirt to rim, per side
DRAWER_DROP = 1.0               # drawer bottom above the lid of the shelf below (0.8 above a table: skirt 0.2 shorter)
GRID_CLR_H = 42.5               # minimum clear height above the grid (Manta 38, a 6u bin 37.4 + lip 4.4)

ZB = -RIM_H + DRAWER_DROP                       # -2.5: drawer bottom
ZG = ZB + T_DF + GF_H                           # 3.75: grid top
ZL = math.ceil(ZG + GRID_CLR_H + LID_GAP + T_LID)  # 50: lid top (shelf height without rim)
ZLU = ZL - T_LID                                # 47.6: lid underside
ZL_V1 = ZL
P = ZL + RIM_H                                  # 53: stack pitch
RAIL_DROP = 0.1                                 # rail top below the flange land as built (drawer seated: 0)
RAIL_Z = ZLU - LID_GAP - FL_EDGE_V1 - RAIL_DROP   # 46.0: shelf rail top
RAIL_X = XD_V1 + FL_W_V1 - FL_LAND + 0.2        # 113.2: rail inner edge (v1: 0.2 to the flange gusset)
FRONT_T = 3.0                                   # drawer front panel (overlay, stops on the shelf front)
FRONT_GAP = 0.5                                 # panel edge to the shelf outline / to the next panel

# detent: arm in the drawer side wall (U-slot), bump outward, pocket in a pad on the shelf wall
# the arm stands upright (root at the bottom, free tip at the top): it grows straight up when the drawer prints on
# its floor; a horizontal arm left its underside over the slot (Bambu "floating cantilever")
ARM = dict(y0=11.0, y1=21.0, z0=6.0, z1=26.0, slot=0.8)    # L 20 (z), width 10 (y), t 2 (wall)
PAD_X = XD_V1 + 0.5                                         # 112.0: pad face (shelf); bump interference 0.6
OPEN_STOP = 130.0                                           # rear arm: its bump clicks into the same pocket here
SNAP = dict(len=30.0, h=0.5, groove=0.7)                    # stack snap: ridge on the rim side, groove in the skirt
POCKET_D = 0.8                                              # pocket depth (bump peak 0.2 clear)



VERSIONS = {
    'v1': dict(vdir='storage_drawers/v1_gridfinity', assy='STOR-9001', drawer='STOR-0002',
               manta_clr=1.5, fl_w=3.0, fl_edge=1.0, bump_h=1.1, manta_check=1.0,
               handle=dict(w=80.0, out=12.0, lip=3.0, up=0.0, top=ZL_V1 - 12.0)),
    # v2 (user 2026-11-19: "the drawers get stuck and the handle has not enough grip"): every sliding gap to the
    # (unchanged) shelf grows: body to detent pad 0.5 -> 1.0, flange tip to wall 0.5 -> 0.7, rail edge to the
    # flange gusset 0.2 -> 0.4, flange top to lid 0.6 -> 0.8 seated. The Manta case keeps 1.0 per side (was 1.5).
    # Handle: a trough with an upward lip at the tip: the fingers hook over the lip and pull on its inner face.
    'v2': dict(vdir='storage_drawers/v2_loose-fit', assy='STOR-9002', drawer='STOR-0005',
               manta_clr=1.0, fl_w=3.3, fl_edge=0.8, bump_h=1.6, manta_check=0.75,
               handle=dict(w=100.0, out=20.0, lip=3.0, up=10.0, top=ZL_V1 - 1.5)),
}

def configure(ver):
    """Set the drawer numbers (and folder, part numbers) of one version; the shelf numbers above stay."""
    global VER, VDIR, ASSY, PN, MANTA_CLR, MANTA_CHECK, DRAWER_IN, XD, FL_W, FL_EDGE, ZDT, BUMP, HANDLE
    v = VERSIONS[ver]
    VER, VDIR = ver, v['vdir']
    ASSY = (v['assy'], parts.register()[v['assy']]['Description'])
    PN = {'shelf': 'STOR-0001', 'drawer': v['drawer'], 'spacer': 'STOR-0003', 'bin': 'STOR-0004'}
    MANTA_CLR = v['manta_clr']                          # case to drawer side wall
    MANTA_CHECK = (v['manta_check'], 1.5)               # verify: the case fits with this margin (sides, top)
    DRAWER_IN = (MANTA[0] + 2 * MANTA_CLR, YD - 2 * T_DW)   # v1 219 x 181, v2 218 x 181
    XD = DRAWER_IN[0] / 2 + T_DW                        # drawer side wall outer face: v1 111.5, v2 111.0
    FL_W, FL_EDGE = v['fl_w'], v['fl_edge']             # flange out from the wall; its outer vertical edge
    ZDT = RAIL_Z + RAIL_DROP + FL_EDGE                  # drawer wall + flange top as built: v1 47.1, v2 46.9
    # bump peak at PAD_X + 0.6 whatever the wall: the same click in the same shelf pocket
    BUMP = dict(y=16.0, h=PAD_X + 0.6 - XD, z0=19.5, z1=24.5)
    HANDLE = dict(v['handle'])


PARTS = []        # (component, PN)
CHECK = []        # check-only bodies
cmds = []


def c(command, **params):
    cmds.append({"command": command, "params": params})


def fx(v):
    return round(v, 4)


def mm(v):
    return f"{fx(v)} mm"


def comp(key, inst):
    return f"{parts.fname(PN[key])}_{inst}"


def new_component(name, grounded=False):
    c("component.activate", component=0)
    c("component.create", name=name, activate=True, grounded=grounded)


def target(p, op, body):
    p.update({"body_name": body} if op == "new" else {"targets": [body]})
    return p


def box(x, y, z, op, body, name):
    c("solid.box", **target(dict(length=mm(x[1] - x[0]), width=mm(y[1] - y[0]), height=mm(z[1] - z[0]),
                                 center=[fx((x[0] + x[1]) / 2), fx((y[0] + y[1]) / 2), fx((z[0] + z[1]) / 2)],
                                 operation=op, name=name), op, body))


def prism_xy(pts, z0, h, op, body, name):
    c("sketch.create", plane="XY", offset=mm(z0), name=f"{name}_sk")
    c("sketch.line", points=[[fx(x), fx(y)] for x, y in pts], closed=True)
    c("sketch.finish")
    c("solid.extrude", **target(dict(distance=mm(h), operation=op, name=name), op, body))


def prism_yz(pts, x0, length, op, body, name):
    """Profile in (y, z), extruded along +X from x0."""
    c("sketch.create", plane="YZ", offset=mm(x0), name=f"{name}_sk")
    c("sketch.line", points=[[fx(y), fx(z)] for y, z in pts], closed=True)
    c("sketch.finish")
    c("solid.extrude", **target(dict(distance=mm(length), operation=op, name=name), op, body))


def prism_xz(pts, y0, length, op, body, name):
    """Profile in (x, z), extruded along +Y from y0 (XZ sketch: x = +X, sketch y = -Z, normal +Y)."""
    c("sketch.create", plane="XZ", offset=mm(y0), name=f"{name}_sk")
    c("sketch.line", points=[[fx(x), fx(-z)] for x, z in pts], closed=True)
    c("sketch.finish")
    c("solid.extrude", **target(dict(distance=mm(length), operation=op, name=name), op, body))


def rrect(cx, cy, w, r, z0, h, taper, op, body, name):
    """Rounded square (side w, corner r) at z0, extruded h up; taper deg (+ = grows upward)."""
    c("sketch.create", plane="XY", offset=mm(z0), name=f"{name}_sk")
    c("sketch.rectangle.rounded", p0=[fx(cx - w / 2), fx(cy - w / 2)], p1=[fx(cx + w / 2), fx(cy + w / 2)],
      radius=mm(r))
    c("sketch.finish")
    p = dict(distance=mm(h), operation=op, name=name)
    if taper:
        p.update(taper=f"{taper} deg", corner="round")
    c("solid.extrude", **target(p, op, body))


def mirror_x(pts):
    return [(-x, y) for x, y in reversed(pts)]


# ----------------------------------------------------------------------------- shelf / spacer
def walls(body, lid):
    """Side walls + back wall + rim + skirt (+ lid). Shared by the shelf and the spacer."""
    box((-XW, XW), (Y_BACK_IN, YS), (0, ZL), 'new', body, f"{body}_back")
    for s in (-1, 1):
        xo, xi = s * XW, s * XWI
        box(sorted((xi, xo)), (0, YS), (0, ZL), 'join', body, f"{body}_wall{s:+d}")
        # rim: inner part of the wall, RIM_H above its top (the next shelf's wall stands on it)
        xr = s * (XW - SKIRT_T - SKIRT_CLR)
        box(sorted((xi, xr)), (0, YS - SKIRT_T - SKIRT_CLR), (ZL - 0.3, ZL + RIM_H), 'join', body,
            f"{body}_rim{s:+d}")
        # skirt: outer part of the wall, down over the rim of the shelf below
        xs = s * (XW - SKIRT_T)
        box(sorted((xs, xo)), (0, YS), (-RIM_H + SKIRT_CLR, 0.3), 'join', body, f"{body}_skirt{s:+d}")
    box((-(XW - SKIRT_T - SKIRT_CLR), XW - SKIRT_T - SKIRT_CLR), (Y_BACK_IN, YS - SKIRT_T - SKIRT_CLR),
        (ZL - 0.3, ZL + RIM_H), 'join', body, f"{body}_rim_back")
    box((-XW, XW), (YS - SKIRT_T, YS), (-RIM_H + SKIRT_CLR, 0.3), 'join', body, f"{body}_skirt_back")
    if lid:
        box((-XW, XW), (0, YS), (ZLU, ZL), 'join', body, f"{body}_lid")
    # stack snap: a short ridge mid-way along each side rim, a groove in the skirt above it (side walls only)
    for s in (-1, 1):
        prism_xz(snap_pts(s, ridge=True), SNAP_Y - SNAP['len'] / 2, SNAP['len'], 'join', body, f"{body}_ridge{s:+d}")
        prism_xz(snap_pts(s, ridge=False), SNAP_Y - SNAP['len'] / 2 - 0.5, SNAP['len'] + 1.0, 'cut', body,
                 f"{body}_groove{s:+d}")


SNAP_Y = (YS - SKIRT_T - SKIRT_CLR) / 2       # ridge centre along the rim


def snap_pts(s, ridge):
    """(x, z) triangle: the ridge on the rim's outer face, or the groove in the skirt (one pitch lower)."""
    xr = XW - SKIRT_T - SKIRT_CLR               # rim outer face (116.4)
    zr = ZL + 1.2                               # ridge peak height
    if ridge:
        b, peak, zc = xr - 0.3, xr + SNAP['h'], zr
    else:
        b, peak, zc = xr + SKIRT_CLR - 0.3, xr + SNAP['h'] + SKIRT_CLR, zr - P
    hw = peak - b
    pts = [(b, zc - hw), (peak, zc), (b, zc + hw)]
    return [(s * x, z) for x, z in pts] if s > 0 else [(s * x, z) for x, z in reversed(pts)]


def rail_pts(s):
    """Rail under the drawer flange, (x, z) profile for side s: a flat top under the flange's land, kept
    RAIL_GAP clear of the flange's 45 deg gusset, 45 deg underneath (prints standing, any profile is fine)."""
    zr, x_in = RAIL_Z, RAIL_X                    # frozen (shelf)
    pts = [(XWI + 0.3, zr), (x_in, zr), (x_in, zr - 1.5), (XWI + 0.3, zr - 1.5 - (XWI + 0.3 - x_in))]
    return [(s * x, z) for x, z in pts] if s > 0 else [(s * x, z) for x, z in reversed(pts)]


def pad_pts(s):
    """Detent pad on the shelf wall, (x, y) profile: lead-in at the front, pocket at the bump, 45 deg back end."""
    yb = BUMP['y']
    pts = [(XWI + 0.3, 0.0), (PAD_X, XWI - PAD_X), (PAD_X, yb - POCKET_D), (PAD_X + POCKET_D, yb),
           (PAD_X, yb + POCKET_D), (PAD_X, ARM['y1'] + 2.0), (XWI + 0.3, ARM['y1'] + 2.0 + XWI + 0.3 - PAD_X)]
    return [(s * x, y) for x, y in pts] if s > 0 else [(s * x, y) for x, y in reversed(pts)]


def build_shelf(inst, z0):
    name = comp('shelf', inst)
    new_component(name, grounded=(z0 == 0))
    body = name
    walls(body, lid=True)
    for s in (-1, 1):
        prism_xz(rail_pts(s), 0.0, Y_BACK_IN + 0.3, 'join', body, f"{body}_rail{s:+d}")
        prism_xy(pad_pts(s), BUMP['z0'] - 3.0, BUMP['z1'] - BUMP['z0'] + 6.0, 'join', body, f"{body}_pad{s:+d}")
    PARTS.append((name, PN['shelf']))
    if z0:
        c("occurrence.move", occurrence=f"{name}:1", move_grounded=True,
          matrix=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, fx(z0)]])
    return name


def build_spacer(inst, z0):
    name = comp('spacer', inst)
    new_component(name)
    walls(name, lid=False)
    PARTS.append((name, PN['spacer']))
    c("occurrence.move", occurrence=f"{name}:1", move_grounded=True,
      matrix=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, fx(z0)]])
    return name


# ----------------------------------------------------------------------------- drawer
def grid_cells():
    xc0 = -(GF_NX - 1) * GF / 2
    yc0 = T_DW + DRAWER_IN[1] / 2 - (GF_NY - 1) * GF / 2
    return [(xc0 + i * GF, yc0 + j * GF) for j in range(GF_NY) for i in range(GF_NX)]


def cell_cut(body, cx, cy, z_floor, tag):
    """One Gridfinity baseplate pocket, cut from the cell floor up (45 / vertical / 45)."""
    w0 = GF - 2 * (GF_STEPS[0] + GF_STEPS[2])          # 36.3 at the floor
    r0 = GF_R_TOP - GF_STEPS[0] - GF_STEPS[2]          # 1.15
    w1, r1 = w0 + 2 * GF_STEPS[0], r0 + GF_STEPS[0]
    z1 = z_floor + GF_STEPS[0]                          # top of the lower 45 deg
    z2 = z1 + GF_STEPS[1]                               # top of the vertical band
    # cut from the top down so every cut opens onto the one above it
    rrect(cx, cy, w1, r1, z2, GF_STEPS[2] + 0.5, 45, 'cut', body, f"{tag}_c")   # runs 0.5 above the grid top
    rrect(cx, cy, w1, r1, z1, GF_STEPS[1] + 0.01, 0, 'cut', body, f"{tag}_b")
    rrect(cx, cy, w0, r0, z_floor, GF_STEPS[0] + 0.01, 45, 'cut', body, f"{tag}_a")


def build_drawer(inst):
    name = comp('drawer', inst)
    new_component(name)
    b = name
    xi = DRAWER_IN[0] / 2
    box((-XD, XD), (-0.3, YD), (ZB, ZDT), 'new', b, f"{b}_body")      # 0.3 into the front panel
    box((-xi, xi), (T_DW, YD - T_DW), (ZG, ZDT + 1.0), 'cut', b, f"{b}_cavity")
    # flanges: (x, z) profile, along the full body depth
    for s in (-1, 1):
        zf = ZDT - FL_EDGE
        xl = XD + FL_W - FL_LAND
        pts = [(XD - 0.3, ZDT), (XD + FL_W, ZDT), (XD + FL_W, zf), (xl, zf), (XD - 0.3, zf - (xl - XD) - 0.3)]
        pts = [(s * x, z) for x, z in pts] if s > 0 else [(s * x, z) for x, z in reversed(pts)]
        prism_xz(pts, 0.0, YD, 'join', b, f"{b}_flange{s:+d}")
    # front panel + handle
    xp = XW - FRONT_GAP
    box((-xp, xp), (-FRONT_T, 0.0), (ZB, ZL), 'join', b, f"{b}_front")
    h = HANDLE
    y0, yt = -FRONT_T + 0.3, -FRONT_T - h['out']
    if h['up']:
        # v2 hook handle: trough floor at z_floor, lip up at the tip (fingers hook over it and pull on its inner
        # face), 1 mm chamfer on the lip's inner top edge; 45 deg underside back to the panel (prints unsupported)
        zl = h['top']                           # lip top
        zf = zl - h['up']                       # trough floor
        yi = yt + h['lip']                      # lip inner face
        pts = [(y0, zf), (yi, zf), (yi, zl - 1.0), (yi - 1.0, zl), (yt, zl), (yt, zf - h['lip']),
               (y0, zf - h['lip'] - h['out'] - 0.3)]
    else:
        zt = h['top']
        pts = [(y0, zt), (yt, zt), (yt, zt - h['lip']), (y0, zt - h['lip'] - h['out'] - 0.3)]
    prism_yz(pts, -h['w'] / 2, h['w'], 'join', b, f"{b}_handle")
    # Gridfinity cells
    for k, (cx, cy) in enumerate(grid_cells()):
        cell_cut(b, cx, cy, ZB + T_DF, f"{b}_cell{k:02d}")
    # detent arms: upside-down U-slot through each side wall, bump on the arm's outer face near its free (top) end.
    # Front arm: clicks into the shelf pocket when closed. Rear arm (OPEN_STOP further back): clicks into the same
    # pocket at OPEN_STOP out, a soft open stop; pulling harder takes the drawer out (to load the Manta case).
    a, bp = ARM, BUMP
    for tag, dy in (('f', 0.0), ('r', OPEN_STOP)):
        for s in (-1, 1):
            xs = sorted((s * (xi - 0.3), s * (XD + 0.3)))
            y0, y1, sl = a['y0'] + dy, a['y1'] + dy, a['slot']
            box(xs, (y0 - sl, y1 + sl), (a['z1'], a['z1'] + sl), 'cut', b, f"{b}_slot_top_{tag}{s:+d}")
            box(xs, (y0 - sl, y0), (a['z0'], a['z1'] + sl), 'cut', b, f"{b}_slot_front_{tag}{s:+d}")
            box(xs, (y1, y1 + sl), (a['z0'], a['z1'] + sl), 'cut', b, f"{b}_slot_back_{tag}{s:+d}")
            yc = bp['y'] + dy
            pts = [(XD - 0.3, yc - bp['h'] - 0.3), (XD + bp['h'], yc), (XD - 0.3, yc + bp['h'] + 0.3)]
            pts = [(s * x, y) for x, y in pts] if s > 0 else [(s * x, y) for x, y in reversed(pts)]
            prism_xy(pts, bp['z0'], bp['z1'] - bp['z0'], 'join', b, f"{b}_bump_{tag}{s:+d}")
    PARTS.append((name, PN['drawer']))
    return name


# ----------------------------------------------------------------------------- bin
def build_bin(inst, cx, cy, z0):
    """Gridfinity 1x1 bin, plain, BIN_U units high (7 mm each, foot bottom to rim)."""
    name = comp('bin', inst)
    new_component(name)
    b = name
    w0 = BIN_W - 2 * (BIN_STEPS[0] + BIN_STEPS[2])     # 35.6
    r0 = BIN_R - BIN_STEPS[0] - BIN_STEPS[2]          # 0.8
    rrect(0, 0, w0, r0, 0, BIN_STEPS[0], 45, 'new', b, f"{b}_foot_a")
    w1, r1 = w0 + 2 * BIN_STEPS[0], r0 + BIN_STEPS[0]
    rrect(0, 0, w1, r1, BIN_STEPS[0] - 0.01, BIN_STEPS[1] + 0.02, 0, 'join', b, f"{b}_foot_b")
    rrect(0, 0, w1, r1, BIN_STEPS[0] + BIN_STEPS[1], BIN_STEPS[2], 45, 'join', b, f"{b}_foot_c")
    hf = sum(BIN_STEPS)
    rrect(0, 0, BIN_W, BIN_R, hf - 0.01, 7 * BIN_U - hf + 0.01, 0, 'join', b, f"{b}_wall")
    rrect(0, 0, BIN_W - 2 * BIN_WALL, BIN_R - BIN_WALL, hf + 1.0, 7 * BIN_U, 0, 'cut', b, f"{b}_inside")
    PARTS.append((name, PN['bin']))
    c("occurrence.move", occurrence=f"{name}:1", move_grounded=True,
      matrix=[[1, 0, 0, fx(cx)], [0, 1, 0, fx(cy)], [0, 0, 1, fx(z0)]])
    return name


# ----------------------------------------------------------------------------- assembly
def params():
    for name, expr, why in [
        ("manta_clr", mm(MANTA_CLR), "Manta case to drawer wall, per side"),
        ("lid_gap", mm(LID_GAP), "drawer wall / flange top to the lid underside: nothing falls over the walls"),
        ("rail_drop", mm(RAIL_DROP), "rail top below the flange land as built (seated: lid gap + this)"),
        ("skirt_clr", mm(SKIRT_CLR), "skirt to rim, per side (stack location)"),
        ("pad_interf", mm(XD + BUMP['h'] - PAD_X), "detent bump to pad: arm deflection to open/close"),
        ("pitch", mm(P), "stack pitch: lid top + rim"),
    ]:
        c("parameters.add", name=name, expression=expr, comment=why)


def build(mode):
    cmds.clear()
    PARTS.clear()
    CHECK.clear()
    pn, desc = ASSY
    c("document.metadata.set", values={"part_number": pn, "description": desc, "revision": "X1",
                                       "project": "storage_drawers"})
    params()
    s1 = build_shelf('F1', 0.0)
    sp = build_spacer('F1', P)
    s2 = build_shelf('F2', 2 * P)
    dr = build_drawer('F1')
    cells = grid_cells()
    bn = build_bin('F1', cells[0][0], cells[0][1], ZB + T_DF)
    if mode == 'check':
        # the case grown by the clearance it needs (sides, top), lifted 0.01 off the grid it rests on
        new_component('CHECK_manta_case')
        e, top = MANTA_CHECK
        yc0 = T_DW + (DRAWER_IN[1] - MANTA[1]) / 2           # case 1.5 clear front and back
        box((-MANTA[0] / 2 - e, MANTA[0] / 2 + e), (yc0 - e, yc0 + MANTA[1] + e),
            (ZG + 0.01, ZG + MANTA[2] + top), 'new', 'CHECK_manta_case', 'CHECK_manta_case_box')
        CHECK.append('CHECK_manta_case')
    o = lambda n: f"{n}:1"  # noqa: E731
    c("component.activate", component=0)
    c("joint.as_built", type="slider", a=o(s1), b=o(dr), at={"point": [0, 0, ZDT], "z": [0, -1, 0]},
      name="S_drawer", limits=[[0.0, YD - 15.0]])
    for n in (sp, s2):
        c("joint.as_built", type="rigid", a=o(s1), b=o(n), name=f"fix_{n}")
    c("joint.as_built", type="rigid", a=o(dr), b=o(bn), name=f"fix_{bn}")
    if mode == 'check':
        c("joint.as_built", type="rigid", a=o(dr), b=o('CHECK_manta_case'), name="fix_manta")
    reg = parts.register()
    for name, p in PARTS:
        c("component.metadata.set", component=name, part_number=p, description=reg[p]['Description'],
          revision="X1", bom_type="normal")
    if mode == 'assy':
        done = set()
        for name, p in PARTS:
            if p in done:
                continue
            done.add(p)
            for ext, cmd in (('step', 'file.export_step'), ('stl', 'file.export_stl'), ('3mf', 'file.export_3mf')):
                q = dict(path=f"{VDIR}/exports/{parts.export(p, 'X1', ext)}", bodies=[name])
                if ext != 'step':
                    q["quality"] = "fine"
                c(cmd, **q)
    return list(cmds)


def out_path(mode, scratch=None):
    stem = parts.fname(ASSY[0])
    if mode == 'check':
        return os.path.join(scratch or '.', f"{stem}_check.json")
    return f"{VDIR}/cad/{stem}.json"


def write(mode, path):
    cmd_list = build(mode)
    if mode == 'assy':
        for sub in ('cad', 'exports', 'docs'):
            os.makedirs(os.path.join(ROOT, VDIR, sub), exist_ok=True)
    with open(path, 'w') as fh:
        fh.write('[\n' + ',\n'.join(' ' + json.dumps(x, separators=(',', ':')) for x in cmd_list) + '\n]\n')
    print(path, len(cmd_list), 'steps')


configure('v1')

if __name__ == '__main__':
    args = sys.argv[1:]
    if '--ver' in args:
        i = args.index('--ver')
        configure(args[i + 1])
        args = args[:i] + args[i + 2:]
    m = args[0] if args else 'assy'
    write(m, args[1] if len(args) > 1 else out_path(m))
