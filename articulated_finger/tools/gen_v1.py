"""Generate v1_raptor-cord/cad/GRIP-9020_assy-finger-raptor-cord.json: concept C5 made printable.

Concept C5 (e-NABLE Raptor principle, user pick 2026-11-22 "working prototypes, C5 + C6 only"): pin joints,
a flexor cord on the palm side, an elastic cord on the back that opens the finger. Hand first: the cord runs
down the palm side, out under the cord-guide bar to a pull ring. Servo stage: the SCS0009 slides into the
cradle between the fork posts and the spool (GRIP-0147) goes on its spline; the cord wraps the spool.

Knuckles, pins, base: finger_common.py. Every part prints without supports:
  phalanges on their back (+X face down), pins on a flat, base dovetail down, ring and spool flat.

    python3 articulated_finger/tools/gen_v1.py
    tools/build.sh articulated_finger/v1_raptor-cord
    python3 articulated_finger/tools/verify_v1.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import finger_common as f  # noqa: E402
from finger_common import c, box, cyl_y, cyl_z, fx  # noqa: E402

VDIR = 'articulated_finger/v1_raptor-cord'
ASSY = 'GRIP-9020'
PN = {'base': 'GRIP-0140', 'proximal': 'GRIP-0141', 'middle': 'GRIP-0142', 'distal': 'GRIP-0143',
      'pin_mcp': 'GRIP-0144', 'pin_k': 'GRIP-0145', 'ring': 'GRIP-0146', 'spool': 'GRIP-0147'}
A = f.Assy(VDIR, ASSY, PN)
OFF = 4.0 + 11.65 + 0.1                       # servo tab plane y (concept C5): spline top at y 4.1

# spool on the spline (servo stage)
SPLINE_TOP = OFF - 11.65                      # 4.1
COLLAR = OFF - 8.75                           # 7.0 (gear collar top, 0.3 over the drawing)
SPOOL = dict(drum_d=12.0, flange_d=18.0, flange_t=1.2, hub_d=9.0, y0=-4.0, y_hub=COLLAR - 0.3,
             bore_d=4.0 + 0.1, screw_d=2.4, head_d=4.4, head_h=1.6, cord_d=1.6, cord_x=3.5)
RING = dict(od=26.0, id=18.0, t=4.0, tab=8.0, hole=2.0, at=(-45.0, 0.0))


def spool():
    n = A.new('spool', 'S')
    s, z = SPOOL, f.ZS
    yd0, yd1 = s['y0'] + s['flange_t'], -s['y0'] - s['flange_t']          # drum between the flanges (|y| 2.8)
    cyl_y(s['flange_d'], 0, z, s['y0'], yd0 + 0.01, "new", n, f"{n}_flange_n")
    cyl_y(s['drum_d'], 0, z, yd0, yd1, "join", n, f"{n}_drum")
    cyl_y(s['flange_d'], 0, z, yd1 - 0.01, -s['y0'], "join", n, f"{n}_flange_p")
    cyl_y(s['hub_d'], 0, z, -s['y0'] - 0.3, s['y_hub'], "join", n, f"{n}_hub")
    # press bore over the 20T spline (drawn 0.1 over its OD 4.0: small holes print small), 0.4 past its end
    cyl_y(s['bore_d'], 0, z, SPLINE_TOP - 0.4, s['y_hub'] + 0.5, "cut", n, f"{n}_spline_bore")
    cyl_y(s['screw_d'], 0, z, s['y0'] - 0.5, SPLINE_TOP, "cut", n, f"{n}_screw_hole")
    cyl_y(s['head_d'], 0, z, s['y0'] - 0.5, s['y0'] + s['head_h'], "cut", n, f"{n}_screw_head")
    cyl_z(s['cord_d'], s['cord_x'], 0, z - 8, z + 8, "cut", n, f"{n}_cord_hole")
    return n


def ring():
    n = A.new('ring', 'R')
    r = RING
    x, y = r['at']
    cyl_z(r['od'], x, y, 0, r['t'], "new", n, f"{n}_outer")
    cyl_z(r['id'], x, y, -0.5, r['t'] + 0.5, "cut", n, f"{n}_inner")
    box((x + r['od'] / 2 - 1.0, x + r['od'] / 2 + r['tab']), (-4.0, 4.0), (0, r['t']), "join", n, f"{n}_tab")
    cyl_z(r['hole'], x + r['od'] / 2 + r['tab'] / 2 + 0.5, y, -0.5, r['t'] + 0.5, "cut", n, f"{n}_cord_hole")
    return n


def build():
    A.comps.clear()
    A.header()
    for name, expr, why in [
        ("pin_clear", f"{f.CLEAR} mm", "printed pin in printed hole, play per side (user rule 0.10-0.15)"),
        ("pin_hole", f"{f.PIN_HOLE} mm", "knuckle / MCP pin hole (teardrop), D3.1 snap pins"),
        ("side_gap", f"{f.SG} mm", "tongue / cheek and finger / base cheek, per side"),
        ("knuckle_gap", f"{f.RG} mm", "radial gap around the rounded knuckle ends"),
        ("channel", f"{f.CH} mm", "square cord / elastic channel (1 mm Dyneema, 1-1.5 mm elastic cord)"),
    ]:
        c("parameters.add", name=name, expression=expr, comment=why)
    b = A.new('base', 'F', grounded=True)
    f.base(b, OFF, centre_dovetail=True)
    for key, i, inst in (('proximal', 0, 'P'), ('middle', 1, 'M'), ('distal', 2, 'D')):
        f.phalanx(A.new(key, inst), i)
    n = A.new('pin_mcp', 'MCP')
    f.snap_pin_y(n, 0, f.Z_MCP, -f.CHEEK_Y1 - f.HEAD_GAP, f.CHEEK_Y1)
    for j, inst in ((1, 'PIP'), (2, 'DIP')):
        n = A.new('pin_k', inst)
        f.snap_pin_y(n, 0, f.ZJ[j], -f.W / 2 - f.HEAD_GAP, f.W / 2)
    ring()
    spool()
    A.servo(OFF)
    # joints
    c("component.activate", component=0)
    o = A.occ
    f.rev_y("MCP", o('base', 'F'), o('proximal', 'P'), f.ZJ[0])
    f.rev_y("PIP", o('proximal', 'P'), o('middle', 'M'), f.ZJ[1])
    f.rev_y("DIP", o('middle', 'M'), o('distal', 'D'), f.ZJ[2])
    for a, bb in ((o('base', 'F'), o('pin_mcp', 'MCP')), (o('proximal', 'P'), o('pin_k', 'PIP')),
                  (o('middle', 'M'), o('pin_k', 'DIP')), (o('base', 'F'), o('ring', 'R')), (o('base', 'F'), o('spool', 'S'))):
        f.rigid(a, bb)
    A.finish()
    return f.cmds


if __name__ == '__main__':
    build()
    print(A.write(), len(f.cmds), 'steps')
