"""Verify finray_tests GRIP-9010: joints, symmetric jaw motion, screw pitch, rack/pinion ratio and
mesh, collisions over the full stroke, finger fit and the closed / open gap.

    python3 finray_tests/tools/verify_finray.py          (run from anywhere; needs the built .sc)
"""
import json
import math
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_finray as g  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SC = g.OUT.replace('.json', '.sc')
SCRIPT = g.OUT.replace('.json', '.verify.json')


def main():
    g.build()
    names = [n for n, _ in g.PARTS]
    car_a, car_b, pin, base = g.comp('car_a'), g.comp('car_b'), g.comp('pinion'), g.comp('base')
    fa1, fa2 = g.comp('fa', 1), g.comp('fa', 2)
    lo, hi = g.XG0 - g.XG_MAX, g.XG0 - g.XG_MIN          # S_A: -15 (open) .. +19 (closed)
    # S_A follows the knob through the screw link (pitch 1 mm): drive R_knob, 360 deg per mm
    K = 360.0
    pa = [-(g.XG0 + g.CAR_L / 2), g.SCREW_Y, 25.0]       # a point on each carriage (as built)
    pb = [g.XG0 + g.CAR_L / 2, g.SCREW_Y, 25.0]
    ptooth = [0.0, g.PIN_Y + g.RP, g.Z0 + 3]             # pinion pitch point under rack A
    c = []
    add = lambda cmd, **p: c.append({"command": cmd, "params": p})  # noqa: E731
    add("joint.list")
    add("motion.trace", occurrence=f"{car_a}:1", point=pa, joint="R_knob", **{"from": K * lo, "to": K * hi}, samples=35)
    add("motion.trace", occurrence=f"{car_b}:1", point=pb, joint="R_knob", **{"from": K * lo, "to": K * hi}, samples=35)
    add("motion.trace", occurrence=f"{pin}:1", point=ptooth, joint="R_knob", **{"from": 0, "to": K * 9}, samples=10)
    add("joint.drive", joint="R_knob", value=360)
    add("joint.list")
    add("joint.drive", joint="R_knob", value=0)
    # sweep budget: chunked, gears (pinion) and knob left out; the mesh is checked statically below
    sweeps = [([car_a, fa1], [base, car_b, fa2]), ([car_b, fa2], [base])]
    for occs, ag in sweeps:
        add("joint.sweep", joint="R_knob", **{"from": K * lo, "to": K * hi}, step=K,
            occurrences=[f"{n}:1" for n in occs], against=[f"{n}:1" for n in ag], report_gaps=True)
    mesh_vals = [lo + k * (math.pi / 6) for k in range(7)] + [0.0, hi - math.pi / 2, hi]
    for v in mesh_vals:
        add("joint.drive", joint="R_knob", value=K * v)
        add("inspect.clearance", bodies=[pin], against=[car_a, car_b], nearest=2)
    for v in (hi, lo):
        add("joint.drive", joint="R_knob", value=K * v)
        add("inspect.clearance", bodies=[fa1], against=[fa2], nearest=1)
    add("joint.drive", joint="R_knob", value=0)
    add("inspect.clearance", bodies=[fa1, fa2], against=[car_a, car_b], nearest=1)
    hw = ["M6x70-ISO4017_F1", "M6-nyloc-DIN985_F1", "M6-nut-ISO4032_F1", g.comp('knob')]
    for v in (hi, lo):
        add("joint.drive", joint="R_knob", value=K * v)
        add("inspect.clearance", bodies=hw, against=[car_a, car_b, base], nearest=1)
    with open(os.path.join(ROOT, SCRIPT), 'w') as fh:
        json.dump(c, fh, indent=0)
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, 'r.json')
        subprocess.run(['solidcraft-cli', 'run', SCRIPT, '--in', SC, '--results', '--json-out', out],
                       check=True, stdout=subprocess.DEVNULL, cwd=ROOT)
        r = json.load(open(out))
    r = [x.get('result', x) if isinstance(x, dict) else x for x in r]
    assert len(r) == len(c), (len(r), len(c))
    if '--raw' in sys.argv:
        print(json.dumps(r, indent=1)[:20000])
        return 0

    rows, fails = [], 0

    def check(name, ok, value):
        nonlocal fails
        rows.append(('PASS' if ok else 'FAIL', name, value))
        fails += not ok

    jl = r[0]
    check("joints solve: no conflicts, nothing floating", not jl.get('conflicts') and not jl.get('floating'),
          f"{len(jl.get('joints', []))} joints, {len(jl.get('links', []))} motion links")
    ta, tb = r[1]['points'], r[2]['points']
    check("traces complete (35 samples each, not stopped)", len(ta) == 35 and len(tb) == 35
          and r[1].get('stopped_at') is None and r[2].get('stopped_at') is None, f"{len(ta)}, {len(tb)}")
    sym = max(abs(a[0] + b[0]) for a, b in zip(ta, tb)) if ta and tb else 99
    flat = max(max(abs(a[1] - ta[0][1]), abs(a[2] - ta[0][2]), abs(b[1] - tb[0][1]), abs(b[2] - tb[0][2]))
               for a, b in zip(ta, tb)) if ta and tb else 99
    check("jaws move symmetrically about x = 0 (<= 0.01 mm)", sym <= 0.01, f"max |xA + xB| {sym:.4f} mm")
    check("jaws move only along X (<= 0.01 mm)", flat <= 0.01, f"{flat:.4f} mm")
    xg = [(b[0] - g.CAR_L / 2) for b in tb]
    check(f"grip-face range {g.XG_MIN:g} .. {g.XG_MAX:g} mm per side (gap {2 * g.XG_MIN:g} .. {2 * g.XG_MAX:g} mm)",
          abs(min(xg) - g.XG_MIN) < 0.01 and abs(max(xg) - g.XG_MAX) < 0.01, f"{min(xg):.2f} .. {max(xg):.2f} mm")
    tp = r[3]['points']
    ang = math.degrees(math.atan2(tp[-1][1] - g.PIN_Y, tp[-1][0]) - math.atan2(tp[0][1] - g.PIN_Y, tp[0][0]))
    check("rack/pinion: 9 mm of rack turns the pinion 1 rad (57.30 deg)", abs(abs(ang) - 57.2958) < 0.05,
          f"{ang:.2f} deg")
    sa = [j for j in r[5].get('joints', []) if j.get('name') == 'S_A']
    v = sa[0]['values'][0]['value'] if sa else None
    check("thumb screw: one knob turn moves jaw A 1.00 mm", v is not None and abs(abs(v) - 1.0) < 0.01, f"{v}")
    for i, (occs, ag) in enumerate(sweeps):
        sw = r[7 + i]
        gaps = sw.get('min_gap') or {}
        mg = min(gaps.values(), key=lambda x: x['mm']) if gaps else None
        check(f"stroke sweep {i + 1}: {' + '.join(o.split('_')[1] for o in occs)} vs {' + '.join(a.split('_')[1] for a in ag)}: no collision",
              sw.get('stopped_by') in (None, 'limit') and sw.get('pairs', 0) > 0,
              f"stopped_at {sw.get('stopped_at')}, by {sw.get('stopped_by')}, {sw.get('pairs')} pairs, "
              f"touching at start {sw.get('touching_at_start')}, nearest {mg['mm']:.2f} mm" if mg else f"{sw}")
    k = 7 + len(sweeps)
    mins, over = [], 0
    for _ in mesh_vals:
        cl = r[k + 1]
        over += len(cl.get('overlaps', []))
        mins += [nb['distance_mm'] for near in (cl.get('nearest') or {}).values() for nb in near]
        k += 2
    check("rack/pinion mesh: no overlap at 10 positions over a tooth pitch + stroke ends, gap >= 0.05 mm",
          over == 0 and mins and min(mins) >= 0.05, f"{over} overlaps, closest {min(mins) if mins else None:.3f} mm")
    closed, opened = r[k + 1], r[k + 3]
    dc = [nb['distance_mm'] for near in (closed.get('nearest') or {}).values() for nb in near]
    do = [nb['distance_mm'] for near in (opened.get('nearest') or {}).values() for nb in near]
    check(f"closed: finger grip faces {2 * g.XG_MIN:g} mm apart; open: {2 * g.XG_MAX:g} mm",
          dc and do and abs(min(dc) - 2 * g.XG_MIN) < 0.02 and abs(min(do) - 2 * g.XG_MAX) < 0.02,
          f"{min(dc) if dc else None:.2f} / {min(do) if do else None:.2f} mm")
    fit = r[k + 5]
    check("finger tongues sit in the jaw grooves without overlap", not fit.get('overlaps') and fit.get('pairs_checked', 0) > 0,
          f"{len(fit.get('overlaps', []))} overlaps, {fit.get('pairs_checked')} pairs")
    hwr = [r[k + 7], r[k + 9]]
    ov = [(o['a'], o['b'], round(o['volume_mm3'], 3)) for x in hwr for o in x.get('overlaps', [])]
    dmin = min(nb['distance_mm'] for x in hwr for near in (x.get('nearest') or {}).values() for nb in near)
    check("screw, nyloc, nut and knob vs carriages and base at both stroke ends: no overlap",
          not ov and all(x.get('pairs_checked', 0) > 0 for x in hwr), f"{len(ov)} overlaps {ov[:2]}, closest {dmin:.2f} mm")
    print('== finray_tests GRIP-9010')
    for s, n, val in rows:
        print(f"{s}  {n:95s} {val}")
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
