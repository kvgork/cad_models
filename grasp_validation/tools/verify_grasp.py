"""Verify GRIP-9015 (grasp validation bench, stages 1-2) against the generator's spec.

Writes grasp_validation/cad/GRIP-9015_assy-grasp-bench-stage1-2.verify.json, runs it on the built
assembly and prints a PASS/FAIL table. Every number comes from gen_grasp.py, never typed here.

    python3 grasp_validation/tools/gen_grasp.py && tools/build.sh grasp_validation
    python3 grasp_validation/tools/verify_grasp.py [--raw]

SOLIDCRAFT_CLI overrides the binary (default: solidcraft-cli on PATH).
"""
import json
import math
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import gen_grasp as g  # noqa: E402

SC = 'grasp_validation/cad/GRIP-9015_assy-grasp-bench-stage1-2.sc'
SCRIPT = 'grasp_validation/cad/GRIP-9015_assy-grasp-bench-stage1-2.verify.json'
CLI = os.environ.get('SOLIDCRAFT_CLI', 'solidcraft-cli')
ADAPTER = 'gripper_tester/exports/GRIP-0002_gripper-adapter_X1.step'


def main():
    g.build()
    names = {pn: n for n, pn in g.PARTS}
    J = {k: names[g.PN[k]] for k in g.PN}
    cell = {s: f"load-cell-TAL220B-{s}30_F1" for s in 'wd'}
    dow = {s: [f"dowel-4x28-ISO2338-{s}30_F{i}" for i in (1, 2)] for s in 'wd'}
    c = []

    def add(cmd, **p):
        c.append({"command": cmd, "params": p})
        return len(c) - 1

    # probes: the cell surface that must NOT touch each jaw (everything except that jaw's end block),
    # grown 0.05 mm toward the jaw. Jaw A may touch only x < -cell_l/2 + end_block on the cell's underside.
    probes = {}
    for s, (ox, oy) in (('w', g.POS['w30']), ('d', g.POS['d30'])):
        xa = ox - g.CELL_L / 2 + g.END_BLOCK + 0.05
        add("solid.box", length=f"{g.CELL_L / 2 - g.END_BLOCK + g.CELL_L / 2 - 0.05} mm", width=f"{g.CELL_W} mm",
            height="0.05 mm", center=[(xa + ox + g.CELL_L / 2) / 2, oy, -g.CELL_H / 2 - 0.025], operation="new",
            body_name=f"probe_a_{s}")
        xb = ox + g.CELL_L / 2 - g.END_BLOCK - 0.05
        add("solid.box", length=f"{xb - (ox - g.CELL_L / 2)} mm", width=f"{g.CELL_W} mm",
            height="0.05 mm", center=[(xb + ox - g.CELL_L / 2) / 2, oy, g.CELL_H / 2 + 0.025], operation="new",
            body_name=f"probe_b_{s}")
        probes[s] = (f"probe_a_{s}", f"probe_b_{s}")
    i_cell = {s: add("inspect.clearance", bodies=[cell[s]], against=[J['a' + s], J['b' + s]], nearest=2) for s in 'wd'}
    i_probe = {s: add("inspect.clearance", bodies=[probes[s][0], probes[s][1]], against=[J['a' + s], J['b' + s]],
                      nearest=4) for s in 'wd'}
    i_dow = {s: add("inspect.clearance", bodies=dow[s], against=[J['a' + s], J['b' + s], cell[s]], nearest=6)
             for s in 'wd'}
    i_plat = add("inspect.clearance", bodies=[J['platform']], against=[J['bw'], J['aw'], cell['w']], nearest=3)
    i_crad = add("inspect.clearance", bodies=[J['cradle']], against=[J['ad'], J['bd'], cell['d']], nearest=3)
    # DR-1a: the real GRIP-0002 adapter in the channel, dovetail on the floor (adapter z 0 = its dovetail base)
    ox, oy = g.POS['dr']
    add("file.insert_step", path=ADAPTER, name="adapter_part")
    add("occurrence.move", occurrence="adapter_part:1", space="world",
        matrix=[[1, 0, 0, ox], [0, 1, 0, oy], [0, 0, 1, g.DT['floor']]], move_grounded=True)
    i_dr = add("inspect.clearance", bodies=["adapter"], against=[J['dr']], nearest=2)
    # hub: a PCB envelope (width x 1.6) in every groove pair, 40 mm long
    bx, by = g.POS['box']
    pcbs = []
    for key, wb, zb, (cx, cy), ax, rl in g.BOARDS:
        z = g.BOX['floor'] + zb + g.PCB / 2
        L = 40.0
        dims = (L, wb, g.PCB) if ax == 'X' else (wb, L, g.PCB)
        add("solid.box", length=f"{dims[0]} mm", width=f"{dims[1]} mm", height=f"{dims[2]} mm",
            center=[bx + cx, by + cy, z], operation="new", body_name=f"pcb_{key}")
        pcbs.append(f"pcb_{key}")
    i_pcb = add("inspect.clearance", bodies=pcbs, against=[J['box']], nearest=12)
    i_pcb2 = add("inspect.clearance", bodies=pcbs, against=pcbs, nearest=12)

    with open(os.path.join(ROOT, SCRIPT), 'w') as fh:
        json.dump(c, fh, indent=0)
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, 'r.json')
        subprocess.run([CLI, 'run', SCRIPT, '--in', SC, '--results', '--json-out', out],
                       check=True, stdout=subprocess.DEVNULL, cwd=ROOT)
        r = json.load(open(out))
        ev = subprocess.run([CLI, 'eval', SC], capture_output=True, text=True, cwd=ROOT).stdout
    r = [x.get('result', x) if isinstance(x, dict) else x for x in r]
    assert len(r) == len(c), (len(r), len(c))
    if '--raw' in sys.argv:
        print(json.dumps(r, indent=1)[:30000])
        return 0
    bodies = {b['name']: b for b in json.loads(ev[ev.index('{'):])['bodies']}

    rows, fails = [], 0

    def check(name, ok, value):
        nonlocal fails
        rows.append(('PASS' if ok else 'FAIL', name, value))
        fails += not ok

    def ovl(x):
        return [(o['a'], o['b'], round(o['volume_mm3'], 4)) for o in x.get('overlaps', [])]

    def mind(x):
        """nearest distances as 'body: mm' (one entry per against-body, per checked body)"""
        out = []
        for b, lst in (x.get('nearest') or {}).items():
            out += [f"{e['body'].split('_F')[0]} {e['distance_mm']:.2f}" for e in lst]
        return '; '.join(out[:4])

    def unexpected(x, allowed):
        """unchecked pairs not in the allowed set (pairs given as frozensets of body names)"""
        return [u for u in x.get('unchecked', []) if frozenset((u['a'], u['b'])) not in allowed]

    # 1. volumes against the analytic model (labels debossed: up to ~25 mm3; d30 counterbore on a curved face)
    exp = expected_volumes()
    for k in ('aw', 'bw', 'ad', 'bd'):
        v = bodies[J[k]]['volume_mm3']
        # W: labels only remove material (v <= expected, by < 25). D: the counterbore meets a curved
        # face, so it removes less than the flat-face estimate (v > expected, by < 60), labels remove some.
        ok = (-25.0 <= v - exp[k] <= 1.0) if k[1] == 'w' else (-25.0 <= v - exp[k] <= 60.0)
        check(f"{g.PN[k]} volume vs analytic (labels; D30: curved counterbore)", ok,
              f"{v:.1f} vs {exp[k]:.1f} ({v - exp[k]:+.1f})")
    # 2. artifact envelope: 30.00 across the squeeze faces, 86 long
    for s in 'wd':
        a, b = bodies[J['a' + s]]['bbox'], bodies[J['b' + s]]['bbox']
        across = b['max'][2] - a['min'][2]
        length = a['max'][0] - a['min'][0]
        check(f"{s}30 artifact: {g.SIZE:g} mm across the squeeze faces, {g.JAW_L:g} long",
              abs(across - g.SIZE) < 0.01 and abs(length - g.JAW_L) < 0.01, f"{across:.3f} x {length:.3f}")
    # 3. cell: no overlap with either jaw; jaws touch only their own end block
    for s in 'wd':
        x = r[i_cell[s]]
        assert not x.get('unchecked') and not r[i_probe[s]].get('unchecked'), 'unexpected unchecked cell pairs'
        check(f"{s}30: cell vs jaws, no overlap", not ovl(x) and x.get('pairs_checked', 0) > 0,
              f"{ovl(x)} pairs {x.get('pairs_checked')} unchecked {x.get('unchecked')}")
        p = r[i_probe[s]]
        check(f"{s}30: jaws clear of the cell's beam + other end (probe 0.05 mm, no overlap)",
              not ovl(p) and p.get('pairs_checked', 0) > 0, f"{ovl(p)} unchecked {p.get('unchecked')}")
    # 4. dowels: no overlap with the jaws or the cell
    for s in 'wd':
        x = r[i_dow[s]]
        # a pin drawn at exactly the press-hole diameter (3.8) is coincident with its hole wall; the kernel
        # may report that pair unchecked. Only those (dowel vs jaw A) are allowed; anything else fails.
        allowed = {frozenset((d, J['a' + s])) for d in dow[s]}
        bad = unexpected(x, allowed)
        check(f"{s}30: dowels (drawn Ø3.8) vs press/slip holes and cell, no overlap",
              not ovl(x) and x.get('pairs_checked', 0) > 0 and not bad,
              f"{ovl(x)} unchecked: {len(x.get('unchecked', []))} (allowed coincident press fits), unexpected {bad}")
    # 5. calibration kit
    x = r[i_plat]
    check("platform rests on W30 jaw B without overlap (rails clear)", not ovl(x) and x.get('pairs_checked', 0) > 0,
          f"{ovl(x)} closest {mind(x)}")
    x = r[i_crad]
    check("V cradle holds D30 jaw A without overlap", not ovl(x) and x.get('pairs_checked', 0) > 0,
          f"{ovl(x)} closest {mind(x)}")
    # 6. DR-1a with the real GRIP-0002 adapter
    x = r[i_dr]
    check("GRIP-0002 adapter in the DR-1a channel: no overlap", not ovl(x) and x.get('pairs_checked', 0) > 0,
          f"{ovl(x)} closest {mind(x)} unchecked {x.get('unchecked')}")
    # 7. hub boards
    x = r[i_pcb]
    check("6 PCB envelopes sit in their grooves without touching the box", not ovl(x) and x.get('pairs_checked', 0) > 0,
          f"{ovl(x)} closest {mind(x)} pairs {x.get('pairs_checked')}")
    x = r[i_pcb2]
    check("PCB envelopes clear of each other", not [o for o in ovl(x) if o[0] != o[1]], f"closest {mind(x)}")

    w = max(len(n) for _, n, _ in rows)
    for st, n, v in rows:
        print(f"{st}  {n.ljust(w)}  {v}")
    print(f"\n{len(rows) - fails}/{len(rows)} passed")
    return 1 if fails else 0


