"""Render the build-plan pictures of a storage_drawers version from its built stack.

    python3 storage_drawers/tools/build_guide_storage.py [--ver v1|v2]   (needs <version>/cad/<ASSY>.sc)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'strandbeest_gripper', 'tools'))
from build_guide_v4b import render  # noqa: E402
import gen_storage as g  # noqa: E402

if '--ver' in sys.argv:
    g.configure(sys.argv[sys.argv.index('--ver') + 1])
g.build('assy')
N = [n for n, _ in g.PARTS]
s1, s2 = sorted(n for n in N if n.startswith('STOR-0001'))
sp = next(n for n in N if n.startswith('STOR-0003'))
dr = next(n for n in N if n.startswith(g.PN['drawer']))
bn = next(n for n in N if n.startswith('STOR-0004'))
SC = f"{g.VDIR}/cad/{g.parts.fname(g.ASSY[0])}.sc"
STEPS = [('step1_shelf', [], [s1], 'iso'),
         ('step2_drawer-in', [s1], [dr], 'iso'),
         ('step3_bin-in-grid', [s1, dr], [bn], 'top'),
         ('step4_spacer-snaps-on', [s1, dr, bn], [sp], 'iso'),
         ('step5_shelf-snaps-on', [s1, dr, bn, sp], [s2], 'iso')]

if __name__ == '__main__':
    render(SC, f"{g.VDIR}/docs/build", STEPS)
