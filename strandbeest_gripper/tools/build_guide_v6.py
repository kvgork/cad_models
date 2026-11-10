"""Render the step pictures of the v6 build plan (README "Build plan") from the built assembly.

    python3 strandbeest_gripper/tools/build_guide_v5.py     (needs the built .sc)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_guide_v4b import render  # noqa: E402

VDIR = 'strandbeest_gripper/v6_mirror-legs'
SC = f'{VDIR}/cad/GRIP-9012_assy-mirror-legs.sc'
OUT = f'{VDIR}/docs/build'


def pin(key, i):
    return f'{key}_F{i}'


FRAME = ['GRIP-0062_frame-mirror-legs_F1']
GEARS = ['GRIP-0034_gear-crank-axle_F1', 'GRIP-0013_gear-crank-idle_F1', 'GRIP-0063_gear-crank-mirror-finger1_F1',
         'GRIP-0064_gear-crank-mirror-finger2_F2', 'GRIP-0014_gear-idler-z33_F1', 'GRIP-0014_gear-idler-z33_F2',
         'GRIP-0065_gear-idler-leg-b_F1', 'GRIP-0065_gear-idler-leg-b_F2', 'GRIP-0035_thumb-wheel_F1'] + \
        [pin('GRIP-0048_snap-pin-crank-axle', i) for i in range(1, 5)] + \
        [pin('GRIP-0049_snap-pin-gear-axle', i) for i in range(1, 4)] + \
        [pin('GRIP-0061_snap-pin-idler-z60', i) for i in range(1, 3)]
# pin instance numbers follow gen_v3 locations(): leg A finger 1, A2, B1, B2
J2 = {'A1': 1, 'A2': 3, 'B1': 5, 'B2': 7}
J5 = {'A1': 2, 'A2': 4, 'B1': 6, 'B2': 8}
N = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4}


def leg(tag):
    f, b = int(tag[1]), ('B' if tag[0] == 'B' else '')
    s = f'_F{f}{b}'
    tf = f if not b else 3 - f          # mirrored leg B carries the other finger's triangles
    bde = 'GRIP-0019_triangle-bde-finger1' if tf == 1 else 'GRIP-0021_triangle-bde-finger2'
    ghi = 'GRIP-0023_triangle-ghi-hub-finger1' if tf == 1 else 'GRIP-0024_triangle-ghi-hub-finger2'
    return [
        ['GRIP-0018_link-f-hub' + s, bde + s, pin('GRIP-0045_snap-pin-j3', N[tag])],
        ['GRIP-0017_link-c' + s, ghi + s, pin('GRIP-0047_snap-pin-j2-j5', J5[tag])],
        ['GRIP-0015_link-j-hub' + s, pin('GRIP-0047_snap-pin-j2-j5', J2[tag])],
        ['GRIP-0016_link-k' + s, pin('GRIP-0046_snap-pin-j4', N[tag])],
    ]


LEGS = [b for t in ('A1', 'A2', 'B1', 'B2') for st in leg(t) for b in st]
MOUNT = [pin('GRIP-0051_snap-pin-g', i) for i in range(1, 5)] + [pin('GRIP-0043_pin-j1-shoulder', i) for i in range(1, 5)]
JAWS = ['GRIP-0066_jaw-long-slot_F1', 'GRIP-0066_jaw-long-slot_F2'] + [pin('GRIP-0050_snap-pin-jaw', i) for i in range(1, 5)]

STEPS = [('step1_gear-train', FRAME, GEARS, 'iso'), ('step1_gear-train_top', FRAME, GEARS, 'top')]
done = []
for i, new in enumerate(leg('A1'), 2):
    STEPS.append((f'step{i}_leg', list(done), new, 'iso'))
    done += new
STEPS += [('step6_mount', FRAME + GEARS + LEGS, MOUNT, 'iso'),
          ('step7_jaws', FRAME + GEARS + LEGS + MOUNT, JAWS, 'iso'),
          ('step8_done_top', FRAME + GEARS + LEGS + MOUNT + JAWS, [], 'top'),
          ('labels_leg', [], leg('A1')[0][:2] + leg('A1')[1][:2] + leg('A1')[2][:1] + leg('A1')[3][:1], 'top'),
          ('legB_step2', [], leg('B1')[0], 'iso'),
          ('finger1_legs_top', [], [b for t in ('A1', 'B1') for st in leg(t) for b in st], 'top')]

if __name__ == '__main__':
    only = sys.argv[1:]
    render(SC, OUT, [st for st in STEPS if not only or st[0] in only])
