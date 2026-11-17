"""Verify finray_tests v2 (GRIP-9017, parallel module mounted), its pull-module check variant, and v2b
(GRIP-9018, C-socket roots): joints, knob-driven motion and range, rack/pinion mesh, collision sweeps over the
stroke, static fits (no overlap, no pair left unchecked by the kernel) and finger gaps.

    python3 finray_tests/tools/verify_finray_v2.py [parallel] [pull] [csocket]    (default: all three)

The committed variants are read from their built .sc; the pull variant is generated and built in a temporary
folder (no exports). What a rigid CAD model can't show: the fin ray bending. In the pull variant the finger is
held rigid on the bracket, so the inner pin moving inside its boss is expected and left out of the sweeps.
"""
import json
import math
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_finray_v2 as v  # noqa: E402
import gen_finray as g  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
K = 360.0          # knob degrees per mm of S_A (screw pitch 1 mm)


class Script:
    def __init__(self):
        self.c, self.tags = [], {}

    def add(self, cmd, tag=None, **p):
        if tag:
            self.tags.setdefault(tag, []).append(len(self.c))
        self.c.append({"command": cmd, "params": p})


def run(script, sc, keep):
    with tempfile.TemporaryDirectory() as td:
        sp = keep or os.path.join(td, 's.json')
        with open(sp, 'w') as fh:
            json.dump(script.c, fh, indent=0)
        out = os.path.join(td, 'r.json')
        subprocess.run(['solidcraft-cli', 'run', sp, '--in', sc, '--results', '--json-out', out],
                       check=True, stdout=subprocess.DEVNULL, cwd=ROOT)
        r = json.load(open(out))
    r = [x.get('result', x) if isinstance(x, dict) else x for x in r]
    assert len(r) == len(script.c), (len(r), len(script.c))
    return r


def names_of(mode):
    v.build(mode)
    return [n for n, _ in v.PARTS], [n for n, _, _ in v.PURCHASED]


def o(n):
    return f"{n}:1"


def nearest(res):
    return [nb['distance_mm'] for near in (res.get('nearest') or {}).values() for nb in near]


class Report:
    def __init__(self, title):
        self.title, self.rows, self.fails = title, [], 0

    def check(self, name, ok, value):
        self.rows.append(('PASS' if ok else 'FAIL', name, value))
        self.fails += not ok

    def show(self):
        print(f'== {self.title}')
        for s, n, val in self.rows:
            print(f"{s}  {n:100s} {val}")


def sweep_rows(rep, r, s, label_groups):
    for i, (label, _occ, _ag) in enumerate(label_groups):
        sw = r[s.tags['sweep'][i]]
        gaps = sw.get('min_gap') or {}
        mg = min(gaps.values(), key=lambda x: x['mm']) if gaps else None
        rep.check(f"stroke sweep: {label}: no collision", sw.get('stopped_by') in (None, 'limit') and sw.get('pairs', 0) > 0,
                  f"{sw.get('pairs')} pairs, stopped at {sw.get('stopped_at')} by "
                  f"{(sw.get('stopped_by') or {}).get('b', sw.get('stopped_by')) if isinstance(sw.get('stopped_by'), dict) else sw.get('stopped_by')}, touching at start "
                  f"{sw.get('touching_at_start')}, nearest {mg['mm']:.2f} mm" if mg else str(sw)[:200])


def static_rows(rep, r, s, tag, label, allow=()):
    res = [r[i] for i in s.tags[tag]]
    ov = [(x['a'], x['b'], round(x['volume_mm3'], 3)) for y in res for x in y.get('overlaps', [])
          if not any(a in x['a'] + x['b'] and b in x['a'] + x['b'] for a, b in allow)]
    unc = [(u['a'], u['b']) for y in res for u in (y.get('unchecked') or [])]
    d = [m for y in res for m in nearest(y)]
    rep.check(label, not ov and not unc and all(y.get('pairs_checked', 0) > 0 for y in res),
              f"{sum(y.get('pairs_checked', 0) for y in res)} pairs, {len(ov)} overlaps {ov[:2]}, {len(unc)} unchecked "
              f"{unc[:2]}, closest {min(d) if d else float('nan'):.2f} mm")


def drive_common(rep, r, s, ta_i, tb_i, xg_min):
    jl = r[s.tags['joints'][0]]
    rep.check("joints solve: no conflicts, nothing floating", not jl.get('conflicts') and not jl.get('floating'),
              f"{len(jl.get('joints', []))} joints, {len(jl.get('links', []))} motion links")
    ta, tb = r[ta_i]['points'], r[tb_i]['points']
    ok = len(ta) == len(tb) and len(ta) > 2 and r[ta_i].get('stopped_at') is None and r[tb_i].get('stopped_at') is None
    sym = max(abs(a[0] + b[0]) for a, b in zip(ta, tb)) if ok else 99
    rep.check("carriages move symmetrically about x = 0 over the stroke (<= 0.01 mm)", ok and sym <= 0.01,
              f"{len(ta)} samples, max |xA + xB| {sym:.4f} mm")
    return ta, tb


