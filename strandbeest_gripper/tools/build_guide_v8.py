"""Render the step pictures of the v8 build plan (README "Build plan") from the built assembly.

    python3 strandbeest_gripper/tools/build_guide_v8.py [step names]     (needs the built .sc)

Body names come from gen_v8 (component = body = <PN>_<name>_<instance>).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_guide_v4b import render  # noqa: E402
import gen_v8 as g  # noqa: E402

VDIR = g.VDIR
SC = f'{VDIR}/cad/{g.parts.fname(g.ASSY)}.sc'
OUT = f'{VDIR}/docs/build'
L = g.LEGS


def n(key, i):
    return g.cname(key, i)


FRAME = [n('frame', 'F')]
IDLERS = [n('idler', 'X1'), n('idler', 'X2'), n('pin_x', 'X1'), n('pin_x', 'X2')]
CRANKS = [n(('crank', x), x) for x in L]
SHAFTS = [n('shaft_knob', 'A1')] + [n('shaft', x) for x in L[1:]]
QPINS = [n('pin_q', x) for x in L]
COUPLERS = [n('coupler', x) for x in L]
ROCKERS = [n('rocker', x) for x in L] + [n('pin_b', x) for x in L]
JAWS = [n('jaw', 'F1'), n('jaw', 'F2')] + [n('pin_p', x) for x in L]
PLATE = [n('plate', 'F')]
KNOB = [n('knob', 'A1')]

# Order (user 2026-11-22): shafts and column pins go in from below right after the gears, so they hold the gears
# and stand up as guides; the top plate goes down over all 8 barbs at the end (no loose stack to turn over).
STEPS = []
done = []
for name, new, view in (('step1_idlers', FRAME + IDLERS, 'iso'), ('step2_cranks', CRANKS + SHAFTS, 'iso'),
                        ('step2_cranks_top', [], 'top'), ('step3_column-pins', QPINS, 'iso'),
                        ('step4_couplers', COUPLERS, 'iso'), ('step5_rockers', ROCKERS, 'iso'),
                        ('step6_jaws', JAWS, 'iso'), ('step7_top-plate', PLATE, 'iso'),
                        ('step8_knob', KNOB, 'iso'), ('step9_done_top', [], 'top'), ('step9_done_iso', [], 'iso')):
    STEPS.append((name, list(done), new, view))
    done += new

if __name__ == '__main__':
    only = [a for a in sys.argv[1:] if a != 'b']   # 'b' selects v8b in gen_v8
    render(SC, OUT, [st for st in STEPS if not only or st[0] in only])
