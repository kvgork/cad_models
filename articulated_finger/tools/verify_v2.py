"""Check v2 (GRIP-9021, rod + crossed links finger) in SolidCraft.   python3 articulated_finger/tools/verify_v2.py

Writes cad/GRIP-9021_assy-finger-rod-fourbar.verify.json and runs it on the built .sc:
  - no feature errors (vendor STEP note ignored); dovetail parameters == GRIP-0002;
  - joints solve (the SCS0009 import is placed, not jointed); the horn alone drives the finger: driven over its
    stroke in 10 steps every joint moved and MCP / PIP / DIP match fingerlinks.py within 0.5 deg;
  - range of the horn to first contact (joint.find_limits, every printed part, the finger linkage following):
    it reaches the full stroke; straight end within 3 deg of horn 0 (extension stop);
  - printed parts vs printed parts at 4 horn angles: clearance + exact interference, nothing unchecked;
  - SCS0009 (lifted 0.05): tab seat 0.05, horn bore on the spline >= 0.05, else >= 0.3; the servo slides in
    along +Y between the fork posts with the horn off; the dummy servo fills the pocket with 0.1 per side.
"""
import json
import math
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import finger_common as f  # noqa: E402
import fingerlinks as fl  # noqa: E402
import gen_v2 as g  # noqa: E402

ROOT = f.ROOT
SERVO = "LIB-0010_servo-scs0009:1"
SLIDE = list(range(2, 51, 2))


