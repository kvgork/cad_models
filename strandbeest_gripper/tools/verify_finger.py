"""Run cad/GRIP-9002.verify.json on GRIP-9002.sc and check the v1 acceptance criteria.

    python3 strandbeest_gripper/tools/verify_finger.py      (from the repo root)

The verify script drives the crank, traces the joint centres, sweeps for
collisions and probes the hard stops (it clears the crank limits on a copy;
the design file is not changed).
"""
import json
import math
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from jansen import pose, check_reference  # noqa: E402
import gen_finger as g  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SC = os.path.join(ROOT, g.VDIR, 'cad', g.parts.fname('GRIP-9002') + '.sc')
SCRIPT = os.path.join(ROOT, g.VDIR, 'cad', g.parts.fname('GRIP-9002') + '.verify.json')

res = []


def check(name, ok, value):
    res.append((name, ok, value))


TRACE = {'J2': ('j', 30.2), 'J3': ('bde', 26.7), 'J4': ('c', 30.2), 'J5': ('f', 30.2), 'F': ('ghi', 40.0)}
DRIVE = [g.THETA_MIN, -40, -20, 0, 20, 40, g.THETA_MAX, 0]
LINKS = [f"{g.CN[k]}:1" for k in ('j', 'k', 'c', 'f', 'bde', 'ghi')]
ALL = [f"{g.CN[k]}:1" for k in ('frame', 'crank', 'j', 'k', 'c', 'f', 'bde', 'ghi')]   # servo left out: links never go below z 25.2 > servo top 20.2


def verify_script():
    c = [{"command": "joint.list", "params": {}}]
    c += [{"command": "joint.drive", "params": {"joint": "O_crank", "value": v}} for v in DRIVE]
    for n, (k, z) in TRACE.items():
        c.append({"command": "motion.trace", "params": {"occurrence": f"{g.CN[k]}:1", "point": [g.J[n][0], g.J[n][1], z],
                                                        "joint": "O_crank", "from": g.THETA_MIN, "to": g.THETA_MAX, "samples": 130}})
    rng = dict(joint="O_crank", **{"from": g.THETA_MIN, "to": g.THETA_MAX}, step=1, report_gaps=True)
    c.append({"command": "joint.sweep", "params": dict(rng, occurrences=LINKS, against=ALL)})          # links vs everything
    c.append({"command": "joint.sweep", "params": dict(rng, occurrences=[ALL[1]], against=[ALL[0]])})  # crank vs frame
    c.append({"command": "joint.limits", "params": {"joint": "O_crank"}})                                # copy only
    c.append({"command": "joint.sweep", "params": {"joint": "O_crank", "from": g.THETA_MAX, "to": g.STOP_MAX + 4,
                                                   "step": 0.25, "occurrences": ALL}})
    c.append({"command": "joint.sweep", "params": {"joint": "O_crank", "from": g.THETA_MIN, "to": g.STOP_MIN - 4,
                                                   "step": 0.25, "occurrences": ALL}})
    return c


