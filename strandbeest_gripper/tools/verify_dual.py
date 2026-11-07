"""Check Strandbeest gripper v2 (GRIP-9003, two mirrored fingers) against its acceptance criteria.

    python3 strandbeest_gripper/tools/verify_dual.py      (from the repo root)

Writes cad/GRIP-9003.verify.json (generated from gen_dual.py) and runs it on
GRIP-9003.sc: full-turn drive, joint-centre traces of both fingers against
jansen.py, collision sweep of every printed part over a full turn, clamp gap and
feed stroke. The design file is not changed.
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
import gen_dual as g  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SC = os.path.join(ROOT, g.Variant().out.replace('.json', '.sc'))
SCRIPT = os.path.join(ROOT, g.Variant().out.replace('.json', '.verify.json'))

N = 181                                   # trace samples over 0..360
TRACE = [(f, n, key, z) for f in (1, 2) for n, key, z in
         (('J2', 'j', g.zb(g.LAYER['j']) + 1), ('J3', 'f', g.zb(g.LAYER['f']) + 1),
          ('J4', 'c', g.zb(g.LAYER['c']) + 1), ('J5', 'f', g.zb(g.LAYER['f']) + 1),
          ('F', 'ghi', g.zb(g.LAYER['ghi']) + 1))]
DRIVE = list(range(30, 361, 30))
PRINTED = [g.occ(k, f) for k, f in g.PARTS]
GEARS = [g.occ('crank1', 1), g.occ('idler', 1), g.occ('idler', 2), g.occ('crank2', 1)]
LINKS = {f: [g.occ(k, f) for k in ('j', 'k', 'c', 'f', 'bde', 'ghi')] for f in (1, 2)}
# Swept checks: together with the mesh checks below they cover every pair of printed parts.
SWEEPS = [(GEARS, [g.occ('frame', 1)], 360, 1), (LINKS[1], PRINTED, 360, 2), (LINKS[2], PRINTED, 360, 2)]
LABELS = ('gears vs frame', 'finger 1 links vs all parts', 'finger 2 links vs all parts')
# Gear meshes: joint.sweep exceeds its collision budget on the dense tooth meshes, so the meshes are
# checked statically (inspect.clearance) at every degree of one tooth pitch of the crank gear (the
# mesh pattern repeats every pitch).
PITCH = 360.0 / g.ZC
MESH_ANGLES = [float(a) for a in range(0, int(round(PITCH)) + 1)] + [float(a) for a in range(30, 360, 10)]   # one pitch fine + full turn coarse
GEAR_BODIES = [g.comp_name('crank1', 1), g.comp_name('idler', 1), g.comp_name('idler', 2), g.comp_name('crank2', 1)]
MESHES = [(GEAR_BODIES[0], GEAR_BODIES[1]), (GEAR_BODIES[1], GEAR_BODIES[2]), (GEAR_BODIES[2], GEAR_BODIES[3])]


def verify_script():
    c = [{"command": "joint.list", "params": {}}]
    c += [{"command": "joint.drive", "params": {"joint": "O1_crank", "value": v}} for v in DRIVE]
    c.append({"command": "joint.drive", "params": {"joint": "O1_crank", "value": 0}})
    c.append({"command": "motion.trace", "params": {"occurrence": g.occ('crank2', 1), "point": list(g.J[2]['J1']) + [g.HORN_TOP + 3],
                                                    "joint": "O1_crank", "from": 0, "to": 360, "samples": N}})
    for f, n, key, z in TRACE:
        c.append({"command": "motion.trace", "params": {"occurrence": g.occ(key, f), "point": list(g.J[f][n]) + [z],
                                                        "joint": "O1_crank", "from": 0, "to": 360, "samples": N}})
    for a in MESH_ANGLES:
        c.append({"command": "joint.drive", "params": {"joint": "O1_crank", "value": a}})
        c.append({"command": "inspect.clearance", "params": {"bodies": [GEAR_BODIES[0], GEAR_BODIES[2]],
                                                            "against": [GEAR_BODIES[1], GEAR_BODIES[3]], "nearest": 2}})
    c.append({"command": "joint.drive", "params": {"joint": "O1_crank", "value": 0}})
    for occs, against, to, step in SWEEPS:
        c.append({"command": "joint.sweep", "params": {"joint": "O1_crank", "from": 0, "to": to, "step": step,
                                                       "occurrences": occs, "against": against, "report_gaps": True}})
    return c


def main():
    check_reference()
    with open(SCRIPT, 'w') as fh:
        fh.write('[\n' + ',\n'.join(' ' + json.dumps(x, separators=(',', ':')) for x in verify_script()) + '\n]\n')
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, 'r.json')
        subprocess.run(['solidcraft-cli', 'run', SCRIPT, '--in', SC, '--results', '--json-out', out],
                       check=True, stdout=subprocess.DEVNULL, cwd=ROOT)
        r = json.load(open(out))
    assert len(r) == 1 + len(DRIVE) + 1 + 1 + len(TRACE) + 2 * len(MESH_ANGLES) + 1 + len(SWEEPS), f'unexpected result count {len(r)}'
    res = []

    def check(name, ok, value):
        res.append((name, ok, value))

    jl = r[0]
    types = [j['type'] for j in jl['joints']]
    check('22 revolute joints + 3 gear links, no conflicts, nothing floating',
          types.count('revolute') == 22 and len(jl.get('links', [])) == 3 and not jl.get('conflicts') and not jl.get('floating'),
          f"{types.count('revolute')} revolute, {len(jl.get('links', []))} links")
    drives = r[1:1 + len(DRIVE)]
    check('crank 1 full turn in 30 deg steps: every step moved, nothing held',
          all(d.get('moved') and not d.get('held') and not d.get('stopped_by_loop') for d in drives), f'{len(drives)} steps')
    i = 1 + len(DRIVE) + 1
    # crank 2 J1 must follow the mirror: link-frame angle -theta about O2
    P = r[i]['points']
    assert len(P) == N
    worst = 0.0
    for k, pt in enumerate(P):
        th = 360.0 * k / (N - 1)
        ref = g.W(g.mir(pose(math.radians(th), g.S)['J1']))
        worst = max(worst, math.hypot(pt[0] - ref[0], pt[1] - ref[1]))
    check('gear train: crank 2 turns 1:1 opposite (J1 of finger 2 <= 0.05 mm from mirror)', worst <= 0.05, f'{worst:.4f} mm')
    tr = {}
    worst = 0.0
    for (f, n, key, z), x in zip(TRACE, r[i + 1:i + 1 + len(TRACE)]):
        P = x['points']
        assert len(P) == N, (f, n, len(P))
        tr[(f, n)] = P
        for k, pt in enumerate(P):
            th = 360.0 * k / (N - 1)
            p = pose(math.radians(th), g.S)[n]
            ref = g.W(p if f == 1 else g.mir(p))
            worst = max(worst, math.hypot(pt[0] - ref[0], pt[1] - ref[1]))
    check('joint centres J2..J5, F of both fingers match jansen.py (<= 0.05 mm)', worst <= 0.05, f'{worst:.4f} mm')
    # clamp: pad gap and feed stroke (link frame of finger 1)
    nx, ny = math.cos(g.ROT), math.sin(g.ROT)

    def link(p):
        return ((p[0] - g.A[0]) * nx + (p[1] - g.A[1]) * ny, -(p[0] - g.A[0]) * ny + (p[1] - g.A[1]) * nx)

    F1 = [link(p) for p in tr[(1, 'F')]]
    F2 = [link(p) for p in tr[(2, 'F')]]
    gaps = [math.hypot(a[0] - b[0], a[1] - b[1]) - g.PAD_D for a, b in zip(F1, F2)]
    gmin, gmax = min(gaps), max(gaps)
    check(f'pads clamp: min pad-to-pad gap {g.CLAMP_GAP:.2f} +- 0.1 mm (pad_d {g.PAD_D:.0f})', abs(gmin - g.CLAMP_GAP) <= 0.1, f'{gmin:.2f} mm')
    check('pads open: max gap >= 15 mm (lift ~9 mm per foot)', gmax >= 15, f'{gmax:.2f} mm')
    clamp = [k for k, gp in enumerate(gaps) if gp <= gmin + 0.4]
    xs = [F1[k][0] for k in clamp]
    stroke = max(xs) - min(xs)
    same = max(abs(F1[k][0] - F2[k][0]) for k in range(N))
    check('feed stroke while clamped (gap within 0.4 mm of min) >= 19.5 mm', stroke >= 19.5,
          f'{stroke:.1f} mm over {len(clamp) * 2} deg of crank')
    check('both pads move together along x (max x difference <= 0.05 mm)', same <= 0.05, f'{same:.4f} mm')
    k0 = 1 + len(DRIVE) + 1 + 1 + len(TRACE)
    clear = r[k0 + 1:k0 + 2 * len(MESH_ANGLES):2]
    worst = {m: 1e9 for m in MESHES}
    overl = []
    for x in clear:
        overl += [(o['a'], o['b'], round(o['volume_mm3'], 3)) for o in x.get('overlaps', [])]
        for b, near in (x.get('nearest') or {}).items():
            for nb in near:
                for m in MESHES:
                    if {b, nb['body']} == set(m):
                        worst[m] = min(worst[m], nb['distance_mm'])
    for m, d in worst.items():
        check(f'mesh {m[0]} / {m[1]}: no overlap, min clearance >= 0.1 mm over one tooth pitch + full turn ({len(MESH_ANGLES)} poses)',
              not any({a, b} == set(m) for a, b, _ in overl) and 0.1 <= d < 1e9, f'{d:.3f} mm')
    for x, lab in zip(r[-len(SWEEPS):], LABELS):
        mg = sorted((v['mm'], k, v.get('to')) for k, v in (x.get('min_gap') or {}).items())
        lim = 0.49
        check(f'{lab}: no contact, closest approach >= {lim} mm', x['stopped_by'] is None and bool(mg) and mg[0][0] >= lim,
              f'{mg[0][0]:.3f} mm {mg[0][1]} - {mg[0][2]} (tol {x.get("gap_tolerance_mm", 0):.3f})' if mg else x['stopped_by'])
    w = max(len(n) for n, _, _ in res)
    for n, ok, v in res:
        print(f"{'PASS' if ok else 'FAIL'}  {n:<{w}}  {v}")
    return all(ok for _, ok, _ in res)


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
