"""Verify storage_drawers v1 (STOR-9001): part sizes and X2D bed fit, the Manta case in the drawer, the drawer
slide (collision sweep), the detent click, lid and rail gaps, the stack fit and the test bin in its grid cell.

    python3 storage_drawers/tools/verify_storage.py [--ver v1|v2]   (default v1)

Builds the check variant (the committed stack + a Manta case dummy, no exports) in a temporary folder.
What a rigid CAD model can't show: the detent arm bending (the bump overlapping the pad while it passes is
expected and is checked as an overlap of the bump only), sag of the flanges under load, print tolerances.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_storage as g  # noqa: E402

if '--ver' in sys.argv:
    g.configure(sys.argv[sys.argv.index('--ver') + 1])

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
BED = (225.5, 246.0)

SEGMENTS = [(g.BUMP['y'] + 2.0, g.OPEN_STOP - 25.0), (g.OPEN_STOP + g.BUMP['y'] + 2.0, g.YD - 15.0)]          # X2D: area both nozzles reach minus 5 mm edge margins (tools/printer.json)


class Script:
    def __init__(self):
        self.c, self.tags = [], {}

    def add(self, cmd, tag=None, **p):
        if tag:
            self.tags.setdefault(tag, []).append(len(self.c))
        self.c.append({"command": cmd, "params": p})


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
            print(f"{s}  {n:92s} {val}")


def o(n):
    return f"{n}:1"


def overlaps(res):
    return [(x['a'], x['b'], round(x['volume_mm3'], 3)) for x in res.get('overlaps', [])]


def main():
    with tempfile.TemporaryDirectory() as td:
        js = g.out_path('check', td)
        g.write('check', js)
        sc = os.path.join(td, 'check.sc')
        subprocess.run(['solidcraft-cli', 'run', js, '--save', sc], check=True, stdout=subprocess.DEVNULL, cwd=ROOT)
        ev = json.loads(subprocess.run(['solidcraft-cli', 'eval', sc], check=True, capture_output=True, text=True,
                                       cwd=ROOT).stdout)
        names = [n for n, _ in g.PARTS]
        pick = lambda pre: sorted(n for n in names if n.startswith(pre))  # noqa: E731
        s1, s2 = pick('STOR-0001')
        sp, = pick('STOR-0003')
        dr, = pick(g.PN['drawer'])
        bn, = pick('STOR-0004')
        manta = 'CHECK_manta_case'
        yb = g.BUMP['y']
        s = Script()
        s.add("joint.list", "joints")
        s.add("inspect.clearance", "manta", bodies=[manta], against=[dr, s1], min_volume=1e-9)   # the bin is elsewhere when the case is in
        s.add("inspect.clearance", "bin", bodies=[bn], against=[dr], nearest=1)
        s.add("inspect.clearance", "stack", bodies=[s1, sp], against=[sp, s2], nearest=2)
        s.add("inspect.clearance", "closed", bodies=[dr, bn, manta], against=[s1, sp, s2], nearest=3)
        # the bump on the pad: half-way between the pocket and the shelf front
        s.add("joint.drive", joint="S_drawer", value=yb / 2)
        s.add("inspect.clearance", "click", bodies=[dr], against=[s1], nearest=1)
        # past the pad: free slide over the rest of the travel
        s.add("joint.drive", joint="S_drawer", value=yb + 2.0)
        s.add("inspect.clearance", "free", bodies=[dr, bn, manta], against=[s1, sp, s2], min_volume=1e-9)
        for lo_, hi_ in SEGMENTS:
            s.add("joint.sweep", "sweep", joint="S_drawer", **{"from": lo_, "to": hi_}, step=5.0,
                  occurrences=[o(dr), o(bn), o(manta)], against=[o(s1), o(sp), o(s2)], report_gaps=True)
        s.add("joint.drive", joint="S_drawer", value=g.OPEN_STOP)
        s.add("inspect.clearance", "openstop", bodies=[dr], against=[s1], nearest=1)
        s.add("joint.drive", joint="S_drawer", value=g.OPEN_STOP - (g.ARM['y1'] + 2.0 - yb) / 2)   # rear bump on the pad flat
        s.add("inspect.clearance", "openclick", bodies=[dr], against=[s1], nearest=1)
        s.add("joint.drive", joint="S_drawer", value=g.YD - 15.0)
        s.add("joint.list", "out")
        s.add("joint.drive", joint="S_drawer", value=0.0)
        sp_ = os.path.join(td, 'v.json')
        with open(sp_, 'w') as fh:
            json.dump(s.c, fh, indent=0)
        out = os.path.join(td, 'r.json')
        subprocess.run(['solidcraft-cli', 'run', sp_, '--in', sc, '--results', '--json-out', out], check=True,
                       stdout=subprocess.DEVNULL, cwd=ROOT)
        r = [x.get('result', x) if isinstance(x, dict) else x for x in json.load(open(out))]
        assert len(r) == len(s.c), (len(r), len(s.c))
    R = lambda t, i=0: r[s.tags[t][i]]  # noqa: E731
    rep = Report(f"{g.VDIR} {g.ASSY[0]} (check variant)")

    # sizes and bed fit
    bb = {b['name']: b['bbox'] for b in ev['bodies']}
    spec = {s1: (2 * g.XW, g.YS, g.ZL + 2 * g.RIM_H - g.SKIRT_CLR),          # skirt bottom .. rim top
            dr: (2 * (g.XW - g.FRONT_GAP), g.YD + g.FRONT_T + g.HANDLE['out'], g.ZL - g.ZB),
            bn: (g.BIN_W, g.BIN_W, 7 * g.BIN_U)}
    for n, want in spec.items():
        got = tuple(round(bb[n]['max'][k] - bb[n]['min'][k], 2) for k in range(3))
        rep.check(f"size {n}: {want[0]:g} x {want[1]:g} x {want[2]:g}", all(abs(a - b) < 0.05 for a, b in zip(got, want)),
                  f"{got}")
    for n, face in ((s1, (0, 2)), (sp, (0, 2)), (dr, (0, 1)), (bn, (0, 1))):
        d = [bb[n]['max'][k] - bb[n]['min'][k] for k in face]
        fits = (d[0] <= BED[1] and d[1] <= BED[0]) or (d[0] <= BED[0] and d[1] <= BED[1])
        rep.check(f"X2D bed: {n} footprint {d[0]:.1f} x {d[1]:.1f} fits {BED[0]} x {BED[1]}", fits, "")

    jl = R('joints')
    rep.check("joints solve: no conflicts, nothing floating", not jl.get('conflicts') and not jl.get('floating'),
              f"{len(jl.get('joints', []))} joints")
    m = R('manta')
    rep.check(f"Manta case {g.MANTA} grown by {g.MANTA_CHECK}: no overlap with drawer or shelf",
              not overlaps(m) and m.get('pairs_checked', 0) > 0 and not m.get('unchecked'), f"{overlaps(m)[:2]}")
    b = R('bin')
    rep.check("test bin in its grid cell: no overlap", not overlaps(b) and b.get('pairs_checked', 0) > 0
              and not b.get('unchecked'), f"{overlaps(b)[:2]}, closest {min(nearest(b) or [9]):.2f} mm")
    st = R('stack')
    rep.check("stack shelf / spacer / shelf: no overlap, none unchecked", not overlaps(st) and not st.get('unchecked'),
              f"{overlaps(st)[:2]}, {len(st.get('unchecked') or [])} unchecked, closest {min(nearest(st) or [9]):.2f}")
    cl = R('closed')
    rep.check("closed: drawer + bin + Manta vs stack: no overlap (bump relaxed in its pocket)",
              not overlaps(cl) and not cl.get('unchecked'), f"{overlaps(cl)[:3]}, closest {min(nearest(cl) or [9]):.2f}")
    ck = R('click')
    ov = overlaps(ck)
    bump_vol = 2 * 0.5 * (2 * g.BUMP['h']) * g.BUMP['h'] * (g.BUMP['z1'] - g.BUMP['z0'])
    rep.check("detent: half-way out the bumps overlap the pad (the arms must bend), only a bump-sized volume",
              ov and sum(v for _, _, v in ov) < bump_vol, f"{ov[:2]} (both bumps together < {bump_vol:.1f} mm³)")
    # Exact distances (nearest / clearance > 0) report a false 0.0 here: the flange-land edge (z 46.1) against the
    # rail's front edge (z 46.0), y = 0; a probe box shows no shelf material above z 46.0 (2026-11-18). So judge
    # contact by overlaps down to 1e-9 mm³ and read the gap from the (tessellated) sweep below.
    fr = R('free')
    rep.check(f"free slide ({yb + 2:g} mm out): no overlap down to 1e-9 mm³, none unchecked",
              not overlaps(fr) and not fr.get('unchecked') and fr.get('pairs_checked', 0) > 0, f"{overlaps(fr)[:2]}")
    for i, (lo_, hi_) in enumerate(SEGMENTS):
        sw = R('sweep', i)
        gaps = sw.get('min_gap') or {}
        mg = min((x['mm'] for x in gaps.values()), default=None)
        rep.check(f"slide sweep {lo_:g} .. {hi_:g} mm out (bumps off the pads): no collision, gap = rail drop",
                  sw.get('stopped_by') in (None, 'limit') and sw.get('pairs', 0) > 0 and mg is not None
                  and abs(mg - g.RAIL_DROP) < 0.02,
                  f"{sw.get('pairs')} pairs, stopped {sw.get('stopped_at')}, nearest {mg}")
    os_ = R('openstop')
    rep.check(f"open stop at {g.OPEN_STOP:g} mm: rear bumps relaxed in the pockets (no overlap)", not overlaps(os_)
              and os_.get('pairs_checked', 0) > 0, f"{overlaps(os_)[:2]}, closest {min(nearest(os_) or [9]):.2f}")
    oc = overlaps(R('openclick'))
    rep.check("open stop: just before it the rear bumps overlap the pad (click), only a bump-sized volume",
              oc and sum(v for _, _, v in oc) < bump_vol, f"{oc[:2]}")
    out = [j for j in R('out').get('joints', []) if j.get('name') == 'S_drawer']
    val = out[0]['values'][0]['value'] if out else None
    rep.check(f"drawer reaches {g.YD - 15:g} mm out", val is not None and abs(val - (g.YD - 15)) < 0.01, f"{val}")
    rep.show()
    return rep.fails


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
