"""Check the v3 variants (GRIP-9004 pivot jaws, GRIP-9005 twin-leg jaws, GRIP-9006 rigid nose).

    python3 strandbeest_gripper/tools/verify_v3.py [a|b|c ...]     (from the repo root; default all)

For each variant it writes cad/<PN>.verify.json and runs it on <PN>.sc:
full-turn drive, joint-centre traces against jansen.py, jaw / nose behaviour,
static gear-mesh clearance over one tooth pitch + full turn, and collision sweeps that
together cover every pair of printed parts. The design files are not changed.
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
import gen_v3 as v3  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
N = 181
DRIVE = list(range(30, 361, 30))


def link(p):
    nx, ny = math.cos(g.ROT), math.sin(g.ROT)
    return ((p[0] - g.A[0]) * nx + (p[1] - g.A[1]) * ny, -(p[0] - g.A[0]) * ny + (p[1] - g.A[1]) * nx)


def theta(k):
    return 360.0 * k / (N - 1)


def run(key):
    v = v3.VARIANTS[key]()
    g.build(v)                                  # sets PN / PARTS for this variant
    sc = os.path.join(ROOT, v.out.replace('.json', '.sc'))
    script = os.path.join(ROOT, v.out.replace('.json', '.verify.json'))
    printed = [g.occ(k, f) for k, f in g.PARTS]
    # v4a: printed pins and caps are checked on their own (they touch the links they hold by design:
    # no washers), the v4 sweeps run on the v4 parts as before
    pins = [o for o in printed if '_pin-' in o or '_snap-pin-' in o or '_cap-' in o]
    printed = [o for o in printed if o not in pins]
    gears = [g.comp_name('crank1', 1), g.comp_name('idler', 1), g.comp_name('idler', 2), g.comp_name('crank2', 1)]
    meshes = [(gears[0], gears[1]), (gears[1], gears[2]), (gears[2], gears[3])]
    DJ, DK = v.drive                            # joint you turn, its degrees per crank degree
    if key in ('h', 'p', 's', '5', '6'):
        gears.append(g.comp_name('wheel', 1))
        meshes.append((gears[0], gears[-1]))
    links = {f: [g.occ(k, f) for k in g.LINK_KEYS] for f in (1, 2)}
    traces = []                                 # (label, occurrence, point, reference(theta) -> link-frame point)
    for f in (1, 2):
        for n, k in (('J2', 'j'), ('J4', 'c'), ('F', 'ghi')):
            z = g.zb(g.LAYER[k]) + 1

            def ref(t, n=n, f=f):
                p = pose(math.radians(t), g.S)[n]
                return p if f == 1 else g.mir(p)
            traces.append((f"{n} finger {f}", g.occ(k, f), list(g.J[f][n]) + [z], ref))
    jaw_pts = {}
    sweeps = [(['gears'], [g.occ('frame', 1)], 'gears vs frame')]
    if key in ('a', 'h', 'p', 's'):
        for f in (1, 2):
            o = g.occ('jawp', f)
            tip = g.W(v3.lk(g.JL[f]['F'], v.JAW_L))
            jaw_pts[f] = [(o, list(g.J[f]['F']) + [v3.JAW_Z0 + 4]), (o, list(tip) + [v3.JAW_Z0 + 4])]
        sweeps.append(([g.occ('jawp', 1), g.occ('jawp', 2)], printed, 'jaws vs all parts'))
    if key in ('b', '5', '6'):
        xb = [g.comp_name('idlerX', 1), g.comp_name('crankB', 1), g.comp_name('idlerX', 2), g.comp_name('crankB', 2)]
        gears += xb
        # by name: v5 has the thumb wheel in the list too, so positions would shift
        if key == '6':      # mirrored leg B: driven from the Z33 idler through idler X
            meshes += [(g.comp_name('idler', 1), xb[0]), (xb[0], xb[1]), (g.comp_name('idler', 2), xb[2]), (xb[2], xb[3])]
        else:
            meshes += [(g.comp_name('crank1', 1), xb[0]), (xb[0], xb[1]), (g.comp_name('crank2', 1), xb[2]), (xb[2], xb[3])]
        nameB = (lambda k, f: v.legB_name(k, f)) if hasattr(v, 'legB_name') else (lambda k, f: f"{g.parts.fname(g.pn(k, f))}_F{f}B")
        printed += [f"{nameB(k, f)}:1" for f in (1, 2) for k in g.LINK_KEYS]
        for f in (1, 2):
            links[f'{f}B'] = [f"{nameB(k, f)}:1" for k in g.LINK_KEYS]
            o = g.occ('jawt', f)
            if key == '6':
                tip = (g.J[f]['F'][0] + v.UW[0] * v.JAW_OVER, g.J[f]['F'][1] + v.UW[1] * v.JAW_OVER)
            else:
                tip = g.W(v3.lk(v.JBL[f]['F'], v.OVERHANG))
            jaw_pts[f] = [(o, list(g.J[f]['F']) + [v3.JAW_Z0 + 4]), (o, list(tip) + [v3.JAW_Z0 + 4])]

            def refB(t, f=f):
                p = pose(math.radians(t), g.S)['F']
                p = (2 * v.XM - p[0], p[1]) if key == '6' else v3.lk(p, v3.TWIN_D)
                return p if f == 1 else g.mir(p)
            traces.append((f"F leg B finger {f}", f"{nameB('ghi', f)}:1",
                           list(v.JB[f]['F']) + [g.zb(g.LAYER['ghi']) + 1], refB))
        sweeps.append(([g.occ('jawt', 1), g.occ('jawt', 2)], printed, 'jaws vs all parts'))
    for lk, occs in links.items():
        sweeps.append((occs, printed, f'links {lk} vs all parts'))
    gear_occ = [x + ':1' for x in gears]
    sweeps = [(gear_occ if o == ['gears'] else o, a, lab) for o, a, lab in sweeps]
    # joint.sweep's gap report has a work budget: gears (dense tooth meshes) go in chunks of 2,
    # other parts in chunks of 8
    chunked = []
    for o, a, lab in sweeps:
        a = [x for x in a if x not in o] or a
        gs = [x for x in a if x in gear_occ]
        rest = [x for x in a if x not in gear_occ]
        for grp, n in ((gs, 2), (rest, 4 if len(printed) > 25 else 8)):   # big assemblies: smaller chunks
            for k in range(0, len(grp), n):
                chunked.append((o, grp[k:k + n], lab))
    sweeps = chunked
    pitch = 360.0 / g.ZC
    mesh_angles = [float(a) for a in range(0, int(round(pitch)) + 1)] + [float(a) for a in range(30, 360, 10)]   # one tooth pitch fine + full turn coarse (hubs over gear tips)

    c = [{"command": "joint.list", "params": {}}]
    c += [{"command": "joint.drive", "params": {"joint": DJ, "value": a * DK}} for a in DRIVE]
    c.append({"command": "joint.drive", "params": {"joint": DJ, "value": 0}})
    allpts = [(lab, o, p) for lab, o, p, _ in traces] + [(f"jaw{f}_{i}", o, p) for f in jaw_pts for i, (o, p) in enumerate(jaw_pts[f])]
    for lab, o, p in allpts:
        c.append({"command": "motion.trace", "params": {"occurrence": o, "point": [round(x, 4) for x in p],
                                                        "joint": DJ, "from": 0, "to": 360 * DK, "samples": N}})
    for a in mesh_angles:
        c.append({"command": "joint.drive", "params": {"joint": DJ, "value": a * DK}})
        c.append({"command": "inspect.clearance", "params": {"bodies": sorted({m[0] for m in meshes}),
                                                            "against": sorted({m[1] for m in meshes}), "nearest": 3}})
    c.append({"command": "joint.drive", "params": {"joint": DJ, "value": 0}})
    for occs, against, lab in sweeps:
        c.append({"command": "joint.sweep", "params": {"joint": DJ, "from": 0, "to": 360 * DK, "step": 2 * abs(DK),
                                                       "occurrences": occs, "against": against, "report_gaps": True}})
    pin_angles = [float(a) for a in range(0, 360, 30)] if pins else []
    for a in pin_angles:
        c.append({"command": "joint.drive", "params": {"joint": DJ, "value": a * DK}})
        c.append({"command": "inspect.clearance", "params": {"bodies": [o[:-2] for o in pins],
                                                            "against": [o[:-2] for o in printed], "nearest": 1}})
    npin = 2 * len(pin_angles)
    with open(script, 'w') as fh:
        fh.write('[\n' + ',\n'.join(' ' + json.dumps(x, separators=(',', ':')) for x in c) + '\n]\n')
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, 'r.json')
        subprocess.run(['solidcraft-cli', 'run', script, '--in', sc, '--results', '--json-out', out],
                       check=True, stdout=subprocess.DEVNULL, cwd=ROOT)
        r = json.load(open(out))
    assert len(r) == 2 + len(DRIVE) + len(allpts) + 2 * len(mesh_angles) + 1 + len(sweeps) + npin, len(r)
    rp = r[len(r) - npin:]
    r = r[:len(r) - npin]

    res = []

    def check(name, ok, value):
        res.append((name, ok, value))

    jl = r[0]
    check('joints solve: no conflicts, nothing floating', not jl.get('conflicts') and not jl.get('floating'),
          {t: [j['type'] for j in jl['joints']].count(t) for t in {j['type'] for j in jl['joints']}})
    drives = r[1:1 + len(DRIVE)]
    check(f'full crank turn driven by {DJ}: every 30 deg step moved, nothing held',
          all(d.get('moved') and not d.get('held') and not d.get('stopped_by_loop') for d in drives), f'{len(drives)} steps')
    i = 2 + len(DRIVE)
    tr = {}
    worst = 0.0
    for (lab, o, p, ref), x in zip(traces, r[i:i + len(traces)]):
        P = x['points']
        assert len(P) == N, (lab, len(P))
        tr[lab] = P
        for k, pt in enumerate(P):
            q = g.W(ref(theta(k)))
            worst = max(worst, math.hypot(pt[0] - q[0], pt[1] - q[1]))
    check(f'{len(traces)} joint traces match jansen.py (<= 0.05 mm)', worst <= 0.05, f'{worst:.4f} mm')
    i += len(traces)
    jt = {}
    for (lab, o, p), x in zip(allpts[len(traces):], r[i:i + len(allpts) - len(traces)]):
        jt[lab] = [link(q) for q in x['points']]
    i += len(allpts) - len(traces)
    F1 = [link(q) for q in tr['F finger 1']]
    F2 = [link(q) for q in tr['F finger 2']]

    if key in ('a', 'b', 'h', 'p', 's', '5', '6'):
        for f in (1, 2):
            a0, a1 = jt[f'jaw{f}_0'], jt[f'jaw{f}_1']
            ang = [math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) for a, b in zip(a0, a1)]
            ang = [ang[0] + ((x - ang[0] + 180) % 360 - 180) for x in ang]      # unwrap (jaws point along -x: +-180)
            spread = max(ang) - min(ang)
            check(f'jaw {f} keeps its orientation over the full turn (<= 0.05 deg)', spread <= 0.05, f'{spread:.4f} deg')
        # inner faces: jaw width JAW_W centred on the F-tip line -> gap = distance between the lines - JAW_W
        gap_root = [abs(a[1] - b[1]) - v3.JAW_W for a, b in zip(jt['jaw1_0'], jt['jaw2_0'])]
        gap_tip = [abs(a[1] - b[1]) - v3.JAW_W for a, b in zip(jt['jaw1_1'], jt['jaw2_1'])]
        L = math.hypot(jt['jaw1_1'][0][0] - jt['jaw1_0'][0][0], jt['jaw1_1'][0][1] - jt['jaw1_0'][0][1])
        check(f'jaw faces parallel: gap at root == gap at tip ({L:.0f} mm apart) (<= 0.05 mm)',
              max(abs(a - b) for a, b in zip(gap_root, gap_tip)) <= 0.05, f'max diff {max(abs(a - b) for a, b in zip(gap_root, gap_tip)):.4f} mm')
        check(f'jaw clamp gap {g.CLAMP_GAP:.2f} +- 0.1 mm, open >= 15 mm', abs(min(gap_root) - g.CLAMP_GAP) <= 0.1 and max(gap_root) >= 15,
              f'{min(gap_root):.2f} .. {max(gap_root):.2f} mm')
        clamp = [k for k, gp in enumerate(gap_root) if gp <= min(gap_root) + 0.4]
        xs = [jt['jaw1_0'][k][0] for k in clamp]
        check('feed stroke while clamped >= 19.5 mm', max(xs) - min(xs) >= 19.5, f'{max(xs) - min(xs):.1f} mm')
        if key in ('a', 'h', 'p', 's'):
            # pivot angle needed between jaw and foot over the turn (real part: jaw free on its pin)
            fa = []
            for k in range(N):
                p = pose(math.radians(theta(k)), g.S)
                fa.append(math.degrees(math.atan2(p['F'][1] - p['J4'][1], p['F'][0] - p['J4'][0])))
            rel = [x - fa[0] for x in fa]
            clamp_rel = [rel[k] for k in clamp]
            check('info: jaw-to-foot pivot angle needed', True,
                  f'clamp window {min(clamp_rel):+.1f}..{max(clamp_rel):+.1f} deg, full turn {min(rel):+.1f}..{max(rel):+.1f} deg')
        if key == '6':
            FB1 = [link(q) for q in tr['F leg B finger 1']]
            dy = max(abs(b[1] - a[1]) for a, b in zip(F1, FB1))
            dx = max(abs(a[0] + b[0] - 2 * v.XM) for a, b in zip(F1, FB1))
            sl = [b[0] - a[0] for a, b in zip(F1, FB1)]
            check('mirrored leg B: foot B height == foot A height, x mirrored (<= 0.05 mm)', dy <= 0.05 and dx <= 0.05,
                  f'height diff {dy:.4f} mm, mirror error {dx:.4f} mm')
            check(f'foot B stays inside the jaw slot ({v.d_slot[0] - 0.5:.1f}..{v.d_slot[1] + 0.5:.1f} mm from foot A)',
                  min(sl) >= v.d_slot[0] - 0.5 - 1e-6 and max(sl) <= v.d_slot[1] + 0.5 + 1e-6,
                  f'{min(sl):.1f}..{max(sl):.1f} mm')
        if key in ('b', '5'):
            FB1 = [link(q) for q in tr['F leg B finger 1']]
            dd = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(F1, FB1)]
            check(f'leg B foot = leg A foot + {v3.TWIN_D:.0f} mm (slot travel <= 0.05 mm)',
                  max(abs(x - v3.TWIN_D) for x in dd) <= 0.05, f'{min(dd):.3f}..{max(dd):.3f} mm')
    if key == 'c':
        gaps = [gp for _, gp in v.gaps(v.inset)]
        clampF = [math.hypot(a[0] - b[0], a[1] - b[1]) - g.PAD_D for a, b in zip(F1, F2)]
        cw = [k for k, gp in enumerate(clampF) if gp <= min(clampF) + 0.4]
        ts = [int(round(theta(k))) % 360 for k in cw]
        ng = [gaps[t] for t in ts]
        check(f'noses never collide (analytic, full turn, >= {v.MIN_GAP} mm)', min(gaps) >= v.MIN_GAP - 1e-6, f'min {min(gaps):.2f} mm')
        tipg = []
        for t in ts:
            n1 = v.nose_tip(pose(math.radians(t), g.S), v.inset)
            tipg.append(math.hypot(n1[0] - g.mir(n1)[0], n1[1] - g.mir(n1)[1]) - 2 * v.NOSE_R)
        check('info: nose TIP gap during the clamp window (pads at their minimum)', True,
              f'{min(tipg):.2f}..{max(tipg):.2f} mm vs pads {min(clampF):.2f} mm')

    clear = r[i + 1:i + 2 * len(mesh_angles):2]
    worst = {m: 1e9 for m in meshes}
    overl = []
    for x in clear:
        overl += [(o['a'], o['b']) for o in x.get('overlaps', [])]
        for b, near in (x.get('nearest') or {}).items():
            for nb in near:
                for m in meshes:
                    if {b, nb['body']} == set(m):
                        worst[m] = min(worst[m], nb['distance_mm'])
    for m, d in worst.items():
        check(f'mesh {m[0]} / {m[1]}: no overlap, >= 0.1 mm over one tooth pitch + full turn',
              not any({a, b} == set(m) for a, b in overl) and 0.1 <= d < 1e9, f'{d:.3f} mm')
    agg = {}
    for (occs, against, lab), x in zip(sweeps, r[-len(sweeps):]):
        a = agg.setdefault(lab, {'stop': None, 'mg': []})
        a['stop'] = a['stop'] or x['stopped_by']
        a['mg'] += [(vv['mm'], kk, vv.get('to')) for kk, vv in (x.get('min_gap') or {}).items()]
    for lab, a in agg.items():
        mg = sorted(a['mg'])
        check(f'{lab}: no contact over a full turn, closest >= 0.49 mm',
              a['stop'] is None and bool(mg) and mg[0][0] >= 0.49,
              f'{mg[0][0]:.3f} mm {mg[0][1]} - {mg[0][2]}' if mg else a['stop'])
    if pins:
        pc = rp[1::2]
        ov = [(o['a'], o['b'], o.get('volume_mm3', o.get('volume'))) for x in pc for o in x.get('overlaps', [])]
        # intended press fit: the J1 shoulder pin's tip in its crank gear (D2.7 tip in the D2.5 hole)
        press = math.pi / 4 * (2.7 ** 2 - 2.5 ** 2) * (g.GEAR_T - 0.5) + 0.05
        crank_names = ('gear-crank',)
        def intended(o):
            return ('pin-j1-shoulder' in o[0] + o[1] and any(k in o[0] + o[1] for k in crank_names)
                    and o[2] is not None and o[2] <= press)
        bad = [o for o in ov if (o[2] is None or o[2] > 0.001) and not intended(o)]
        unchecked = [(u['a'], u['b']) for x in pc for u in (x.get('unchecked') or [])]
        unchecked_bad = [u for u in unchecked if not ('pin-j1-shoulder' in u[0] + u[1] and 'gear-crank' in u[0] + u[1])]
        dists = [nb['distance_mm'] for x in pc for near in (x.get('nearest') or {}).values() for nb in near]
        check(f'{len(pins)} printed pins + caps vs all parts at {len(pin_angles)} crank angles: no overlap '
              '(touching the links they hold is expected: no washers)',
              len(pc) == len(pin_angles) and all(x.get('pairs_checked', 0) > 0 for x in pc) and not bad and not unchecked_bad,
              f"{min(x.get('pairs_checked', 0) for x in pc)}+ pairs per angle, {len(bad)} overlaps" + (f' e.g. {bad[0]}' if bad else '')
              + f"; J1 press fits: {len([o for o in ov if intended(o)])} measured <= {press:.2f} mm3, "
              f"{len(unchecked) - len(unchecked_bad)} unchecked by the kernel; other unchecked {len(unchecked_bad)}")
    print(f'== v3{key} {v.assy_pn}')
    w = max(len(n) for n, _, _ in res)
    for n, ok, val in res:
        print(f"{'PASS' if ok else 'FAIL'}  {n:<{w}}  {val}")
    return all(ok for _, ok, _ in res)


if __name__ == '__main__':
    check_reference()
    oks = [run(k) for k in (sys.argv[1:] or ['a', 'b', 'c', 'h'])]
    sys.exit(0 if all(oks) else 1)
