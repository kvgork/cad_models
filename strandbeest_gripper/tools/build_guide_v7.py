"""Render the step pictures of the v7 build plan (README "Build plan") from the built assembly.

    python3 strandbeest_gripper/tools/build_guide_v7.py [step names]     (needs the built .sc)

Pin instance numbers follow gen_v7.V7.locations(): per finger leg A, leg B (crank, G low, G top, arm,
jaw, J2, J3, J4, J5), then that finger's Z33 + Z20 idlers and 4 pillars; the wheel axle last.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_guide_v4b import render  # noqa: E402

VDIR = 'strandbeest_gripper/v7_sandwich'
SC = f'{VDIR}/cad/GRIP-9014_assy-sandwich.sc'
OUT = f'{VDIR}/docs/build'
LEGS4 = ('A1', 'B1', 'A2', 'B2')                 # order of the legs in locations()


def b(name, i):
    return f'{name}_F{i}'


def idx(tag):
    return LEGS4.index(tag)                       # 0..3


P_CRANK, P_X, P_J23, P_ARM = 'GRIP-0088_snap-pin-2f-crank-axle', 'GRIP-0089_snap-pin-2f-idler-z20', \
    'GRIP-0090_snap-pin-2f-j2-j3', 'GRIP-0091_snap-pin-2f-z33-arm'
P_J4, P_GTOP, P_J5G, P_JAW = 'GRIP-0092_snap-pin-2f-j4', 'GRIP-0093_snap-pin-2f-g-top', \
    'GRIP-0094_snap-pin-2f-j5-g-low', 'GRIP-0095_snap-pin-2f-jaw'
P_PILLAR, P_WHEEL, P_J1 = 'GRIP-0096_snap-pin-2f-pillar', 'GRIP-0097_snap-pin-2f-wheel', \
    'GRIP-0075_pin-j1-shoulder-double-press'
ARM_I = {'A1': 1, 'A2': 2, 'B1': 3, 'B2': 4}      # arm / J1 pin instances follow the crank list A1 A2 B1 B2
ARM_PIN = {'A1': 1, 'B1': 2, 'A2': 4, 'B2': 5}    # GRIP-0091 instances 3 and 6 are the Z33 idler axles

FRAME = ['GRIP-0070_frame-sandwich_F1']
GEARS = ['GRIP-0076_gear-crank-a1-sandwich_F1', 'GRIP-0077_gear-crank-a2-sandwich_F1',
         'GRIP-0078_gear-crank-b1-sandwich_F1', 'GRIP-0079_gear-crank-b2-sandwich_F2',
         'GRIP-0014_gear-idler-z33_F1', 'GRIP-0014_gear-idler-z33_F2',
         'GRIP-0065_gear-idler-leg-b_F1', 'GRIP-0065_gear-idler-leg-b_F2', 'GRIP-0074_gear-wheel-hub_F1'] + \
        [b(P_CRANK, i) for i in range(1, 5)] + [b(P_ARM, 3), b(P_ARM, 6)] + [b(P_X, i) for i in (1, 2)]


def leg(tag):
    f, legb = int(tag[1]), tag[0] == 'B'
    s = f'_F{f}{"B" if legb else ""}'
    tf = 3 - f if legb else f                     # mirrored leg B carries the other finger's triangles
    bde = ('GRIP-0084_triangle-bde-finger1-v7' if tf == 1 else 'GRIP-0085_triangle-bde-finger2-v7') + s
    ghi = ('GRIP-0086_triangle-ghi-hub-finger1-v7' if tf == 1 else 'GRIP-0087_triangle-ghi-hub-finger2-v7') + s
    n = idx(tag)
    return [
        [bde, 'GRIP-0083_link-f-hub-v7' + s, b(P_J23, 2 * n + 2)],                          # J3, from the top
        ['GRIP-0080_link-j-v7' + s, b(P_J23, 2 * n + 1)],                                   # J2, from the top
        ['GRIP-0081_link-k-v7' + s, ghi, 'GRIP-0082_link-c-v7' + s, b(P_J4, n + 1), b(P_J5G, 2 * n + 2)],
    ]


LEGS = [x for t in LEGS4 for st in leg(t) for x in st]
MOUNT = [b(P_J1, i) for i in range(1, 5)] + [b(P_J5G, 2 * idx(t) + 1) for t in LEGS4]
ARMS = [b('GRIP-0072_arm-crank-top', i) for i in range(1, 5)]
TOP = ['GRIP-0071_top-plate_F1', 'GRIP-0071_top-plate_F2'] + [b(P_PILLAR, i) for i in range(1, 9)] + \
      [b(P_ARM, ARM_PIN[t]) for t in LEGS4] + [b(P_GTOP, i) for i in range(1, 5)]
KNOB = ['GRIP-0073_knob-thumb-hex_F1', b(P_WHEEL, 1)]
JAWS = ['GRIP-0066_jaw-long-slot_F1', 'GRIP-0066_jaw-long-slot_F2'] + [b(P_JAW, i) for i in range(1, 5)]

STEPS = [('step1_gear-train', FRAME, GEARS, 'iso'), ('step1_gear-train_top', FRAME, GEARS, 'top')]
done = []
for i, new in enumerate(leg('A1'), 2):
    STEPS.append((f'step{i}_leg', list(done), new, 'iso'))
    done += new
base = FRAME + GEARS
STEPS += [('step5_mount', base + LEGS, MOUNT, 'iso'),
          ('step6_arms', base + LEGS + MOUNT, ARMS, 'iso'),
          ('step7_top-plates', base + LEGS + MOUNT + ARMS, TOP, 'iso'),
          ('step8_knob', base + LEGS + MOUNT + ARMS + TOP, KNOB, 'iso'),
          ('step9_jaws', base + LEGS + MOUNT + ARMS + TOP + KNOB, JAWS, 'iso'),
          ('step10_done_top', base + LEGS + MOUNT + ARMS + TOP + KNOB + JAWS, [], 'top'),
          ('step10_done_iso', base + LEGS + MOUNT + ARMS + TOP + KNOB + JAWS, [], 'iso'),
          ('legB_step2', [], leg('B1')[0], 'iso')]

if __name__ == '__main__':
    only = sys.argv[1:]
    render(SC, OUT, [st for st in STEPS if not only or st[0] in only])
