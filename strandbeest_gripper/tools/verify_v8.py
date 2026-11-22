"""Check v8 (GRIP-9016, four-bar legs) in SolidCraft against the analytic model fourbar.py.

    python3 strandbeest_gripper/tools/verify_v8.py          (from the repo root; after building the .sc)

Writes cad/GRIP-9016_assy-four-bar.verify.json and runs it on the built .sc:
  - joints solve; a full crank turn driven from O_A1 really moves (every 30 deg step);
  - J1 / B / P of all 4 legs traced over the turn and compared with fourbar.py (shifted / mirrored);
  - jaws: orientation constant, faces parallel, clamp gap, opening, feed stroke while clamped,
    leg-B pin inside its 2 mm jaw slot;
  - the 5 gear meshes: static clearance over one crank tooth pitch (1 deg) + full turn (15 deg);
  - collision sweeps over a full turn (moving parts vs everything they can reach, pins left out);
  - pins, crank shafts and knob vs all parts at 12 crank angles: no overlap except the intended press
    fits (B / P pins in the coupler), and no pair the kernel could not check.
"""
import json
import math
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fourbar as fb  # noqa: E402
import gen_v8 as g  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
N = 121
DRIVE = list(range(30, 361, 30))
STEP = 3.0
MIN_GAP = 0.45            # rocker vs top-plate O stub is 0.48 by design (fourbar fit, rockO)


def theta(k):
    return 360.0 * k / (N - 1)


