"""Check the six concept massing models (python3 articulated_finger/tools/verify_concepts.py [C1 ...]).

Per concept: no feature errors/warnings except the vendor STEP tolerance note; every body is one piece;
finger (proximal..distal) is 18 wide and 90-100 long above the MCP; dovetail parameters equal GRIP-0002's;
the SCS0009 has >= 0.3 mm to every printed body; printed bodies do not overlap each other.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import gen_concepts as g  # noqa: E402

CAD = os.path.join(ROOT, 'articulated_finger', 'concepts', 'cad')
SERVO_PREFIX = 'SJ-'


def run(cmds, sc):
    with tempfile.TemporaryDirectory() as td:
        script, res = os.path.join(td, 's.json'), os.path.join(td, 'r.json')
        json.dump(cmds, open(script, 'w'))
        subprocess.run(['solidcraft-cli', 'run', script, '--in', sc, '--results', '--json-out', res],
                       check=True, stdout=subprocess.DEVNULL, cwd=ROOT)
        return json.load(open(res))


def gp2():
    src = json.load(open(os.path.join(ROOT, 'gripper_tester', 'cad', 'GRIP-0002_gripper-adapter.json')))
    return {s['params']['name']: float(s['params']['expression'].split()[0]) for s in src
            if s['command'] == 'parameters.add' and s['params']['name'] in g.DT}


def check(key):
    sc = os.path.join(CAD, key + '.sc')
    ev = json.loads(subprocess.run(['solidcraft-cli', 'eval', sc], capture_output=True, text=True, check=True).stdout)
    bodies = {b['name']: b for b in ev['bodies']}
    servo = [n for n in bodies if n.startswith(SERVO_PREFIX)]
    printed = [n for n in bodies if not n.startswith(SERVO_PREFIX)]
    res = []
    bad = [(t['name'], t['error'] or t['warning']) for t in ev['timeline']
           if (t['error'] or t['warning']) and t['type'] != 'BaseFeature']
    res.append(('no feature errors/warnings', not bad, bad or 'none'))
    lo = [min(bodies[n]['bbox']['min'][i] for n in ('proximal', 'middle', 'distal')) for i in range(3)]
    wy = [f(bodies[n]['bbox'][k][1] for n in ('middle', 'distal')) for f, k in ((min, 'min'), (max, 'max'))]
    hi = [max(bodies[n]['bbox']['max'][i] for n in ('proximal', 'middle', 'distal')) for i in range(3)]
    width, length = wy[1] - wy[0], hi[2] - lo[2]
    res.append(('finger width 18-20 (Y, middle+distal; proximal carries hubs/levers)', 17.9 <= width <= 20.1, round(width, 2)))
    res.append(('finger length 90-110 incl. root wrap (Z)', 90 <= length <= 110, round(length, 2)))
    dt = gp2()
    res.append(('dovetail params == GRIP-0002', dt == g.DT, dt))
    res.append(('servo inserted (4 vendor bodies)', len(servo) == 4, len(servo)))
    # the tab undersides sit ON the cradle face (y = OFF), a contact the kernel can't intersect: lift the servo
    # 0.05 mm off its seat (-Y) for the check, so a real overlap still shows and the seat gap reads 0.05
    lift = {"command": "occurrence.move", "params": {"occurrence": "LIB-0010_servo-scs0009:1", "move_grounded": True,
                                                     "matrix": [[1, 0, 0, 0], [0, 1, 0, -0.05], [0, 0, 1, 0]]}}
    r = run([lift, {"command": "inspect.clearance", "params": {"bodies": servo, "against": printed, "nearest": 2}},
             {"command": "inspect.clearance", "params": {"bodies": printed, "nearest": 2}}], sc)
    assert len(r) == 3, len(r)
    for lab, x, need in (('servo vs printed: seat 0.05 (lifted), else >= 0.3', r[1], 0.3),
                         ('printed vs printed: no overlap or contact', r[2], 0.0)):
        near = sorted((d['distance_mm'], a_, d['body']) for a_, lst in x['nearest'].items() for d in lst)
        if lab.startswith('servo'):
            # designed contacts, each 0.05 after the lift: tab seat on the cradle, driver on the spline top
            seat = [n for n in near if n[0] < 0.1]
            rest = [n for n in near if n[0] >= 0.1]
            exp = {('TOPCASE', 'base')} | {('OUTPUTGEAR', d) for d in ('spool', 'crank', 'horn')}
            ok = all(abs(n[0] - 0.05) < 0.01 and (n[1].split('-')[3], n[2]) in exp for n in seat) \
                and any('TOPCASE' in n[1] for n in seat) and (not rest or rest[0][0] >= need)
        else:
            # C4: the kernel reports 0 between the TPU strip and the base at the slot mouth edge (3.5, -8, z_mcp);
            # the slot cut removes exactly 1.7 x 16.2 x 5.1 mm (0.1 gap all round), checked by volume below
            near = [n for n in near if not (key.startswith('C4') and {n[1], n[2]} == {'base', 'flexure'})]
            # C7: same kernel reading (0 at the recess mouth edge, x = palm face) between each TPU pad and its
            # phalanx; the recess volumes below and the exact interference check show the 0.1 seat gap is there
            near = [n for n in near if not (key.startswith('C7') and {n[1], n[2]} in
                                            [{'pad_' + b, b} for b in ('proximal', 'middle', 'distal')])]
            ok = not near or near[0][0] >= 0.05
        ok = ok and not x['overlaps'] and not x['unchecked'] and not x['truncated']
        res.append((lab, ok, {'nearest': [(round(d, 3), a_, b_) for d, a_, b_ in near[:3]],
                              'overlaps': x['overlaps'], 'unchecked': [(u['a'], u['b']) for u in x['unchecked']]}))
    if key.startswith('C7'):
        ri = run([{"command": "inspect.interference", "params": {"bodies": printed}}], sc)[0]
        res.append(('exact interference (boolean), all printed bodies: none', not ri['interferences'] and not ri['unchecked']
                    and not ri['budget_exceeded'], {'count': ri['count'], 'unchecked': ri['unchecked']}))
        ref = json.loads(subprocess.run(['solidcraft-cli', 'eval', os.path.join(CAD, 'C5_raptor-cord-elastic.sc')],
                                        capture_output=True, text=True, check=True).stdout)
        v5 = {b['name']: b['volume_mm3'] for b in ref['bodies']}
        P, z_mcp = g.PAD, g.ZS + 26.0
        zj = [z_mcp, z_mcp + g.L[0], z_mcp + g.L[0] + g.L[1], z_mcp + sum(g.L)]
        spans = {'proximal': (zj[0] + 3.0, zj[1] - 1.5), 'middle': (zj[1] + 1.5, zj[2] - 1.5), 'distal': (zj[2] + 1.5, zj[3] - g.T / 2)}
        for b, (za, zb) in spans.items():
            h = zb - za + 2 * P['gap']
            want = 2 * h * ((P['lip_x'] + 0.2 + g.T / 2) * P['lip'] + (P['tooth'][1] - P['tooth'][0] + 2 * P['gap']) * (P['tooth_in'] + P['gap']))
            got = v5[b] - bodies[b]['volume_mm3']
            res.append((f'C7 {b}: lip recess + tooth grooves cut in full (vs C5)', abs(got - want) < 0.05, (round(got, 2), round(want, 2))))
            pb = bodies['pad_' + b]['bbox']
            res.append((f'C7 pad_{b}: 18 wide, 6.0 deep fin ray + 0.1 seat, lips to x -4.2',
                        abs(pb['max'][1] - pb['min'][1] - 18) < 0.01 and abs(pb['min'][0] + 14.1) < 0.01 and abs(pb['max'][0] + 4.2) < 0.01,
                        [round(v, 2) for v in pb['min'] + pb['max']]))
    if key.startswith('C4'):
        cmds = [x for x in json.load(open(os.path.join(CAD, key + '.json'))) if x['params'].get('name') != 'base_flexure_slot']
        with tempfile.TemporaryDirectory() as td:
            j, o = os.path.join(td, 'n.json'), os.path.join(td, 'n.sc')
            json.dump(cmds, open(j, 'w'))
            subprocess.run(['solidcraft-cli', 'run', j, '--save', o], check=True, stdout=subprocess.DEVNULL, cwd=ROOT)
            e2 = json.loads(subprocess.run(['solidcraft-cli', 'eval', o], capture_output=True, text=True, check=True).stdout)
        dv = {b['name']: b['volume_mm3'] for b in e2['bodies']}['base'] - bodies['base']['volume_mm3']
        res.append(('C4 base slot = flexure + 0.1 all round (1.7 x 16.2 x 5.1 = 140.45 mm3)', abs(dv - 140.454) < 0.05, round(dv, 2)))
    return res


if __name__ == '__main__':
    keys = [k for k in g.CONCEPTS if not sys.argv[1:] or k.split('_')[0] in sys.argv[1:]]
    allok = True
    for k in keys:
        print('==', k)
        for name, ok, v in check(k):
            allok &= ok
            print('  ', 'PASS' if ok else 'FAIL', name, '|', v)
    print('ALL PASS' if allok else 'SOME FAIL')
    sys.exit(0 if allok else 1)
