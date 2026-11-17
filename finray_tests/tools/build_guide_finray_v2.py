"""Render the build-plan pictures of finray_tests v2 (parallel + pull module) and v2b (C-socket) from the built
assemblies. The pull pictures come from the pull check variant, built here in a temporary folder.

    python3 finray_tests/tools/build_guide_finray_v2.py [v2|v2b]      (needs the built .sc of each version)
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'strandbeest_gripper', 'tools'))
from build_guide_v4b import render  # noqa: E402
import gen_finray_v2 as v  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))


def names(mode):
    v.build(mode)
    return [n for n, _ in v.PARTS] + [n for n, _, _ in v.PURCHASED]


def pick(allb, *pre):
    return [n for n in allb if any(n.startswith(p) for p in pre)]


def steps(seq):
    out, done = [], []
    for name, new, view in seq:
        out.append((name, list(done), new, view))
        done += new
    return out


def drive(a):
    return [('step1_base-pinion', pick(a, 'GRIP-0124', 'GRIP-0055'), 'iso'),
            ('step2_carriages-screw-knob', pick(a, 'GRIP-0125', 'GRIP-0126', 'GRIP-0056', 'M6'), 'iso')]


def main(which):
    if 'v2' in which:
        a = names('parallel')
        sc = f"{v.VDIR['parallel']}/cad/{os.path.basename(v.out_path('parallel')).replace('.json', '.sc')}"
        par = steps(drive(a) + [
            ('step3_parallel-holders', pick(a, 'GRIP-0127', 'M3x8-ISO4762_hold'), 'iso'),
            ('step4_parallel-fingers-pins', pick(a, 'GRIP-0133', 'GRIP-0134'), 'iso'),
            ('step5_parallel-done-top', [], 'top')])
        render(sc, f"{v.VDIR['parallel']}/docs/build", par)
        p = names('pull')
        base = pick(p, 'GRIP-0124', 'GRIP-0055', 'GRIP-0125', 'GRIP-0126', 'GRIP-0056', 'M6')
        pull = [(n, base + old, new, view) for n, old, new, view in steps([
            ('pull1_brackets', pick(p, 'GRIP-0128', 'GRIP-0129', 'M3x8-ISO4762_br'), 'iso'),
            ('pull2_sliders', pick(p, 'GRIP-0130'), 'iso'),
            ('pull3_fingers-pins', pick(p, 'GRIP-0133', 'GRIP-0134'), 'iso'),
            ('pull4_cam-plates', pick(p, 'GRIP-0131', 'GRIP-0132'), 'iso'),
            ('pull5_done-top', [], 'top')])]
        with tempfile.TemporaryDirectory() as td:
            js = v.out_path('pull', td)
            v.write('pull', js)
            scp = os.path.join(td, 'pull.sc')
            subprocess.run(['solidcraft-cli', 'run', js, '--save', scp], check=True, stdout=subprocess.DEVNULL, cwd=ROOT)
            render(scp, f"{v.VDIR['pull']}/docs/build", pull)
    if 'v2b' in which:
        a = names('csocket')
        sc = f"{v.VDIR['csocket']}/cad/{os.path.basename(v.out_path('csocket')).replace('.json', '.sc')}"
        render(sc, f"{v.VDIR['csocket']}/docs/build", steps(drive(a) + [
            ('step3_c-socket-holders', pick(a, 'GRIP-0136', 'M3x8-ISO4762_hold'), 'iso'),
            ('step4_fingers-slide-in', pick(a, 'GRIP-0135'), 'iso'),
            ('step5_done-top', [], 'top')]))


if __name__ == '__main__':
    main(sys.argv[1:] or ['v2', 'v2b'])
