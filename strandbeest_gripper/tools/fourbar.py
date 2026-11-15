"""Four-bar leg of v8 (GRIP-9016): crank-rocker whose coupler point P traces the same jaw loop
function as the v7 Jansen foot at S = 0.4 (jansen.py): same opening (step height H), same flat
clamp-and-pull stroke (gap within +-0.2 per jaw), same crank share in the clamp.

Fitted by differential evolution (scratch scripts, 2026-11-15) with constraints for the real parts:
eccentric crank (coupler ring on an eccentric boss of the crank gear, D5 shaft through it), the
rocker pivot post Q outside the ring sweep, the rocker clear of the top-plate stub at O, and the
loop below the linkage (clamp side facing away from it, as the Jansen foot).

Leg frame: crank centre O = (0, 0); the clamp flat runs along x at the bottom of the loop (y min);
crank angle theta from +x, counter-clockwise. Joints: J1 crank pin (ring centre), B coupler-rocker,
Q rocker pivot (fixed), P coupler point = jaw pin.
"""
import math

# lengths (mm) and coupler point in the J1->B frame; PSI turns the fitted linkage so the flat is along x
# Seed 2 of the robust fit (user choice 2026-11-15), rounded to 0.01 mm: rounding changes the clamp flatness
# by 0.003 mm (flatness() below), so these are the design values.
LEG = dict(r=8.77, a=16.75, c=25.07, g=28.27, u=11.48, v=29.87)
PSI = 2.1596                     # rad
BRANCH = +1
CS, SN = math.cos(PSI), math.sin(PSI)


def rot(p):
    return (CS * p[0] - SN * p[1], SN * p[0] + CS * p[1])


Q_LEG = rot((LEG['g'], 0.0))


def pose(theta, L=LEG):
    """Joint positions (leg frame) at crank angle theta (rad, measured in the leg frame)."""
    # solve in the fit frame (Q on +x), then rotate by PSI; theta in the leg frame = fit angle + PSI
    t = theta - PSI
    A = (L['r'] * math.cos(t), L['r'] * math.sin(t))
    Q = (L['g'], 0.0)
    dx, dy = Q[0] - A[0], Q[1] - A[1]
    D = math.hypot(dx, dy)
    a, c = L['a'], L['c']
    if D > a + c or D < abs(a - c):
        return None
    al = (a * a - c * c + D * D) / (2 * D)
    h = math.sqrt(max(a * a - al * al, 0.0))
    ex, ey = dx / D, dy / D
    B = (A[0] + al * ex - BRANCH * h * ey, A[1] + al * ey + BRANCH * h * ex)
    e = ((B[0] - A[0]) / a, (B[1] - A[1]) / a)
    P = (A[0] + L['u'] * e[0] - L['v'] * e[1], A[1] + L['u'] * e[1] + L['v'] * e[0])
    return dict(O=(0.0, 0.0), J1=rot(A), B=rot(B), Q=rot(Q), P=rot(P))


def loop(n=1440):
    return [(2 * math.pi * k / n, pose(2 * math.pi * k / n)) for k in range(n)]


def metrics(n=1440, band=0.2):
    rows = loop(n)
    ys = [p['P'][1] for _, p in rows]
    xs = [p['P'][0] for _, p in rows]
    ymin = min(ys)
    i0 = ys.index(ymin)
    run = [i0]
    k = i0
    while ys[(k + 1) % n] - ymin <= band and len(run) < n:
        k = (k + 1) % n
        run.append(k)
    k = i0
    while ys[(k - 1) % n] - ymin <= band and len(run) < n:
        k = (k - 1) % n
        run.insert(0, k)
    fx = [xs[i] for i in run]
    mu = []
    for _, p in rows:
        b, a_, q = p['B'], p['J1'], p['Q']
        v1, v2 = (a_[0] - b[0], a_[1] - b[1]), (q[0] - b[0], q[1] - b[1])
        ang = math.degrees(math.acos((v1[0] * v2[0] + v1[1] * v2[1]) / (math.hypot(*v1) * math.hypot(*v2))))
        mu.append(min(ang, 180 - ang))
    return dict(H=max(ys) - ymin, stroke=max(fx) - min(fx), stride=max(xs) - min(xs), ymin=ymin,
                clamp_deg=len(run) * 360.0 / n, clamp_theta=(math.degrees(rows[run[0]][0]), math.degrees(rows[run[-1]][0])),
                mu_min=min(mu), xrange=(min(xs), max(xs)), yrange=(ymin, max(ys)))


def flatness(L=LEG, stroke=19.9, n=1440):
    """Smallest band b such that P stays within b of its lowest y over a contiguous stroke of `stroke` mm.
    This is the clamp-gap error per jaw over the clamp-and-pull stroke (continuous, unlike a fixed-band
    stroke length, which jumps when a bump of the flat crosses the band). Jansen v7 at S = 0.4: 0.189."""
    pts = [pose(2 * math.pi * k / n, L)['P'] for k in range(n)]
    ys, xs = [p[1] for p in pts], [p[0] for p in pts]
    ymin = min(ys)
    i0 = ys.index(ymin)

    def run_len(b):
        run, k = [i0], i0
        while ys[(k + 1) % n] - ymin <= b and len(run) < n:
            k = (k + 1) % n
            run.append(k)
        k = i0
        while ys[(k - 1) % n] - ymin <= b and len(run) < n:
            k = (k - 1) % n
            run.append(k)
        f = [xs[i] for i in run]
        return max(f) - min(f)
    lo, hi = 0.0, 3.0
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if run_len(mid) >= stroke else (mid, hi)
    return hi


def tolerance_flatness(dl=0.1):
    """Worst flatness with any one length off by +-dl (print error). Jansen v7 at S = 0.4: 0.270."""
    worst = 0.0
    for k in LEG:
        for s in (-dl, dl):
            L = dict(LEG)
            L[k] += s
            worst = max(worst, flatness(L))
    return worst


def check_against_jansen():
    """Asserts the v8 leg keeps the v7 jaw function (jaw_relations.py numbers at S = 0.4)."""
    m = metrics()
    assert abs(m['H'] - 8.98) < 0.05, m           # opening 2H = 17.97 (v7 max gap 19.50 - clamp 1.53)
    assert 19.8 <= m['stroke'] <= 21.0, m           # clamp-and-pull stroke 19.9 (v7)
    m['flatness'] = flatness()
    assert m['flatness'] <= 0.189, m                # gap error over 19.9 mm no worse than Jansen v7
    m['tolerance_flatness'] = tolerance_flatness()
    assert m['tolerance_flatness'] <= 0.27, m       # and no worse than Jansen with +-0.1 mm length errors
    assert m['clamp_deg'] >= 120, m                 # v7: 132 deg of crank in the clamp band
    assert m['mu_min'] >= 45, m                     # transmission angle (v7 Jansen J4: lower)
    return m


if __name__ == '__main__':
    m = check_against_jansen()
    for k, v in m.items():
        print(f'{k:12s} {v}')
    p0 = pose(0.0)
    print('theta=0:', {k: (round(v[0], 3), round(v[1], 3)) for k, v in p0.items()})
