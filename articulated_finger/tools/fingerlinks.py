"""Planar model of v2's coupled finger (concept C6): servo horn -> rod -> MCP lever; crossed links make PIP
follow MCP (base pivot B0 -> middle M1) and DIP follow PIP (proximal P1 -> distal D1). One DOF.

Frame: the XZ plane of finger_common (MCP at (0, 60.5), finger up +Z, palm -X); joint angles positive for
flexion (CCW in (x, z): +Z turns toward -X). Every link is drawn in the straight pose (all angles 0), so its
length is the as-built distance. Local points are offsets in the straight pose from the joint they turn about.

    python3 articulated_finger/tools/fingerlinks.py      prints the motion table and asserts check()
"""
import math

MCP = (0.0, 60.5)
SERVO = (0.0, 34.5)
L_PROX, L_MID = 45.0, 25.0

# fitted 2026-11-22 (fit_links() from a hand start: crossed links with each pivot's travel centred on the
# direction of its link; Nelder-Mead on BOUNDS, then rounded to 0.1); check() asserts what they must satisfy
P = dict(
    B0=(11.9, 70.3),         # base pivot of the PIP link (dorsal-high on a -Y cheek lug), world
    M1=(-11.3, 5.8),         # middle pivot (palm ear on the -Y side), from PIP
    P1=(5.1, 5.0),           # proximal pivot of the DIP link (dorsal ear on +Y, over the PIP), from PIP
    D1=(-7.3, 4.0),          # distal pivot (palm ear on +Y), from DIP
    L=(14.4, -4.0),          # MCP lever pin, from MCP
    rh=12.0,                 # horn radius
    phi0=-75.0,              # horn angle at the straight pose (deg from +X toward +Z)
)


def rot(p, a):
    c, s = math.cos(a), math.sin(a)
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def frames(t1, t2, t3):
    """World origins + rotations of proximal (MCP), middle (PIP), distal (DIP); angles in rad."""
    pip = add(MCP, rot((0, L_PROX), t1))
    dip = add(pip, rot((0, L_MID), t1 + t2))
    return (MCP, t1), (pip, t1 + t2), (dip, t1 + t2 + t3)


def world(p, frame):
    return add(frame[0], rot(p, frame[1]))


def p1loc(q=P):
    """P1 in the proximal frame (origin MCP)."""
    return (q['P1'][0], L_PROX + q['P1'][1])


def horn_pt(phi, q=P):
    a = math.radians(q['phi0'] + phi)
    return add(SERVO, (q['rh'] * math.cos(a), q['rh'] * math.sin(a)))


def lengths(q=P):
    f = frames(0, 0, 0)
    return dict(rod=dist(horn_pt(0, q), world(q['L'], f[0])),
                l1=dist(q['B0'], world(q['M1'], f[1])),
                l2=dist(world(p1loc(q), f[0]), world(q['D1'], f[2])))


def _root(fn, x0, span=math.radians(25), n=50):
    """Root of fn nearest x0 (continuation): widen a bracket around x0 step by step, then bisect."""
    step = math.radians(0.5)
    f0 = fn(x0)
    if f0 == 0:
        return x0
    for k in range(1, int(span / step) + 1):
        for a, b in ((x0 + (k - 1) * step, x0 + k * step), (x0 - (k - 1) * step, x0 - k * step)):
            fa, fb = fn(a), fn(b)
            if fa * fb <= 0:
                lo, hi = a, b
                for _ in range(50):
                    m = (lo + hi) / 2
                    fm = fn(m)
                    if fn(lo) * fm <= 0:
                        hi = m
                    else:
                        lo = m
                return (lo + hi) / 2
    return None


def solve(phi, guess=(0.0, 0.0, 0.0), q=P, ln=None):
    """Joint angles (rad) for horn angle phi (deg), continuing from guess; None if a loop can't close."""
    ln = ln or lengths(q)
    h = horn_pt(phi, q)
    t1 = _root(lambda t: dist(h, world(q['L'], (MCP, t))) - ln['rod'], guess[0])
    if t1 is None:
        return None
    t2 = _root(lambda t: dist(q['B0'], world(q['M1'], frames(t1, t, 0)[1])) - ln['l1'], guess[1])
    if t2 is None:
        return None
    t3 = _root(lambda t: dist(world(p1loc(q), frames(t1, t2, 0)[0]), world(q['D1'], frames(t1, t2, t)[2])) - ln['l2'], guess[2])
    if t3 is None:
        return None
    return t1, t2, t3


