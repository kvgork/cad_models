"""Render the step pictures of the v2 build plan (README "Build plan") from the built assembly.

    python3 articulated_finger/tools/build_guide_v2.py [step names]     (needs the built .sc)

The dummy servo is built parked 60 mm +X of the base (it shares the servo's place); from step 2 on the pictures
show it in the cradle (its rigid joint is dropped for the picture and it is moved -60 in X).
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'strandbeest_gripper', 'tools'))
from build_guide_v4b import bodies, NEW  # noqa: E402
import finger_common as f  # noqa: E402
import gen_v2 as g  # noqa: E402

VDIR = g.VDIR
SC = f'{VDIR}/cad/{f.parts.fname(g.ASSY)}.sc'
OUT = f'{VDIR}/docs/build'
n = g.A.cname

BASE = [n('base', 'F')]
DUMMY = [n('dummy', 'X')]
PROX = [n('proximal', 'P'), n('pin_mcp', 'MCP')]
MID = [n('middle', 'M'), n('pin_k', 'PIP')]
DIST = [n('distal', 'D'), n('pin_k', 'DIP')]
LINK2 = [n('link2', 'L2'), n('pin_ear', 'P1'), n('pin_ear', 'D1')]
LINK1 = [n('link1', 'L1'), n('pin_b0', 'B0'), n('pin_ear', 'M1')]
ROD = [n('rod', 'R'), n('pin_l', 'L')]
HORN = [n('horn', 'S'), n('pin_ear', 'H')]

# each part goes on with its own pins straight away: nothing loose waits for a pin (CLAUDE.md build-order rule)
STEPS = []
done = []
for name, new, view in (('step1_base', BASE, 'iso'), ('step2_dummy', DUMMY, 'iso'), ('step3_proximal', PROX, 'iso'),
                        ('step4_middle', MID, 'iso'), ('step5_distal', DIST, 'iso'),
                        ('step6_dip-link', LINK2, 'iso'), ('step7_pip-link', LINK1, 'back'),
                        ('step8_rod', ROD, 'iso'), ('step9_horn', HORN, 'iso')):
    STEPS.append((name, list(done), new, view, []))
    done += new
ALL = list(done)
STEPS += [('step10_done_back', ALL, [], 'back', []), ('step10_done_front', ALL, [], 'front', []),
          ('step11_curled', ALL, [], 'iso', [('HORN', 60)])]


def shot(name, visible, colour, drive, view, dummy_in=True, extra=()):
    allb = bodies(SC)
    hide = [b for b in allb if b not in visible and b not in extra]
    with tempfile.TemporaryDirectory() as td:
        s = os.path.join(td, 's.json')
        cm = []
        if dummy_in:
            cm += [{"command": "joint.delete", "params": {"joint": f"fix_{n('dummy', 'X')}"}},
                   {"command": "occurrence.move", "params": {"occurrence": g.A.occ('dummy', 'X'), "move_grounded": True,
                                                             "matrix": [[1, 0, 0, -60.0], [0, 1, 0, 0], [0, 0, 1, 0]]}}]
        cm += [{"command": "joint.drive", "params": {"joint": j, "value": v}} for j, v in drive]
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
    os.makedirs(os.path.join(f.ROOT, OUT), exist_ok=True)
    for name, prev, new, view, drv in STEPS:
        if not only or name in only:
            shot(name, prev + new, new, drv, view, dummy_in=(name != 'step1_base'))
    servo = [b for b in bodies(SC) if b.startswith('SJ-')]
    if not only or 'servo_stage' in only:
        shot('servo_stage', [b for b in ALL if b not in DUMMY] + servo, servo + HORN, [], 'iso', dummy_in=False)