def main():
    g.build()
    out = f"{g.VDIR}/cad/{g.parts.fname(g.ASSY)}"
    sc, script = os.path.join(ROOT, out + '.sc'), os.path.join(ROOT, out + '.verify.json')
    occ = lambda key, i: g.occ(key, i)                                   # noqa: E731
    crank = {leg: occ(('crank', leg), leg) for leg in g.LEGS}
    idl = {f: occ('idler', f'X{f}') for f in (1, 2)}
    coup = {leg: occ('coupler', leg) for leg in g.LEGS}
    rock = {leg: occ('rocker', leg) for leg in g.LEGS}
    jaw = {f: occ('jaw', f'F{f}') for f in (1, 2)}
    frame, plate = occ('frame', 'F'), occ('plate', 'F')
    small = [occ(k, i) for k, i in g.COMPS if k in ('pin_q', 'pin_b', 'pin_p', 'pin_x', 'shaft', 'shaft_knob', 'knob')]
    big = [occ(k, i) for k, i in g.COMPS if occ(k, i) not in small]
    gears = list(crank.values()) + list(idl.values())
    meshes = [(crank['A1'], idl[1]), (idl[1], crank['B1']), (idl[1], idl[2]), (idl[2], crank['A2']), (idl[2], crank['B2'])]
    # traces
    traces = []
    for leg in g.LEGS:
        j = g.JP[leg]
        for n, o, z in (('J1', coup[leg], g.Z_L1 + 1), ('B', rock[leg], g.Z_L2 + 1), ('P', coup[leg], g.Z_L1 + 1)):
            traces.append((f'{n} {leg}', o, list(j[n]) + [z], leg, n))
    jaw_pts = {f: [(jaw[f], list(g.JP[f'A{f}']['P']) + [g.Z_L2 + 4]),
                   (jaw[f], [g.JP[f'B{f}']['P'][0] + g.L_FREE - 3, g.JP[f'B{f}']['P'][1], g.Z_L2 + 4])] for f in (1, 2)}
    # sweeps (moving part, against), chunked; designed close pairs left out (checked statically below):
    # coupler ring on its own crank's boss (0.15 per side), rocker eye on its frame journal (0.15 per side)
    # v8b: the idler turns on a frame post (0.15 per side): a designed close pair, checked statically below
    sweeps = [([x], [plate] if (g.VARIANT == 'b' and x in idl.values()) else [frame, plate], 'gears vs frame + top plate')
              for x in gears]
    for leg in g.LEGS:
        sweeps.append(([coup[leg]], [o for o in big if o not in (coup[leg], crank[leg])], f'coupler {leg} vs all (not its crank)'))
        sweeps.append(([rock[leg]], [o for o in big if o not in (rock[leg], frame)], f'rocker {leg} vs all (not the frame)'))
    for f in (1, 2):
        sweeps.append(([jaw[f]], [o for o in big if o != jaw[f]], f'jaw {f} vs all'))
    chunked = []
    for o, a, lab in sweeps:
        gs = [x for x in a if x in gears]
        rest = [x for x in a if x not in gears]
        for grp, n in ((gs, 2), (rest, 6)):
            for k in range(0, len(grp), n):
                chunked.append((o, grp[k:k + n], lab))
    pitch = 360.0 / g.ZC
    mesh_angles = [float(a) for a in range(0, int(math.ceil(pitch)) + 1)] + [float(a) for a in range(15, 360, 15)]
    small_angles = [float(a) for a in range(0, 360, 30)]

    c = [{"command": "joint.list", "params": {}}]
    c += [{"command": "joint.drive", "params": {"joint": "O_A1", "value": a}} for a in DRIVE]
    c.append({"command": "joint.drive", "params": {"joint": "O_A1", "value": 0}})
    allpts = [(lab, o, p) for lab, o, p, _, _ in traces] + [(f"jaw{f}_{i}", o, p) for f in jaw_pts for i, (o, p) in enumerate(jaw_pts[f])]
    for lab, o, p in allpts:
        c.append({"command": "motion.trace", "params": {"occurrence": o, "point": [round(x, 4) for x in p],
                                                        "joint": "O_A1", "from": 0, "to": 360, "samples": N}})
    names = lambda L: sorted({x[:-2] for x in L})                         # noqa: E731
    for a in mesh_angles:
        c.append({"command": "joint.drive", "params": {"joint": "O_A1", "value": a}})
        c.append({"command": "inspect.clearance", "params": {"bodies": names([m[0] for m in meshes]),
                                                            "against": names([m[1] for m in meshes]), "nearest": 4}})
    c.append({"command": "joint.drive", "params": {"joint": "O_A1", "value": 0}})
    for occs, against, lab in chunked:
        c.append({"command": "joint.sweep", "params": {"joint": "O_A1", "from": 0, "to": 360, "step": STEP,
                                                       "occurrences": occs, "against": against, "report_gaps": True}})
    for a in small_angles:
        c.append({"command": "joint.drive", "params": {"joint": "O_A1", "value": a}})
        c.append({"command": "inspect.clearance", "params": {"bodies": names(small), "against": names(big + small), "nearest": 1}})
        c.append({"command": "inspect.clearance", "params": {"bodies": names(list(coup.values()) + list(rock.values())
                                                                     + (list(idl.values()) if g.VARIANT == 'b' else [])),
                                                            "against": names(list(crank.values()) + [frame]), "nearest": 1}})
    with open(script, 'w') as fh:
        fh.write('[\n' + ',\n'.join(' ' + json.dumps(x, separators=(',', ':')) for x in c) + '\n]\n')
    with tempfile.TemporaryDirectory() as td:
        res_file = os.path.join(td, 'r.json')
        subprocess.run(['solidcraft-cli', 'run', script, '--in', sc, '--results', '--json-out', res_file],
                       check=True, stdout=subprocess.DEVNULL, cwd=ROOT)
        r = json.load(open(res_file))
    nsmall = 3 * len(small_angles)
    assert len(r) == 2 + len(DRIVE) + len(allpts) + 2 * len(mesh_angles) + 1 + len(chunked) + nsmall, len(r)
    rs, r = r[len(r) - nsmall:], r[:len(r) - nsmall]

    res = []

    def check(name, ok, value):
        res.append((name, ok, value))

    jl = r[0]
    check('joints solve: no conflicts, nothing floating', not jl.get('conflicts') and not jl.get('floating'),
          {t: [j['type'] for j in jl['joints']].count(t) for t in {j['type'] for j in jl['joints']}})
    drives = r[1:1 + len(DRIVE)]
    check('full crank turn driven by O_A1: every 30 deg step moved, nothing held',
          len(drives) == len(DRIVE) and all(d.get('moved') and not d.get('held') and not d.get('stopped_by_loop') for d in drives),
          f'{len(drives)} steps')
    i = 2 + len(DRIVE)
    tr = {}
    errs = {1: 0.0, -1: 0.0}
    for (lab, o, p, leg, n), x in zip(traces, r[i:i + len(traces)]):
        P = x['points']
        assert len(P) == N, (lab, len(P))
        tr[lab] = P
        for sgn in (1, -1):
            for k, pt in enumerate(P):
                q = g.leg_pts(leg, fb.pose(math.radians(sgn * theta(k))))[n]
                errs[sgn] = max(errs[sgn], math.hypot(pt[0] - q[0], pt[1] - q[1]))
    sgn = min(errs, key=errs.get)
    check(f'{len(traces)} joint traces (J1, B, P of 4 legs) match fourbar.py (<= 0.01 mm)', errs[sgn] <= 0.01,
          f"{errs[sgn]:.5f} mm (crank turns {'CCW' if sgn > 0 else 'CW'} for +O_A1)")
    i += len(traces)
    jt = {}
    for (lab, o, p), x in zip(allpts[len(traces):], r[i:i + len(allpts) - len(traces)]):
        assert len(x['points']) == N, lab
        jt[lab] = x['points']
    i += len(allpts) - len(traces)
    for f in (1, 2):
        ang = [math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) for a, b in zip(jt[f'jaw{f}_0'], jt[f'jaw{f}_1'])]
        check(f'jaw {f} keeps its orientation over the full turn (<= 0.02 deg)', max(ang) - min(ang) <= 0.02,
              f'{max(ang) - min(ang):.4f} deg')
    gap_root = [abs(a[1] - b[1]) - g.JAW_W for a, b in zip(jt['jaw1_0'], jt['jaw2_0'])]
    gap_tip = [abs(a[1] - b[1]) - g.JAW_W for a, b in zip(jt['jaw1_1'], jt['jaw2_1'])]
    L = jt['jaw1_1'][0][0] - jt['jaw1_0'][0][0]
    dmax = max(abs(a - b) for a, b in zip(gap_root, gap_tip))
    check(f'jaw faces parallel: gap at the pin == gap near the tip ({L:.0f} mm apart) (<= 0.02 mm)', dmax <= 0.02, f'max diff {dmax:.4f} mm')
    check(f'clamp gap {g.CLAMP_GAP:.2f} +- 0.05 mm, open >= 19 mm', abs(min(gap_root) - g.CLAMP_GAP) <= 0.05 and max(gap_root) >= 19,
          f'{min(gap_root):.2f} .. {max(gap_root):.2f} mm (v7: 1.53 .. 19.50)')
    clamp = [k for k, gp in enumerate(gap_root) if gp <= min(gap_root) + 0.4]
    xs = [jt['jaw1_0'][k][0] for k in clamp]
    check('feed stroke while clamped (gap within +0.4) >= 19.5 mm', max(xs) - min(xs) >= 19.5, f'{max(xs) - min(xs):.1f} mm (v7 19.9)')
    sl = [b[0] - a[0] - g.D for a, b in zip(tr['P A1'], tr['P B1'])]
    sl2 = [b[0] - a[0] - g.D for a, b in zip(tr['P A2'], tr['P B2'])]
    check(f'leg-B pin stays centred in its {g.JAW_SLOT:.0f} mm jaw slot (<= 0.05 mm)', max(map(abs, sl + sl2)) <= 0.05,
          f'{max(map(abs, sl + sl2)):.4f} mm')

    clear = r[i + 1:i + 2 * len(mesh_angles):2]
    worst = {m: 1e9 for m in meshes}
    overl = []
    for x in clear:
        overl += [(o['a'], o['b']) for o in x.get('overlaps', [])]
        for b, near in (x.get('nearest') or {}).items():
            for nb in near:
                for m in meshes:
                    if {b, nb['body']} == {m[0][:-2], m[1][:-2]}:
                        worst[m] = min(worst[m], nb['distance_mm'])
    for m, d in worst.items():
        check(f'mesh {m[0][:-2]} / {m[1][:-2]}: no overlap, >= 0.1 mm over one pitch + full turn',
              not any({a, b} == {m[0][:-2], m[1][:-2]} for a, b in overl) and 0.1 <= d < 1e9, f'{d:.3f} mm')
    agg = {}
    for (occs, against, lab), x in zip(chunked, r[-len(chunked):]):
        a = agg.setdefault(lab, {'stop': None, 'mg': []})
        a['stop'] = a['stop'] or x.get('stopped_by')
        a['mg'] += [(vv['mm'], kk, vv.get('to')) for kk, vv in (x.get('min_gap') or {}).items()]
    for lab, a in agg.items():
        mg = sorted(a['mg'])
        check(f'{lab}: no contact over a full turn, closest >= {MIN_GAP} mm', a['stop'] is None and bool(mg) and mg[0][0] >= MIN_GAP,
              f'{mg[0][0]:.3f} mm to {mg[0][2]}' if mg else a['stop'])
    pc = rs[1::3]
    cp = rs[2::3]
    press = 0.0   # X3 coupler: Ø3.1 pin in a Ø3.2 hole, drawn loose, so no overlap is allowed (X2 had 0.05 interference)

    def intended(a, b, vol):
        ab = a + b
        return ('pin-press-head' in ab and 'coupler-eccentric' in ab and a.split('_')[-1] == b.split('_')[-1]
                and vol is not None and vol <= press)
    ov = [(o['a'], o['b'], o.get('volume_mm3', o.get('volume'))) for x in pc for o in x.get('overlaps', [])]
    bad = [o for o in ov if (o[2] is None or o[2] > 0.001) and not intended(*o)]
    unchecked = [(u['a'], u['b']) for x in pc for u in (x.get('unchecked') or [])]
    unchecked_bad = [u for u in unchecked if not ('pin-press-head' in u[0] + u[1] and 'coupler' in u[0] + u[1])]
    check(f'{len(small)} pins / shafts / knob vs all parts at {len(small_angles)} crank angles: no overlap '
          '(X3: B / P pins drawn loose in the couplers); only pin-in-coupler pairs may be unchecked',
          len(pc) == len(small_angles) and all(x.get('pairs_checked', 0) > 0 for x in pc) and not bad and not unchecked_bad,
          f"{min(x.get('pairs_checked', 0) for x in pc)}+ pairs per angle, {len(bad)} overlaps" + (f' e.g. {bad[0]}' if bad else '')
          + f"; press fits measured {len([o for o in ov if intended(*o)])} (<= {press:.2f} mm3), unchecked by the kernel "
          f"{len(unchecked) - len(unchecked_bad)}; other unchecked {len(unchecked_bad)}" + (f' e.g. {unchecked_bad[0]}' if unchecked_bad else ''))
    ovc = [(o['a'], o['b'], o.get('volume_mm3', o.get('volume'))) for x in cp for o in x.get('overlaps', [])]
    ovc = [o for o in ovc if o[2] is None or o[2] > 0.001]
    unc = [(u['a'], u['b']) for x in cp for u in (x.get('unchecked') or [])]
    gaps = [nb['distance_mm'] for x in cp for near in (x.get('nearest') or {}).values() for nb in near]
    check('close pairs left out of the sweeps (coupler ring on its boss, rocker eye on its journal' + (', idler on its frame post' if g.VARIANT == 'b' else '') + ') at '
          f'{len(small_angles)} crank angles: no overlap, none unchecked',
          len(cp) == len(small_angles) and all(x.get('pairs_checked', 0) > 0 for x in cp) and not ovc and not unc,
          f"{min(x.get('pairs_checked', 0) for x in cp)}+ pairs per angle, {len(ovc)} overlaps, {len(unc)} unchecked, "
          f"closest {min(gaps):.3f} mm (ring / journal play 0.15, thrust faces touch)")
    print(f'== v8 {g.ASSY}')
    w = max(len(n) for n, _, _ in res)
    for n, ok, val in res:
        print(f"{'PASS' if ok else 'FAIL'}  {n:<{w}}  {val}")
    return all(ok for _, ok, _ in res)


if __name__ == '__main__':
    fb.check_against_jansen()
    sys.exit(0 if main() else 1)