MCP_END = 80.0          # the sweep runs the MCP from 0 to this; the horn stroke follows from the rod loop


def sweep(q=P, ln=None, n=40):
    """(horn angle deg, (t1, t2, t3) rad) for MCP 0 .. MCP_END; None if a loop cannot close on the way."""
    ln = ln or lengths(q)
    out, g, phi = [], (0.0, 0.0), 0.0
    for k in range(n + 1):
        t1 = math.radians(MCP_END * k / n)
        Lw = world(q['L'], (MCP, t1))
        ph = _root(lambda a: dist(horn_pt(math.degrees(a), q), Lw) - ln['rod'], math.radians(phi), span=math.radians(60))
        if ph is None:
            return None
        phi = math.degrees(ph)
        t2 = _root(lambda t: dist(q['B0'], world(q['M1'], frames(t1, t, 0)[1])) - ln['l1'], g[0])
        if t2 is None:
            return None
        t3 = _root(lambda t: dist(world(p1loc(q), frames(t1, t2, 0)[0]), world(q['D1'], frames(t1, t2, t)[2])) - ln['l2'], g[1])
        if t3 is None:
            return None
        out.append((phi, (t1, t2, t3)))
        g = (t2, t3)
    return out


def _tang(a, b, piv):
    """Transmission angle (deg) at b: between link a->b and the arm piv->b (90 = ideal)."""
    u = (b[0] - a[0], b[1] - a[1])
    v = (b[0] - piv[0], b[1] - piv[1])
    cs = (u[0] * v[0] + u[1] * v[1]) / (math.hypot(*u) * math.hypot(*v))
    return math.degrees(math.acos(max(-1, min(1, cs))))


def _seg_pt(a, b, p):
    ax, az = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((p[0] - a[0]) * ax + (p[1] - a[1]) * az) / (ax * ax + az * az)))
    return dist(p, (a[0] + t * ax, a[1] + t * az))


EAR_R = 4.0                          # boss radius round an ear pin
PAD_M1 = ((-8.0, 9.5), (8.0, 20.0))  # where the M1 ear joins the middle (x, dz from PIP): its own footprint
PAD_D1 = ((-8.0, 9.5), (8.0, 14.0))  # where the D1 ear joins the distal (from DIP)
PAD_P1 = ((-8.0, -20.0), (8.0, -9.5))  # where the P1 ear joins the proximal (from PIP)


def _hull(pts):
    pts = sorted(set(pts))
    lo, hi = [], []
    for seq, out in ((pts, lo), (pts[::-1], hi)):
        for p in seq:
            while len(out) >= 2 and ((out[-1][0] - out[-2][0]) * (p[1] - out[-2][1])
                                     - (out[-1][1] - out[-2][1]) * (p[0] - out[-2][0])) <= 0:
                out.pop()
            out.append(p)
    return lo[:-1] + hi[:-1]


