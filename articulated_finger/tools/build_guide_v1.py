"""Render the step pictures of the v1 build plan (README "Build plan") from the built assembly.

    python3 articulated_finger/tools/build_guide_v1.py [step names]     (needs the built .sc)
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'strandbeest_gripper', 'tools'))
from build_guide_v4b import render, bodies, NEW  # noqa: E402
import finger_common as f  # noqa: E402
import gen_v1 as g  # noqa: E402

VDIR = g.VDIR
SC = f'{VDIR}/cad/{f.parts.fname(g.ASSY)}.sc'
OUT = f'{VDIR}/docs/build'
n = g.A.cname

BASE = [n('base', 'F')]
PROX = [n('proximal', 'P'), n('pin_mcp', 'MCP')]
MID = [n('middle', 'M'), n('pin_k', 'PIP')]
DIST = [n('distal', 'D'), n('pin_k', 'DIP')]
RING = [n('ring', 'R')]
FINGER = BASE + PROX + MID + DIST

# each phalanx goes on with its pin straight away: nothing loose waits for a pin (CLAUDE.md build-order rule)
STEPS = []
done = []
for name, new, view in (('step1_base', BASE, 'iso'), ('step2_proximal', PROX, 'iso'), ('step3_middle', MID, 'iso'),
                        ('step4_distal', DIST, 'iso'), ('step5_ring', RING, 'iso'), ('step6_done_front', [], 'front')):
    STEPS.append((name, list(done), new, view))
    done += new


def posed(name, visible, colour, drive, view='front'):
    """Snapshot with the joints driven (render() only shows the as-built pose)."""
    allb = bodies(SC)
    hide = [b for b in allb if b not in visible]
    with tempfile.TemporaryDirectory() as td:
        s = os.path.join(td, 's.json')
        cm = [{"command": "joint.drive", "params": {"joint": j, "value": v}} for j, v in drive]
        if hide:
            cm.append({"command": "browser.visibility", "params": {"visible": False, "items": hide}})
        json.dump(cm, open(s, 'w'))
        args = ['solidcraft-cli', 'snapshot', s, '--in', SC, '--out', f'{OUT}/{name}.png', '--view', view,
                '--no-grid', '--no-axes', '--width', '1100', '--height', '750']
        for b in colour:
            args += ['--body', f'{b}:color={NEW}']
        subprocess.run(args, check=True, stdout=subprocess.DEVNULL, cwd=f.ROOT)
    print(f'{OUT}/{name}.png')


if __name__ == '__main__':
    only = sys.argv[1:]
    render(SC, OUT, [st for st in STEPS if not only or st[0] in only])
    servo = [b for b in bodies(SC) if b.startswith('SJ-')]
    for name, vis, col, drv, view in (
            ('step7_curled', FINGER, [], [('MCP', 40), ('PIP', 60), ('DIP', 45)], 'front'),
            ('servo_stage', FINGER + servo + [n('spool', 'S')], servo + [n('spool', 'S')], [], 'iso')):
        if not only or name in only:
            posed(name, vis, col, drv, view)