def mesh_rows(rep, r, s):
    res = [r[i] for i in s.tags['mesh']]
    over = sum(len(x.get('overlaps', [])) for x in res)
    d = [m for x in res for m in nearest(x)]
    rep.check("rack/pinion mesh: no overlap at 10 positions over a tooth pitch + stroke ends, gap >= 0.05 mm",
              over == 0 and d and min(d) >= 0.05, f"{over} overlaps, closest {min(d) if d else float('nan'):.3f} mm")


def mesh_steps(s, car_a, car_b, pin, lo, hi):
    for val in [lo + k * (math.pi / 6) for k in range(7)] + [0.0, hi - math.pi / 2, hi]:
        s.add("joint.drive", joint="R_knob", value=K * val)
        s.add("inspect.clearance", "mesh", bodies=[pin], against=[car_a, car_b], nearest=2)


# ----------------------------------------------------------------------------- parallel / csocket
def check_parallel(mode):
    names, bought = names_of(mode)
    vdir = v.VDIR[mode]
    sc = os.path.join(vdir, 'cad', os.path.basename(v.out_path(mode)).replace('.json', '.sc'))
    keep = os.path.join(ROOT, sc.replace('.sc', '.verify.json'))
    pick = lambda pre: [n for n in names + bought if n.startswith(pre)]  # noqa: E731
    car_a, car_b = pick('GRIP-0125')[0], pick('GRIP-0126')[0]
    pin, base = pick('GRIP-0055')[0], pick('GRIP-0124')[0]
    fpn, hpn = ('GRIP-0135', 'GRIP-0136') if mode == 'csocket' else ('GRIP-0133', 'GRIP-0127')
    f1, f2 = sorted(pick(fpn))
    h1, h2 = sorted(pick(hpn))
    pins = pick('GRIP-0134')
    pins1, pins2 = [p for p in pins if '_F1' in p], [p for p in pins if '_F2' in p]
    hd1, hd2 = pick('M3x8-ISO4762_hold1'), pick('M3x8-ISO4762_hold2')
    parked = [n for n in names if any(n.startswith(p) for p in ('GRIP-0128', 'GRIP-0129', 'GRIP-0130', 'GRIP-0131',
                                                                 'GRIP-0132'))] + pick('M3x8-ISO4762_br')
    xg_min = v.XG_MIN_C if mode == 'csocket' else v.XG_MIN
    lo, hi = v.XG0 - v.XG_MAX, v.XG0 - xg_min
    s = Script()
    s.add("joint.list", "joints")
    pa = [-(v.XG0 + g.CAR_L / 2), g.SCREW_Y, 25.0]
    pb = [v.XG0 + g.CAR_L / 2, g.SCREW_Y, 25.0]
    s.add("motion.trace", "ta", occurrence=o(car_a), point=pa, joint="R_knob", **{"from": K * lo, "to": K * hi}, samples=35)
    s.add("motion.trace", "tb", occurrence=o(car_b), point=pb, joint="R_knob", **{"from": K * lo, "to": K * hi}, samples=35)
    s.add("joint.drive", joint="R_knob", value=360)
    s.add("joint.list", "turn")
    s.add("joint.drive", joint="R_knob", value=0)
    left = [car_a, h1, f1] + pins1 + hd1
    right = [car_b, h2, f2] + pins2 + hd2
    groups = [("jaw A + holder + finger + pins vs base, jaw B side and the parked module", left, [base] + right + parked),
              ("jaw B + holder + finger + pins vs base and the parked module", right, [base] + parked)]
    for _l, occ, ag in groups:
        s.add("joint.sweep", "sweep", joint="R_knob", **{"from": K * lo, "to": K * hi}, step=K,
              occurrences=[o(n) for n in occ], against=[o(n) for n in ag], report_gaps=True)
    mesh_steps(s, car_a, car_b, pin, lo, hi)
    for val in (hi, lo):
        s.add("joint.drive", joint="R_knob", value=K * val)
        s.add("inspect.clearance", "gap", bodies=[f1], against=[f2], nearest=1)
        s.add("inspect.clearance", "hgap", bodies=[h1], against=[h2], nearest=1)
    s.add("joint.drive", joint="R_knob", value=0)
    s.add("inspect.clearance", "fit", bodies=[f1, f2] + pins, against=[h1, h2, car_a, car_b, base] + hd1 + hd2, nearest=1)
    s.add("inspect.clearance", "fit", bodies=[h1, h2], against=[car_a, car_b, base] + hd1 + hd2, nearest=1)
    hw = ["M6x70-ISO4017_F1", "M6-nyloc-DIN985_F1", "M6-nut-ISO4032_F1", pick('GRIP-0056')[0]]
    for val in (hi, lo):
        s.add("joint.drive", joint="R_knob", value=K * val)
        s.add("inspect.clearance", "hw", bodies=hw, against=[car_a, car_b, base, h1, h2], nearest=1)
    r = run(s, sc, keep)

    rep = Report(f"{vdir} {v.ASSY[mode][0]} ({mode})")
    ta, tb = drive_common(rep, r, s, s.tags['ta'][0], s.tags['tb'][0], xg_min)
    xg = [b[0] - g.CAR_L / 2 for b in tb]
    rep.check(f"grip-face range {xg_min:g} .. {v.XG_MAX:g} mm per side", abs(min(xg) - xg_min) < 0.01
              and abs(max(xg) - v.XG_MAX) < 0.01, f"{min(xg):.2f} .. {max(xg):.2f} mm")
    sa = [j for j in r[s.tags['turn'][0]].get('joints', []) if j.get('name') == 'S_A']
    val = sa[0]['values'][0]['value'] if sa else None
    rep.check("thumb screw: one knob turn moves jaw A 1.00 mm", val is not None and abs(abs(val) - 1.0) < 0.01, f"{val}")
    sweep_rows(rep, r, s, groups)
    mesh_rows(rep, r, s)
    gc, go = nearest(r[s.tags['gap'][0]]), nearest(r[s.tags['gap'][1]])
    # C-socket cylinders sit on the neck mid-lines, 1.6 mm proud of the grip face behind the root (closest points)
    proud = 2 * (v.CR - v.NECK / 2) if mode == 'csocket' else 0.0
    rep.check(f"grip faces closed {2 * xg_min:g} mm / open {2 * v.XG_MAX:g} mm apart (closest points"
              + (f" = root cylinders, {proud:.1f} mm less)" if proud else ")"),
              gc and go and abs(min(gc) - 2 * xg_min + proud) < 0.05 and abs(min(go) - 2 * v.XG_MAX + proud) < 0.05,
              f"{min(gc) if gc else None:.2f} / {min(go) if go else None:.2f} mm")
    hc = nearest(r[s.tags['hgap'][0]])
    rep.check("holders don't touch each other when closed (>= 0.5 mm)", hc and min(hc) >= 0.5, f"{min(hc) if hc else None:.2f} mm")
    static_rows(rep, r, s, 'fit', "fingers, pins, holders, carriages, base, M3 heads as built: no overlap, none unchecked")
    static_rows(rep, r, s, 'hw', "M6 screw, nyloc, nut and knob vs carriages, base, holders at both stroke ends: no overlap")
    rep.show()
    return rep.fails


