"""Render the build-plan pictures for grasp_validation (README "Build plan") from the built
GRIP-9015 assembly. Each step hides what isn't in place yet and colours the new parts orange.

    python3 grasp_validation/tools/build_guide.py     (needs the built .sc)
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import gen_grasp as g  # noqa: E402

SC = f'{g.VDIR}/cad/GRIP-9015_assy-grasp-bench-stage1-2.sc'
OUT = f'{g.VDIR}/docs/build'
NEW = '#e8761a'
CLI = os.environ.get('SOLIDCRAFT_CLI', 'solidcraft-cli')


def steps():
    g.build()
    n = {pn: name for name, pn in g.PARTS}
    J = {k: n[g.PN[k]] for k in g.PN}
    cell = {s: f"load-cell-TAL220B-{s}30_F1" for s in 'wd'}
    dow = {s: [f"dowel-4x28-ISO2338-{s}30_F{i}" for i in (1, 2)] for s in 'wd'}
    box_ = [J['box']]
    w_done = [J['aw'], cell['w']] + dow['w'] + [J['bw']]
    return [
        ('step1_hub-box', [], box_, 'iso'),
        ('step2_hub-lid', box_, [J['lid']], 'iso'),
        ('step3_cell-on-jaw-a', [], [J['aw'], cell['w']], 'iso'),
        ('step4_dowels', [J['aw'], cell['w']], dow['w'], 'iso'),
        ('step5_jaw-b', [J['aw'], cell['w']] + dow['w'], [J['bw']], 'iso'),
        ('step6_calibrate-w30', w_done, [J['platform']], 'iso'),
        ('step7_d30-in-cradle', [], [J['cradle'], J['ad'], J['bd'], cell['d']] + dow['d'], 'iso'),
        ('step8_dovetail-receptacle', [], [J['dr']], 'iso'),
        ('overview', [b for b in all_bodies()], [], 'iso'),
    ]


def all_bodies():
    out = subprocess.run([CLI, 'eval', SC], capture_output=True, text=True, check=True, cwd=ROOT).stdout
    return [b['name'] for b in json.loads(out[out.index('{'):])['bodies']]


def render():
    allb = all_bodies()
    st = steps()
    known = {b for _, old, new, _ in st for b in old + new}
    missing = known - set(allb)
    assert not missing, f'not in the model: {sorted(missing)}'
    os.makedirs(os.path.join(ROOT, OUT), exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        for name, old, new, view in st:
            hide = [b for b in allb if b not in old and b not in new]
            script = os.path.join(td, 'hide.json')
            json.dump([{"command": "browser.visibility", "params": {"visible": False, "items": hide}}] if hide else [],
                      open(script, 'w'))
            args = [CLI, 'snapshot', script, '--in', SC, '--out', f'{OUT}/{name}.png', '--view', view,
                    '--no-grid', '--no-axes', '--width', '1100', '--height', '750']
            for b in new:
                args += ['--body', f'{b}:color={NEW}']
            subprocess.run(args, check=True, stdout=subprocess.DEVNULL, cwd=ROOT)
            print(f'{OUT}/{name}.png: {len(old)} in place, {len(new)} new')


if __name__ == '__main__':
    render()
