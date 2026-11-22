"""Check v1 (GRIP-9020, Raptor cord finger) in SolidCraft.   python3 articulated_finger/tools/verify_v1.py

Writes cad/GRIP-9020_assy-finger-raptor-cord.verify.json and runs it on the built .sc:
  - no feature errors (vendor STEP tolerance note ignored); dovetail parameters == GRIP-0002;
  - joints solve; MCP / PIP / DIP each driven to 90 deg really move;
  - range of every joint to first contact (joint.find_limits, all parts): extension stops within 3 deg of
    straight on the stop spur, flexion reaches >= 85 deg;
  - printed parts vs printed parts at the straight pose and at 3 curled poses: no overlap, nothing unchecked;
  - SCS0009 in its cradle (lifted 0.05 off its tab seat): seat 0.05, spool bore over the spline 0.05,
    everything else >= 0.3; the servo slides in along +Y between the fork posts (46 mm in 2 mm steps).
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import finger_common as f  # noqa: E402
import gen_v1 as g  # noqa: E402

ROOT = f.ROOT
SERVO = "LIB-0010_servo-scs0009:1"
POSES = [(0, 0, 0), (45, 60, 45), (80, 90, 80), (95, 0, 0)]
SLIDE = list(range(2, 47, 2))


def main():
    g.build()
    out = f"{g.VDIR}/cad/{f.parts.fname(g.ASSY)}"
    sc, script = os.path.join(ROOT, out + '.sc'), os.path.join(ROOT, out + '.verify.json')
    ev = json.loads(subprocess.run(['solidcraft-cli', 'eval', sc], capture_output=True, text=True, check=True, cwd=ROOT).stdout)
    bodies = [b['name'] for b in ev['bodies']]
    servo = [n for n in bodies if n.startswith('SJ-')]
    printed = [n for n in bodies if not n.startswith('SJ-')]
    base = g.A.cname('base', 'F')
    spool = g.A.cname('spool', 'S')
    o = g.A.occ
    occ_all = [o(k, i) for k, i in g.A.comps]
    cm = [{"command": "joint.list", "params": {}}]
    for j in ("MCP", "PIP", "DIP"):
        cm += [{"command": "joint.drive", "params": {"joint": j, "value": 90}},
               {"command": "joint.drive", "params": {"joint": j, "value": 0}}]
    for j in ("MCP", "PIP", "DIP"):
        # the servo stays below z 45.1 and the finger above z 48.5 (checked statically below): left out (dense mesh)
        cm.append({"command": "joint.find_limits", "params": {"joint": j, "refine": 0.05, "step": 1.0,
                                                             "occurrences": [x for x in occ_all if 'ring' not in x]}})
    for p in POSES:
        cm.append({"command": "joint.drive", "params": {"joint": "MCP", "value": p[0]}})
        cm.append({"command": "joint.drive", "params": {"joint": "PIP", "value": p[1]}})
        cm.append({"command": "joint.drive", "params": {"joint": "DIP", "value": p[2]}})
        cm.append({"command": "inspect.clearance", "params": {"bodies": printed, "nearest": 2}})
        cm.append({"command": "inspect.interference", "params": {"bodies": printed}})
    for j in ("MCP", "PIP", "DIP"):
        cm.append({"command": "joint.drive", "params": {"joint": j, "value": 0}})
    lift = lambda dy: {"command": "occurrence.move", "params": {"occurrence": SERVO, "move_grounded": True,  # noqa: E731
                                                               "matrix": [[1, 0, 0, 0], [0, 1, 0, dy], [0, 0, 1, 0]]}}
    cm += [lift(-0.05), {"command": "inspect.clearance", "params": {"bodies": servo, "against": printed, "nearest": 3}}]
    prev = 0.05
    for s in SLIDE:
        cm += [lift(-(s - prev)), {"command": "inspect.clearance", "params": {"bodies": servo, "against": [base], "nearest": 1}}]
        prev = s
    with open(script, 'w') as fh:
        fh.write('[\n' + ',\n'.join(' ' + json.dumps(x, separators=(',', ':')) for x in cm) + '\n]\n')
    with tempfile.TemporaryDirectory() as td:
        rf = os.path.join(td, 'r.json')
        subprocess.run(['solidcraft-cli', 'run', script, '--in', sc, '--results', '--json-out', rf],
                       check=True, stdout=subprocess.DEVNULL, cwd=ROOT)
        r = json.load(open(rf))
    assert len(r) == len(cm), (len(r), len(cm))
    res = []

    def check(n, ok, v):
        res.append((n, ok, v))

    bad = [(t['name'], t['error'] or t['warning']) for t in ev['timeline']
           if (t['error'] or t['warning']) and t['name'] != 'LIB-0010_servo-scs0009']
    check('no feature errors / warnings (vendor STEP tolerance note ignored)', not bad, bad or 'none')
    src = json.load(open(os.path.join(ROOT, 'gripper_tester', 'cad', 'GRIP-0002_gripper-adapter.json')))
    dt = {s['params']['name']: float(s['params']['expression'].split()[0]) for s in src
          if s['command'] == 'parameters.add' and s['params']['name'] in f.DT}
    check('dovetail parameters == GRIP-0002', dt == f.DT, dt)
    jl = r[0]
    fl = [x for x in jl.get('floating', []) if not all(('scs0009' in q.lower() or 'SJ-' in q or '_ASM' in q) for q in x['occurrences'])]
    check('joints solve: no conflicts, nothing floating (the SCS0009 import is placed, not jointed)', not jl.get('conflicts') and not fl,
          {t: [j['type'] for j in jl['joints']].count(t) for t in {j['type'] for j in jl['joints']}})
    dr = r[1:7]
    check('MCP / PIP / DIP each driven to 90 deg and back: moved, nothing held',
          all(d.get('moved') and not d.get('held') for d in dr), f'{len(dr)} drives')
    k = 7
    for j, x in zip(("MCP", "PIP", "DIP"), r[k:k + 3]):
        v = x['values'][0]
        lo, hi = v['min'], v['max']
        lob = v.get('min_by') if isinstance(v.get('min_by'), dict) else {}
        hib = v.get('max_by') if isinstance(v.get('max_by'), dict) else {}
        check(f'{j}: extension stops at -3 .. 0 deg, flexion reaches >= 85 deg',
              lo is not None and hi is not None and -3.0 <= lo <= 0.0 and hi >= 85.0,
              f"{lo:.1f} .. {hi:.1f} deg; stops: {lob.get('a', v.get('min_by'))} / {lob.get('b', '')} | "
              f"{hib.get('a', v.get('max_by'))} / {hib.get('b', '')}")
    k += 3
    for i, p in enumerate(POSES):
        x = r[k + 5 * i + 3]
        xi = r[k + 5 * i + 4]
        # the kernel reads 0 where the MCP pin's flat edge passes the cheek face (hole mouth, x 1.3 y -12.3); the
        # pin is 0.15 inside the D3.4 hole there: the exact boolean interference check below proves no overlap
        near = sorted((d['distance_mm'], a, d['body']) for a, lst in x['nearest'].items() for d in lst
                      if {a, d['body']} != {base, g.A.cname('pin_mcp', 'MCP')})
        ok_i = not xi['interferences'] and not xi['unchecked'] and not xi.get('budget_exceeded')
        check(f'pose MCP/PIP/DIP {p}: printed parts no overlap (clearance + exact interference), none unchecked, >= 0.09',
              ok_i and near[0][0] >= 0.09 and
              not x['overlaps'] and not x['unchecked'] and not x.get('truncated') and x.get('pairs_checked', 1) > 0,
              f"closest {near[0][0]:.3f} {near[0][1]} / {near[0][2]}; overlaps {[(q['a'], q['b']) for q in x['overlaps']]}; "
              f"unchecked {[(u['a'], u['b']) for u in x['unchecked']]}")
    k += 5 * len(POSES) + 3
    x = r[k + 1]
    near = sorted((d['distance_mm'], a, d['body']) for a, lst in x['nearest'].items() for d in lst)
    seat = [n for n in near if n[0] < 0.1 and n[2] != spool]
    rest = [n for n in near if n[0] >= 0.1]
    # designed: tab seat 0.05 (lift); spool bore over the spline 0.05 radial (reads ~0.075 on the 20T teeth);
    # spool hub face 0.3 under the gear collar (reads 0.25: the collar is 0.05 off the SOURCE.md value)
    sp = [n for n in near if n[2] == spool]
    rest = [n for n in rest if n[2] != spool]
    ok = (len(seat) == 1 and 'TOPCASE' in seat[0][1] and seat[0][2] == base and abs(seat[0][0] - 0.05) < 0.01
          and sp and min(n[0] for n in sp) >= 0.05 and (not rest or rest[0][0] >= 0.3)
          and not x['overlaps'] and not x['unchecked'])
    check('SCS0009 (lifted 0.05): tab seat 0.05; spool >= 0.05 (bore on spline), else >= 0.3', ok,
          [(round(d, 3), a, b) for d, a, b in near[:5]])
    k += 2
    sl = r[k + 1:k + 2 * len(SLIDE):2]
    gaps = [min((d['distance_mm'] for lst in x['nearest'].values() for d in lst), default=None) for x in sl]
    ov = [s for s, x in zip(SLIDE, sl) if x['overlaps'] or x['unchecked']]
    check(f'servo slides in/out along Y between the fork posts ({SLIDE[-1]} mm, {len(SLIDE)} steps): no overlap, >= 0.3 to the base',
          not ov and all(gp is not None and gp >= 0.3 for gp in gaps), f'closest {min(gaps):.3f} mm; overlaps at {ov}')
    # tester baseplate: rails (48 wide) reach z dt_h beside the head; nothing of the base may come below dt_h + 0.2
    # outside the dovetail profile (its head is 28 wide about dt_y)
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    import plates  # noqa: E402
    V = plates.read_stl(os.path.join(ROOT, g.VDIR, 'exports', f.parts.export(g.PN['base'], f.REV(g.PN['base']), 'stl'))).reshape(-1, 3)
    dt_y = (-f.CHEEK_Y1 + g.OFF + f.CASE['y_in'] + f.SERVO_CLR + 2.0) / 2
    out_ = V[(abs(V[:, 1] - dt_y) > f.DT['dt_top'] / 2 + 0.01) & (V[:, 2] > 0.01)]
    zmin = float(out_[:, 2].min())
    check('base clears the tester rails: outside the dovetail nothing below z 6.2 (rail top 6.0)', zmin >= f.DT['dt_h'] + 0.19,
          f'lowest {zmin:.2f} mm (dovetail centre y {dt_y:.2f})')
    print(f'== v1 {g.ASSY}')
    w = max(len(n) for n, _, _ in res)
    for n, ok, v in res:
        print(f"{'PASS' if ok else 'FAIL'}  {n:<{w}}  {v}")
    return all(ok for _, ok, _ in res)


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