def main():
    g.build()
    out = f"{g.VDIR}/cad/{f.parts.fname(g.ASSY)}"
    sc, script = os.path.join(ROOT, out + '.sc'), os.path.join(ROOT, out + '.verify.json')
    ev = json.loads(subprocess.run(['solidcraft-cli', 'eval', sc], capture_output=True, text=True, check=True, cwd=ROOT).stdout)
    bodies = [b['name'] for b in ev['bodies']]
    servo = [n for n in bodies if n.startswith('SJ-')]
    dummy = g.A.cname('dummy', 'X')
    printed = [n for n in bodies if not n.startswith('SJ-') and n != dummy]
    base, horn = g.A.cname('base', 'F'), g.A.cname('horn', 'S')
    o = g.A.occ
    occ_all = [o(k, i) for k, i in g.A.comps if k != 'dummy']
    stroke = fl.sweep()[-1][0]
    steps = [stroke * k / 10 for k in range(1, 11)]
    poses = [0.0, stroke / 3, 2 * stroke / 3, stroke]
    cm = [{"command": "joint.list", "params": {}}]
    for a in steps:
        cm += [{"command": "joint.drive", "params": {"joint": "HORN", "value": round(a, 4)}},
               {"command": "joint.list", "params": {}}]
    cm.append({"command": "joint.drive", "params": {"joint": "HORN", "value": 0}})
    cm.append({"command": "joint.find_limits", "params": {"joint": "HORN", "refine": 0.05, "step": 1.0, "occurrences": occ_all}})
    for a in poses:
        cm += [{"command": "joint.drive", "params": {"joint": "HORN", "value": round(a, 4)}},
               {"command": "inspect.clearance", "params": {"bodies": printed, "nearest": 2}},
               {"command": "inspect.interference", "params": {"bodies": printed}}]
    cm.append({"command": "joint.drive", "params": {"joint": "HORN", "value": 0}})
    lift = lambda dy: {"command": "occurrence.move", "params": {"occurrence": SERVO, "move_grounded": True,  # noqa: E731
                                                               "matrix": [[1, 0, 0, 0], [0, 1, 0, dy], [0, 0, 1, 0]]}}
    cm += [lift(-0.05), {"command": "inspect.clearance", "params": {"bodies": servo, "against": printed, "nearest": 3}}]
    prev = 0.05
    for s in SLIDE:
        cm += [lift(-(s - prev)), {"command": "inspect.clearance", "params": {"bodies": servo, "against": [base], "nearest": 1}}]
        prev = s
    # dummy servo: park it in the pocket (it is built 60 mm +X of it) and check its fit against the base
    cm += [{"command": "joint.delete", "params": {"joint": f"fix_{g.A.cname('dummy', 'X')}"}},
           {"command": "occurrence.move", "params": {"occurrence": o('dummy', 'X'), "move_grounded": True,
                                                     "matrix": [[1, 0, 0, -60.0], [0, 1, 0, 0], [0, 0, 1, 0]]}},
           {"command": "inspect.clearance", "params": {"bodies": [dummy], "against": [base, horn], "nearest": 3}},
           {"command": "inspect.interference", "params": {"bodies": [dummy, base, horn]}}]
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
    fl_ = [x for x in jl.get('floating', []) if not all(('scs0009' in q.lower() or 'SJ-' in q or '_ASM' in q) for q in x['occurrences'])]
    check('joints solve: no conflicts, nothing floating (the SCS0009 import is placed, not jointed)',
          not jl.get('conflicts') and not fl_,
          {t: [j['type'] for j in jl['joints']].count(t) for t in {j['type'] for j in jl['joints']}})
    dr = list(zip(r[1:1 + 2 * len(steps):2], r[2:2 + 2 * len(steps):2]))
    err, worst, moved = 0.0, None, True
    guess = (0.0, 0.0, 0.0)
    ends = None
    for a, (d, jl2) in zip(steps, dr):
        moved &= bool(d.get('moved')) and not d.get('held') and not d.get('stopped_by_loop')
        v = {j['name']: j['values'][0]['value'] for j in jl2['joints'] if j['name'] in ('MCP', 'PIP', 'DIP')}
        m = fl.solve(a, guess)
        guess = m
        for j, t in zip(("MCP", "PIP", "DIP"), m):
            e = abs(v[j] - math.degrees(t))
            if e > err:
                err, worst = e, (round(a, 1), j, round(v[j], 2), round(math.degrees(t), 2))
        ends = v
    check(f'horn driven 0 .. {stroke:.1f} deg (10 steps): moved, nothing held; MCP / PIP / DIP == fingerlinks.py (<= 0.5 deg)',
          moved and err <= 0.5, f"max err {err:.3f} deg {worst}; end MCP {ends['MCP']:.1f} PIP {ends['PIP']:.1f} DIP {ends['DIP']:.1f}")
    k = 2 + 2 * len(steps)
    v = r[k]['values'][0]
    lo, hi = v['min'], v['max']
    mb = lambda x: f"{x.get('a')} / {x.get('b')}" if isinstance(x, dict) else x  # noqa: E731
    check(f'horn range to first contact (all printed parts, linkage following): reaches {stroke:.1f}, stops within 3 deg below 0',
          lo is not None and hi is not None and -3.0 <= lo <= 0.0 and hi >= stroke,
          f"{lo:.1f} .. {hi:.1f} deg; stops {mb(v.get('min_by'))} | {mb(v.get('max_by'))}")
    k += 1
    for i, a in enumerate(poses):
        x, xi = r[k + 3 * i + 1], r[k + 3 * i + 2]
        # as in v1: the kernel reads 0 where the MCP pin's flat edge passes the cheek face (hole mouth); the pin is
        # 0.15 inside its D3.4 hole there, and the exact boolean interference check (same pose) finds nothing
        near = sorted((d['distance_mm'], aa, d['body']) for aa, lst in x['nearest'].items() for d in lst
                      if {aa, d['body']} != {base, g.A.cname('pin_mcp', 'MCP')})
        ok_i = not xi['interferences'] and not xi['unchecked'] and not xi.get('budget_exceeded')
        check(f'horn {a:.0f} deg: printed parts no overlap (clearance + exact interference), none unchecked, >= 0.09',
              ok_i and not x['overlaps'] and not x['unchecked'] and not x.get('truncated') and near[0][0] >= 0.09,
              f"closest {near[0][0]:.3f} {near[0][1]} / {near[0][2]}; overlaps {[(q['a'], q['b']) for q in x['overlaps']]}; "
              f"unchecked {[(u['a'], u['b']) for u in x['unchecked']]}; interference {xi.get('count')}")
    k += 3 * len(poses) + 1
    x = r[k + 1]
    near = sorted((d['distance_mm'], a, d['body']) for a, lst in x['nearest'].items() for d in lst)
    seat = [n for n in near if n[0] < 0.1 and n[2] != horn]
    hn = [n for n in near if n[2] == horn]
    rest = [n for n in near if n[0] >= 0.1 and n[2] != horn]
    ok = (len(seat) == 1 and 'TOPCASE' in seat[0][1] and seat[0][2] == base and abs(seat[0][0] - 0.05) < 0.01
          and hn and min(n[0] for n in hn) >= 0.05 and (not rest or rest[0][0] >= 0.3) and not x['overlaps'] and not x['unchecked'])
    check('SCS0009 (lifted 0.05): tab seat 0.05; horn >= 0.05 (bore on spline, face 0.3 off the collar), else >= 0.3', ok,
          [(round(d, 3), a, b) for d, a, b in near[:5]])
    k += 2
    sl = r[k + 1:k + 2 * len(SLIDE):2]
    gaps = [min((d['distance_mm'] for lst in y['nearest'].values() for d in lst), default=None) for y in sl]
    ov = [s for s, y in zip(SLIDE, sl) if y['overlaps'] or y['unchecked']]
    check(f'servo slides in/out along Y between the fork posts, horn off ({SLIDE[-1]} mm, {len(SLIDE)} steps): no overlap, >= 0.3 to the base',
          not ov and all(gp is not None and gp >= 0.3 for gp in gaps), f'closest {min(gaps):.3f} mm; overlaps at {ov}')
    k += 2 * len(SLIDE)
    x, xi = r[k + 2], r[k + 3]
    # the kernel reads 0 at the pocket mouth (cradle face y = OFF, case corner x -6.45 z 40.85), where the dummy is
    # 0.1 inside the pocket walls by construction; the exact interference check proves there is no overlap
    near = sorted((d['distance_mm'], a, d['body']) for a, lst in x['nearest'].items() for d in lst)
    hb = [n for n in near if n[2] == horn]
    ok = (not x['overlaps'] and not x['unchecked'] and not xi['interferences'] and not xi['unchecked']
          and hb and hb[0][0] >= 0.15)
    check('dummy servo in the pocket (0.1 per side; mouth-edge 0 reading exempted): exact interference none, '
          'stub in the horn bore >= 0.15', ok, [(round(d, 3), a, b) for d, a, b in near[:4]] + [f"interference {xi.get('count')}"])
    print(f'== v2 {g.ASSY}')
    w = max(len(n) for n, _, _ in res)
    for n, ok, v in res:
        print(f"{'PASS' if ok else 'FAIL'}  {n:<{w}}  {v}")
    return all(ok for _, ok, _ in res)


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