if __name__ == '__main__':
    with open(SCRIPT, 'w') as fh:
        fh.write('[\n' + ',\n'.join(' ' + json.dumps(x, separators=(',', ':')) for x in verify_script()) + '\n]\n')
    check_reference()
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, 'r.json')
        subprocess.run(['solidcraft-cli', 'run', SCRIPT, '--in', SC, '--results', '--json-out', out],
                       check=True, stdout=subprocess.DEVNULL, cwd=ROOT)
        r = json.load(open(out))

    assert len(r) == 1 + len(DRIVE) + len(TRACE) + 5, f'unexpected result count {len(r)}'
    jl = r[0]
    nrev = [j['type'] for j in jl['joints']].count('revolute')
    check('10 revolute joints, no conflicts, nothing floating',
          nrev == 10 and not jl.get('conflicts') and not jl.get('floating'), f'{nrev} revolute')
    drives = r[1:1 + len(DRIVE)]
    check('crank drive -63..+66: every step moved, nothing held',
          all(d.get('moved') and not d.get('held') and not d.get('stopped_by_loop') for d in drives),
          [d['values'][0]['value'] for d in drives])
    worst = 0.0
    traces = r[1 + len(DRIVE):1 + len(DRIVE) + len(TRACE)]
    for n, x in zip(TRACE, traces):
        P = x['points']
        assert len(P) == 130, (n, len(P))
        for i, pt in enumerate(P):
            th = g.THETA_MIN + (g.THETA_MAX - g.THETA_MIN) * i / (len(P) - 1)
            ref = g.W(pose(math.radians(th), g.S)[n])
            worst = max(worst, math.hypot(pt[0] - ref[0], pt[1] - ref[1]))
    check('joint centres J2..J5, F match jansen.py (<= 0.05 mm)', worst <= 0.05, f'{worst:.4f} mm')
    P = traces[-1]['points']
    nx, ny = math.cos(g.ROT), math.sin(g.ROT)
    lx = [(p[0] - g.A[0]) * nx + (p[1] - g.A[1]) * ny for p in P]
    ly = [-(p[0] - g.A[0]) * ny + (p[1] - g.A[1]) * nx for p in P]
    check('tip travel >= 19.5 mm', max(lx) - min(lx) >= 19.5, f'{max(lx) - min(lx):.2f} mm')
    check('tip straightness <= 0.25 mm', max(ly) - min(ly) <= 0.25, f'{max(ly) - min(ly):.3f} mm')
    pad = g.P0  # noqa
    gap0, gap1 = -lx[0] - 5.0, -lx[-1] - 5.0
    check('grip opening at -63 = 21.0 +- 0.3 mm', abs(gap0 - 21.0) <= 0.3, f'{gap0:.2f} mm')
    check('grip opening at +66 = 1.3 +- 0.3 mm', abs(gap1 - 1.3) <= 0.3, f'{gap1:.2f} mm')
    sw = [x for x in r if isinstance(x, dict) and 'stopped_by' in x]
    assert len(sw) == 4, len(sw)
    links_sw, crank_sw, pos, neg = sw
    check('collision sweep -63..+66 (links vs all parts): no contact',
          links_sw['stopped_by'] is None and not links_sw['touching_at_start'], links_sw['stopped_by'])
    lg = min(v['mm'] for v in links_sw['min_gap'].values())
    check('every link >= 0.49 mm from every other part (washer gap)', lg >= 0.49, f'{lg:.3f} mm')
    check('crank vs frame over -63..+66: no contact', crank_sw['stopped_by'] is None, crank_sw['stopped_by'])
    fc = min(v['mm'] for v in crank_sw['min_gap'].values())
    check('crank-to-frame min gap >= 0.3 mm (stop tab approaching at -63)', fc >= 0.3,
          f"{fc:.3f} mm (mesh tolerance {links_sw['gap_tolerance_mm']:.3f})")
    main = links_sw
    tol_deg = math.degrees(main['gap_tolerance_mm'] / 11.5)
    for lab, x, want in (('+', pos, g.STOP_MAX), ('-', neg, g.STOP_MIN)):
        hit = x['stopped_by'] and {x['stopped_by']['a'], x['stopped_by']['b']} == {g.CN['frame'] + ':1', g.CN['crank'] + ':1'}
        check(f'hard stop {lab}: crank tab hits frame post at {want:+.2f} deg (+- 0.25 + mesh {tol_deg:.2f})',
              bool(hit) and abs(x['stopped_at'] - want) <= 0.25 + tol_deg, f"{x['stopped_at']:+.2f} deg")

    w = max(len(n) for n, _, _ in res)
    for n, ok, v in res:
        print(f"{'PASS' if ok else 'FAIL'}  {n:<{w}}  {v}")
    sys.exit(0 if all(ok for _, ok, _ in res) else 1)