# ----------------------------------------------------------------------------- pull
def check_pull():
    names, bought = names_of('pull')
    pick = lambda pre: [n for n in names + bought if n.startswith(pre)]  # noqa: E731
    car_a, car_b, base = pick('GRIP-0125')[0], pick('GRIP-0126')[0], pick('GRIP-0124')[0]
    br_l, br_r = pick('GRIP-0128')[0], pick('GRIP-0129')[0]
    s1, s2 = sorted(pick('GRIP-0130'))
    cam_l, cam_r = pick('GRIP-0131')[0], pick('GRIP-0132')[0]
    f1, f2 = sorted(pick('GRIP-0133'))
    pins = pick('GRIP-0134')
    pi1, po1 = [p for p in pins if p.endswith('_F1i')][0], [p for p in pins if p.endswith('_F1o')][0]
    pi2, po2 = [p for p in pins if p.endswith('_F2i')][0], [p for p in pins if p.endswith('_F2o')][0]
    brs = pick('M3x8-ISO4762_br')
    parked = pick('GRIP-0127') + pick('M3x8-ISO4762_hold')
    pmax = v.PULL_MAX
    with tempfile.TemporaryDirectory() as td:
        js = v.out_path('pull', td)
        v.write('pull', js)
        scp = os.path.join(td, 'pull.sc')
        subprocess.run(['solidcraft-cli', 'run', js, '--save', scp], check=True, stdout=subprocess.DEVNULL, cwd=ROOT)
        s = Script()
        s.add("joint.list", "joints")
        pa = [-(v.XG0 + g.CAR_L / 2), g.SCREW_Y, 25.0]
        pb = [v.XG0 + g.CAR_L / 2, g.SCREW_Y, 25.0]
        p1 = [-(v.XG0 + v.DRIVE[0]), v.DRIVE[1], v.CAP[1]]
        p2 = [v.XG0 + v.DRIVE[0], v.DRIVE[1], v.CAP[1]]
        rng = {"from": 0.0, "to": K * pmax}
        s.add("motion.trace", "ta", occurrence=o(car_a), point=pa, joint="R_knob", **rng, samples=13)
        s.add("motion.trace", "tb", occurrence=o(car_b), point=pb, joint="R_knob", **rng, samples=13)
        s.add("motion.trace", "s1", occurrence=o(s1), point=p1, joint="R_knob", **rng, samples=13)
        s.add("motion.trace", "s2", occurrence=o(s2), point=p2, joint="R_knob", **rng, samples=13)
        s.add("joint.drive", joint="R_knob", value=0)
        groups = [("carriage A + cam plate + slider (no inner pin) vs base, bracket, finger, outer pin, screws, B side",
                   [car_a, cam_l, s1], [base, br_l, f1, po1] + brs + [car_b, cam_r, s2, br_r]),
                  ("inner pin A vs base, bracket, cam plate, outer pin (not its finger: the finger bends there)",
                   [pi1], [base, br_l, cam_l, po1, car_a]),
                  ("carriage B + cam plate + slider (no inner pin) vs base, bracket, finger, outer pin, screws",
                   [car_b, cam_r, s2], [base, br_r, f2, po2] + brs),
                  ("inner pin B vs base, bracket, cam plate, outer pin", [pi2], [base, br_r, cam_r, po2, car_b]),
                  ("slider A (drive boss in the 45 deg slot) vs its cam plate and carriage", [s1], [cam_l, car_a]),
                  ("slider B (drive boss in the 45 deg slot) vs its cam plate and carriage", [s2], [cam_r, car_b])]
        for _l, occ, ag in groups:
            s.add("joint.sweep", "sweep", joint="R_knob", **rng, step=K / 2,
                  occurrences=[o(n) for n in occ], against=[o(n) for n in ag], report_gaps=True)
        s.add("joint.drive", joint="R_knob", value=0)
        everything = [n for n in names + bought if n not in parked]
        s.add("inspect.clearance", "fit", bodies=pins + [f1, f2, s1, s2], against=[n for n in everything
                                                                                   if n not in pins + [f1, f2, s1, s2]],
              nearest=1)
        s.add("inspect.clearance", "fit", bodies=[s1, s2, f1, f2], against=[s1, s2, f1, f2], nearest=1)
        r = run(s, scp, None)

    rep = Report(f"finray_tests/v2_multi-actuation GRIP-9017 (pull module mounted, check variant)")
    ta, tb = drive_common(rep, r, s, s.tags['ta'][0], s.tags['tb'][0], None)
    t1, t2 = r[s.tags['s1'][0]], r[s.tags['s2'][0]]
    q1, q2 = t1.get('points', []), t2.get('points', [])
    ok = len(q1) == 13 and len(q2) == 13 and t1.get('stopped_at') is None and t2.get('stopped_at') is None
    pulls = [q1[0][1] - q1[-1][1], q2[0][1] - q2[-1][1]] if ok else [None, None]
    drift = max(max(abs(a[0] - q1[0][0]) for a in q1), max(abs(a[0] - q2[0][0]) for a in q2)) if ok else 99
    rep.check(f"{pmax:g} knob turns pull both inner corners {pmax:g} mm back along the finger (+-0.02), sliders keep x",
              ok and all(abs(p - pmax) < 0.02 for p in pulls) and drift < 0.01,
              f"pull {pulls[0]:.3f} / {pulls[1]:.3f} mm, x drift {drift:.4f} mm" if ok else str(t1)[:200])
    step = [q1[k][1] - q1[k + 1][1] for k in range(12)] if ok else []
    rep.check("1 knob turn = 1 mm of pull, constant over the stroke (45 deg cam)", step and max(abs(x - 0.5) for x in step) < 0.01,
              f"per half turn {min(step):.3f} .. {max(step):.3f} mm" if step else '-')
    car = [b[0] for b in tb]
    rep.check(f"carriage B moves {pmax:g} mm toward the centre for {pmax:g} mm of pull", ta and abs(car[0] - car[-1] - pmax) < 0.02,
              f"{car[0] - car[-1]:.3f} mm")
    sweep_rows(rep, r, s, groups)
    static_rows(rep, r, s, 'fit', "pins, fingers, sliders vs everything mounted at zero pull: no overlap, none unchecked")
    rep.show()
    return rep.fails


if __name__ == '__main__':
    which = [a for a in sys.argv[1:] if a in ('parallel', 'pull', 'csocket')] or ['parallel', 'pull', 'csocket']
    fails = 0
    for m in which:
        fails += check_pull() if m == 'pull' else check_parallel(m)
    sys.exit(1 if fails else 0)
