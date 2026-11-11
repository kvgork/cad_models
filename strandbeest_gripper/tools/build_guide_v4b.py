"""Render the step pictures of the v4b build plan (README "Build plan") from the built assembly.

Each step hides every body that isn't in place yet (browser.visibility), colours the parts
added in that step orange and lets the camera frame what is visible.

    python3 strandbeest_gripper/tools/build_guide_v4b.py     (needs the built .sc)
"""
import json
import os
import subprocess
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
VDIR = 'strandbeest_gripper/v4b_snap-pins'
SC = f'{VDIR}/cad/GRIP-9009_assy-snap-pins.sc'
OUT = f'{VDIR}/docs/build'
NEW = '#e8761a'

FRAME = ['GRIP-0033_frame-hand_F1']
GEARS = ['GRIP-0034_gear-crank-axle_F1', 'GRIP-0013_gear-crank-idle_F1', 'GRIP-0014_gear-idler-z33_F1',
         'GRIP-0014_gear-idler-z33_F2', 'GRIP-0035_thumb-wheel_F1',
         'GRIP-0048_snap-pin-crank-axle_F1', 'GRIP-0048_snap-pin-crank-axle_F2',
         'GRIP-0049_snap-pin-gear-axle_F1', 'GRIP-0049_snap-pin-gear-axle_F2', 'GRIP-0049_snap-pin-gear-axle_F3']
# finger sub-assembly, in build order (finger 1; finger 2 = same steps with the UP2 parts)
F1 = [
    ['GRIP-0018_link-f-hub_F1', 'GRIP-0019_triangle-bde-finger1_F1', 'GRIP-0045_snap-pin-j3_F1'],
    ['GRIP-0017_link-c_F1', 'GRIP-0023_triangle-ghi-hub-finger1_F1', 'GRIP-0047_snap-pin-j2-j5_F2'],
    ['GRIP-0025_jaw-pivot_F1', 'GRIP-0050_snap-pin-jaw_F1'],
    ['GRIP-0015_link-j-hub_F1', 'GRIP-0047_snap-pin-j2-j5_F1'],
    ['GRIP-0016_link-k_F1', 'GRIP-0046_snap-pin-j4_F1'],
]
F2 = ['GRIP-0018_link-f-hub_F2', 'GRIP-0021_triangle-bde-finger2_F2', 'GRIP-0045_snap-pin-j3_F2',
      'GRIP-0017_link-c_F2', 'GRIP-0024_triangle-ghi-hub-finger2_F2', 'GRIP-0047_snap-pin-j2-j5_F4',
      'GRIP-0025_jaw-pivot_F2', 'GRIP-0050_snap-pin-jaw_F2', 'GRIP-0015_link-j-hub_F2', 'GRIP-0047_snap-pin-j2-j5_F3',
      'GRIP-0016_link-k_F2', 'GRIP-0046_snap-pin-j4_F2']
MOUNT = ['GRIP-0051_snap-pin-g_F1', 'GRIP-0051_snap-pin-g_F2', 'GRIP-0043_pin-j1-shoulder_F1',
         'GRIP-0043_pin-j1-shoulder_F2']
FINGERS = [b for s in F1 for b in s] + F2

# (file, bodies already in place, bodies added now, view)
STEPS = [('step1_gear-train', FRAME, GEARS, 'iso'),
         ('step1_gear-train_top', FRAME, GEARS, 'top')]
done = []
for i, new in enumerate(F1, 2):
    STEPS.append((f'step{i}_finger', list(done), new, 'iso'))
    done += new
STEPS += [('step7_mount', FRAME + GEARS + FINGERS, MOUNT, 'iso'),
          ('step8_done_top', FRAME + GEARS + FINGERS + MOUNT, [], 'top')]


def bodies(sc):
    out = subprocess.run(['solidcraft-cli', 'eval', sc], capture_output=True, text=True, check=True, cwd=ROOT)
    return [b['name'] for b in json.loads(out.stdout)['bodies']]


def render(sc, out, steps):
    """steps: (file, bodies in place, bodies added now (orange), view). Every other body is hidden."""
    allb = bodies(sc)
    known = {b for _, old, new, _ in steps for b in old + new}
    missing = known - set(allb)
    assert not missing, f'not in the model: {sorted(missing)}'
    os.makedirs(os.path.join(ROOT, out), exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        for name, old, new, view in steps:
            hide = [b for b in allb if b not in old and b not in new]
            script = os.path.join(td, 'hide.json')
            # browser.visibility refuses an empty list: nothing to hide -> empty script
            json.dump([{"command": "browser.visibility", "params": {"visible": False, "items": hide}}] if hide else [],
                      open(script, 'w'))
            args = ['solidcraft-cli', 'snapshot', script, '--in', sc, '--out', f'{out}/{name}.png', '--view', view,
                    '--no-grid', '--no-axes', '--width', '1100', '--height', '750']
            for b in new:
                args += ['--body', f'{b}:color={NEW}']
            subprocess.run(args, check=True, stdout=subprocess.DEVNULL, cwd=ROOT)
            print(f'{out}/{name}.png: {len(old)} in place, {len(new)} new')


if __name__ == '__main__':
    render(SC, OUT, STEPS)