def ear(pin, pad, r=EAR_R, n=24):
    """Ear outline (local frame): hull of the pin boss and the pad it is joined on."""
    (x0, z0), (x1, z1) = pad
    circ = [(pin[0] + r * math.cos(2 * math.pi * k / n), pin[1] + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
    return _hull(circ + [(x0, z0), (x1, z0), (x1, z1), (x0, z1)])


def poly_dist(poly, p):
    inside = all((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= 0 for a, b in zip(poly, poly[1:] + poly[:1]))
    if inside:
        return 0.0
    return min(_seg_pt(a, b, p) for a, b in zip(poly, poly[1:] + poly[:1]))


def seg_seg(a, b, c, d):
    return min(_seg_pt(a, b, c), _seg_pt(a, b, d), _seg_pt(c, d, a), _seg_pt(c, d, b))


def to_local(p, frame):
    return rot((p[0] - frame[0][0], p[1] - frame[0][1]), -frame[1])


def metrics(q=P, ln=None):
    sw = sweep(q, ln)
    if sw is None:
        return None
    ta, rod_mcp, m1_p1, rod_l2, l2_lhead, l2_zmin = [], 1e9, 1e9, 1e9, 1e9, 1e9
    ear_m1, ear_d1, ear_p1 = ear(q['M1'], PAD_M1), ear(q['D1'], PAD_D1), ear(q['P1'], PAD_P1)
    for phi, (t1, t2, t3) in sw:
        f = frames(t1, t2, t3)
        h, Lw = horn_pt(phi, q), world(q['L'], f[0])
        m1, p1, d1 = world(q['M1'], f[1]), world(p1loc(q), f[0]), world(q['D1'], f[2])
        ta += [_tang(h, Lw, MCP), _tang(q['B0'], m1, f[1][0]), _tang(p1, d1, f[2][0]), _tang(Lw, h, SERVO)]
        rod_mcp = min(rod_mcp, _seg_pt(h, Lw, MCP))          # MCP pin barb (r 2) sits in the rod layer
        # P1 and D1 ears share y 9.3 .. 14.0 (+Y): distal-frame P1 ear corners vs the D1 ear, and back
        pe = [to_local(world(add((0, L_PROX), v), f[0]), f[2]) for v in ear_p1]
        m1_p1 = min(m1_p1, min(poly_dist(ear_d1, v) for v in pe), min(poly_dist(pe, v) for v in ear_d1))
        rod_l2 = min(rod_l2, seg_seg(h, Lw, p1, d1))          # rod and DIP link share y 14.3 .. 16.6
        l2_lhead = min(l2_lhead, _seg_pt(p1, d1, Lw))         # L pin head (+Y) vs the DIP link
        l2_zmin = min(l2_zmin, _seg_pt(p1, d1, SERVO))       # DIP link (y 14.3 .. 17.3) vs the horn + hand lever
    t = sw[-1][1]
    return dict(mcp=math.degrees(t[0]), pip=math.degrees(t[1]), dip=math.degrees(t[2]),
                tmin=min(min(ta), 180 - max(ta)), rod_mcp=rod_mcp, m1_p1=m1_p1, rod_l2=rod_l2,
                l2_lhead=l2_lhead, l2_zmin=l2_zmin,
                # an ear may cover its joint's pin end (pocket r 3.0 round the axis); its own pin hole (r 1.7) keeps
                # 1.0 of wall to that pocket
                ear_r=min(math.hypot(*q['M1']), math.hypot(*q['P1']), math.hypot(*q['D1'])),
                stroke=sw[-1][0],
                mono=all(b[1][i] >= a[1][i] - 1e-6 for a, b in zip(sw, sw[1:]) for i in range(3))
                and all(b[0] > a[0] for a, b in zip(sw, sw[1:])))


def robust(q=P):
    """End angles with every length +-0.1 mm (one at a time): worst change per joint (deg)."""
    base = metrics(q)
    worst = {'pip': 0, 'dip': 0, 'stroke': 0}
    for k in ('rod', 'l1', 'l2'):
        for d in (-0.1, 0.1):
            ln = lengths(q)
            ln[k] += d
            m = metrics(q, ln)
            if m is None:
                return None
            for j in worst:
                worst[j] = max(worst[j], abs(m[j] - base[j]))
    return worst


def check(q=P):
    m = metrics(q)
    assert m is not None, 'a loop does not close over the stroke'
    assert m['mono'], 'not monotonic'
    assert 85 <= m['pip'] <= 95 and 62 <= m['dip'] <= 78 and 70 <= m['stroke'] <= 130, m
    assert m['tmin'] >= 30, m
    assert m['rod_mcp'] >= 6.3, m           # rod half width 3.5 + MCP barb r 2.0 + 0.8
    assert m['m1_p1'] >= 0.5, m             # P1 ear (proximal) vs D1 ear (distal), both +Y
    assert m['rod_l2'] >= 7.5, m            # rod / DIP link half widths 3.5 + 3.5 + 0.5
    assert m['l2_lhead'] >= 6.8, m          # DIP link half width 3.5 + L pin head r 2.75 + 0.5
    assert m['l2_zmin'] >= 28.0, m          # DIP link stays out of the horn layer's reach (lever r 22 + pad 5)
    assert m['ear_r'] >= 5.7, m             # ear pin hole 1.0 clear of the joint-pin pocket
    assert b0_ok(q) and lever_ok(q), (q['B0'], q['L'])
    r = robust(q)
    assert r is not None and max(r['pip'], r['dip']) <= 3.0 and r['stroke'] <= 3.0, r
    return m, r


KEYS = [('B0', 0), ('B0', 1), ('M1', 0), ('M1', 1), ('P1', 0), ('P1', 1), ('D1', 0), ('D1', 1), ('L', 0), ('L', 1),
        ('rh', None), ('phi0', None)]
BOUNDS = [(6, 17), (55, 75), (-14, 4), (-2, 14), (-4, 12), (-14, 10), (-14, 4), (-2, 13), (11, 16), (-4, 10),
          (6, 12), (-130, 30)]


def unpack(v, q0=P):
    q = dict(q0)
    for (k, i), x in zip(KEYS, v):
        if i is None:
            q[k] = x
        else:
            t = list(q[k])
            t[i] = x
            q[k] = tuple(t)
    return q


def b0_ok(q):
    """B0's barb pokes into the finger's width: it must stay outside the proximal's sweep (block half width 8,
    flexing away from it; barb r 2 + 0.3)."""
    dx, dz = q['B0'][0] - MCP[0], q['B0'][1] - MCP[1]
    r, a = math.hypot(dx, dz), math.degrees(math.atan2(dz, dx))
    return r >= 13.0 and a <= 90 - math.degrees(math.asin(8.0 / r)) - math.degrees(2.3 / r)


def lever_ok(q):
    """The L boss (r 4, y 9 .. 12.3) shares y with the +Y base cheek (x <= 10 below the MCP, round r 8 above)."""
    x, z = q['L']
    return math.hypot(x, z) >= 12.4 and (z >= 4.5 or x >= 14.3)


def cost(v):
    q = unpack(v)
    for x, (lo, hi) in zip(v, BOUNDS):
        if not lo <= x <= hi:
            return 1e6
    if not b0_ok(q) or not lever_ok(q):
        return 1e6
    m = metrics(q)
    if m is None:
        return 1e5
    c = (0 if m['mono'] else 500) + (m['pip'] - 90) ** 2 + (m['dip'] - 70) ** 2 + 0.05 * (m['stroke'] - 100) ** 2
    pen = [(40 - m['tmin'], 5), (7 - m['rod_mcp'], 20), (1.0 - m['m1_p1'], 20), (8.5 - m['rod_l2'], 20),
           (7.5 - m['l2_lhead'], 20), (29 - m['l2_zmin'], 20), (6.2 - m['ear_r'], 20)]
    return c + sum(w * max(0, x) ** 2 for x, w in pen)


def fit_links(starts=12, seed=1):
    """Nelder-Mead from random starts inside BOUNDS; targets MCP 80 / PIP 90 / DIP 70 at the end of the stroke."""
    import random
    from scipy.optimize import minimize
    rnd = random.Random(seed)
    best = None
    for k in range(starts):
        v0 = ([rnd.uniform(lo, hi) for lo, hi in BOUNDS] if k else [P[a][b] if b is not None else P[a] for a, b in KEYS])
        if cost(v0) >= 1e5:
            continue
        r = minimize(cost, v0, method='Nelder-Mead', options=dict(maxiter=3000, xatol=1e-3, fatol=1e-4))
        if best is None or r.fun < best[1]:
            best = (unpack(r.x), r.fun)
    return best


if __name__ == '__main__':
    import sys
    if 'fit' in sys.argv:
        q, f = fit_links()
        print('cost', f)
        for k in ('B0', 'M1', 'P1', 'D1', 'L', 'rh', 'phi0'):
            print(k, tuple(round(x, 2) for x in q[k]) if isinstance(q[k], tuple) else round(q[k], 2))
        print(metrics(q), robust(q))
    else:
        m, r = check()
        print('lengths', {k: round(v, 3) for k, v in lengths().items()})
        print('end', {k: round(v, 2) if isinstance(v, float) else v for k, v in m.items()}, 'robust', {k: round(v, 2) for k, v in r.items()})
        for phi, t in sweep(n=10):
            print(f'horn {phi:6.1f}  MCP {math.degrees(t[0]):6.1f}  PIP {math.degrees(t[1]):6.1f}  DIP {math.degrees(t[2]):6.1f}')
