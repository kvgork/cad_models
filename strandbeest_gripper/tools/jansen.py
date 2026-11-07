"""Jansen linkage kinematics (Theo Jansen's "holy numbers").

Forward kinematics after Wang (circle-circle intersections). The branch
(-1, -1, +1, -1, +1) reproduces Ghassaei's published reference at scale 1:
stride 67.9, step height 22.5, lowest foot point -91.8 (asserted below).

Link frame: crank centre O = (0, 0), frame pivot G = (-a, -l), crank angle
theta from +x, counter-clockwise.  Vault: 05-Wiki/research/
2026-11-06-strandbeest-jansen-linkage-grippers.md section 2.
"""
import math

HOLY = dict(a=38.0, l=7.8, m=15.0, j=50.0, b=41.5, d=40.1, e=55.8, k=61.9,
            c=39.3, f=39.4, g=36.7, h=65.7, i=49.0)
BRANCH = (-1, -1, +1, -1, +1)


def circ(P, rp, Q, rq, side):
    """Intersection of circle(P, rp) and circle(Q, rq); side picks the branch."""
    dx, dy = Q[0] - P[0], Q[1] - P[1]
    D = math.hypot(dx, dy)
    if D > rp + rq or D < abs(rp - rq):
        return None
    a = (rp * rp - rq * rq + D * D) / (2 * D)
    h = math.sqrt(max(rp * rp - a * a, 0.0))
    mx, my = P[0] + a * dx / D, P[1] + a * dy / D
    return (mx - side * h * dy / D, my + side * h * dx / D)


def pose(theta, s=1.0):
    """Joint positions at crank angle theta (rad) and scale s, or None."""
    L = {k: v * s for k, v in HOLY.items()}
    b1, b2, b3, b4, b5 = BRANCH
    O, G = (0.0, 0.0), (-L['a'], -L['l'])
    J1 = (L['m'] * math.cos(theta), L['m'] * math.sin(theta))
    J2 = circ(J1, L['j'], G, L['b'], b1)
    J3 = J2 and circ(J2, L['e'], G, L['d'], b2)
    J4 = circ(J1, L['k'], G, L['c'], b3)
    J5 = J3 and J4 and circ(J3, L['f'], J4, L['g'], b4)
    F = J5 and circ(J4, L['i'], J5, L['h'], b5)
    if not F:
        return None
    return dict(O=O, G=G, J1=J1, J2=J2, J3=J3, J4=J4, J5=J5, F=F)


def foot_path(s=1.0, step_deg=0.5):
    n = int(round(360 / step_deg))
    out = []
    for i in range(n):
        p = pose(math.radians(i * step_deg), s)
        if p is None:
            raise ValueError(f'linkage cannot close at crank {i * step_deg} deg (scale {s})')
        out.append((i * step_deg, p['F']))
    return out


def check_reference():
    """Ghassaei Table 3.3.1 (scale 1): stride 67.9, height 22.4-22.5, ymin -91.8."""
    F = [p for _, p in foot_path(1.0)]
    xs, ys = [p[0] for p in F], [p[1] for p in F]
    stride, height, ymin = max(xs) - min(xs), max(ys) - min(ys), min(ys)
    assert abs(stride - 67.9) < 0.1 and abs(height - 22.45) < 0.1 and abs(ymin + 91.8) < 0.1, \
        (stride, height, ymin)
    return stride, height, ymin


def transmission(p, at, a, b):
    """Angle (deg) at joint `at` between the two links to `a` and `b`."""
    a1 = math.atan2(p[a][1] - p[at][1], p[a][0] - p[at][0])
    a2 = math.atan2(p[b][1] - p[at][1], p[b][0] - p[at][0])
    return abs((math.degrees(a1 - a2) + 180) % 360 - 180)


if __name__ == '__main__':
    import sys
    s = float(sys.argv[1]) if len(sys.argv) > 1 else 0.4
    print('reference (s=1): stride %.2f height %.2f ymin %.2f  OK' % check_reference())
    rows = []
    for t in range(-180, 180):
        p = pose(math.radians(t), s)
        if p is None:
            raise SystemExit(f'linkage cannot close at crank {t} deg (scale {s})')
        rows.append((t, p))
    ymin = min(p['F'][1] for _, p in rows)
    st = [(t, p) for t, p in rows if p['F'][1] <= ymin + 0.2 * s / 0.4]
    ts = [t for t, _ in st]
    xs = [p['F'][0] for _, p in st]
    print('s=%.2f stance (tip within +-%.2f of ymin %.2f): crank %d..%d deg, travel %.2f mm'
          % (s, 0.2 * s / 0.4, ymin, min(ts), max(ts), max(xs) - min(xs)))
    fa = [math.degrees(math.atan2(p['F'][1] - p['J4'][1], p['F'][0] - p['J4'][0])) for _, p in st]
    fa = [fa[0] + ((a - fa[0] + 180) % 360 - 180) for a in fa]          # unwrap around the first
    print('foot triangle rotation through stance: %.1f..%.1f deg' % (min(fa), max(fa)))
    tj4 = [transmission(p, 'J4', 'J1', 'G') for _, p in st]
    print('transmission angle at J4 in stance: %.0f..%.0f deg' % (min(tj4), max(tj4)))
    full = min((transmission(p, 'J4', 'J1', 'G'), t) for t, p in rows)
    print('minimum J4 transmission over the full turn: %.1f deg at crank %d deg' % full)