def expected_volumes():
    R, t = g.SIZE / 2, g.SIZE / 2 - g.ZI
    hole = math.pi / 4 * (g.M5_CLR ** 2 * t + (g.M5_CB_D ** 2 - g.M5_CLR ** 2) * g.M5_CB_H)
    xa0 = -g.CELL_L / 2 + g.END_BLOCK
    pk_a = (g.POCKET_END - xa0) * 2 * g.POCKET_Y * g.POCKET
    pk_b = (g.CELL_L / 2 - g.END_BLOCK + g.POCKET_END) * 2 * g.POCKET_Y * g.POCKET
    # dowels sit outside the closed pockets: through the full jaw (A), full blind depth (B)
    dp = 2 * math.pi / 4 * g.DOWEL_PRESS ** 2 * t
    ds = 2 * math.pi / 4 * g.DOWEL_SLIP ** 2 * g.DOWEL_B_DEPTH
    seg = R * R * math.acos(g.ZI / R) - g.ZI * math.sqrt(R * R - g.ZI * g.ZI)
    w, d = g.JAW_L * g.SIZE * t, g.JAW_L * seg
    return {'aw': w - hole - pk_a - dp, 'bw': w - hole - pk_b - ds, 'ad': d - hole - pk_a - dp, 'bd': d - hole - pk_b - ds}


if __name__ == '__main__':
    sys.exit(main())
