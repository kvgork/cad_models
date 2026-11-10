"""How the link lengths set the jaw opening and the forward (feed) stroke of the gripper.

    python3 strandbeest_gripper/tools/jaw_relations.py

Model: two mirrored Jansen legs, mirror line at y = YM (half the crank-to-crank distance).
Foot point F of leg 1 at height y(theta); jaw thickness = PAD_D.

    gap(theta)  = 2 * (|YM| - |y(theta)|) - PAD_D           (both jaws move by the same amount)
    clamp gap   = 2 * (|YM| - |y_min|) - PAD_D               set by the gear distance, not by the legs
    max gap     = clamp gap + 2 * H,   H = step height of the foot path (max y - min y)
    feed stroke = x-travel of F while the gap is within TOL of the clamp gap (the flat part of the loop)

So the legs fix the *opening* (2 H) and the *stroke*; the gear distance only shifts the clamp gap.
Everything scales linearly with the scale factor S. The script prints, at the holy numbers:
  - H, stroke and full stride per unit of S, checked against the verified v4b/v5 numbers;
  - the sensitivity (elasticity) of H and stroke to each link: % change of H per % change of the link;
  - a sweep of the crank length m alone (the practical knob).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jansen import HOLY, BRANCH, circ  # noqa: E402

TOL = 0.4          # gap within this of the clamp gap counts as "clamped" (same as verify_v3.py)


def pose_L(theta, L):
    b1, b2, b3, b4, b5 = BRANCH
    G = (-L['a'], -L['l'])
    J1 = (L['m'] * math.cos(theta), L['m'] * math.sin(theta))
    J2 = circ(J1, L['j'], G, L['b'], b1)
    J3 = J2 and circ(J2, L['e'], G, L['d'], b2)
    J4 = circ(J1, L['k'], G, L['c'], b3)
    J5 = J3 and J4 and circ(J3, L['f'], J4, L['g'], b4)
    return J5 and circ(J4, L['i'], J5, L['h'], b5)


def metrics(L, n=1440, tol=TOL):
    F = []
    for k in range(n):
        p = pose_L(2 * math.pi * k / n, L)
        if p is None:
            return None
        F.append(p)
    ys = [p[1] for p in F]
    xs = [p[0] for p in F]
    ymin = min(ys)
    H = max(ys) - ymin
    flat = [p[0] for p in F if p[1] - ymin <= tol / 2]      # each jaw within TOL/2 -> gap within TOL
    stroke = max(flat) - min(flat)
    return dict(H=H, stroke=stroke, stride=max(xs) - min(xs), ymin=ymin)


def main():
    S = 0.4
    base = metrics(HOLY, tol=TOL / S)             # same tolerance relative to size as 0.4 mm at S = 0.4
    print('Holy numbers, scale 1 (per unit S):')
    print(f"  step height H = {base['H']:.2f}   -> opening 2H = {2 * base['H']:.2f} x S")
    print(f"  feed stroke (gap within {TOL / S:.1f} x S of the clamp gap) = {base['stroke']:.2f} x S")
    print(f"  lowest foot point |y_min| = {-base['ymin']:.2f} x S")
    print(f"  => clamp gap = D - {-2 * base['ymin']:.1f} S - pad ;  max gap = D - {-2 * base['ymin'] - 2 * base['H']:.1f} S - pad  (D = crank-to-crank distance)")
    print(f"  full stride  = {base['stride']:.2f} x S")
    sc = metrics({k: v * S for k, v in HOLY.items()})
    print(f'At S = {S} (v4b / v5): opening 2H = {2 * sc["H"]:.2f} mm (verified: 19.50 - 1.53 = 17.97), '
          f'feed stroke {sc["stroke"]:.1f} mm (verified 19.9), full stride {sc["stride"]:.1f} mm')
    print('\nElasticity at S = 0.4 (% change of H / stroke per +1 % of one link, others fixed):')
    print(f"  {'link':5s} {'length':>7s} {'dH %':>7s} {'dStroke %':>10s}")
    rows = []
    for k in HOLY:
        L = {kk: v * S for kk, v in HOLY.items()}
        L[k] *= 1.01
        m = metrics(L)
        if m is None:
            rows.append((k, None, None))
            continue
        rows.append((k, 100 * (m['H'] / sc['H'] - 1), 100 * (m['stroke'] / sc['stroke'] - 1)))
    for k, dh, ds in sorted(rows, key=lambda r: -abs(r[1] or 99)):
        print(f"  {k:5s} {HOLY[k] * S:7.2f} {dh:+7.2f} {ds:+10.2f}" if dh is not None else f"  {k:5s}   does not close")
    print('\nCrank length m alone (other links at S = 0.4):')
    print(f"  {'m (mm)':>7s} {'2H (mm)':>8s} {'stroke':>7s}")
    for f in (0.8, 0.9, 1.0, 1.1, 1.2, 1.3):
        L = {kk: v * S for kk, v in HOLY.items()}
        L['m'] *= f
        m = metrics(L)
        print(f"  {L['m']:7.2f} " + (f"{2 * m['H']:8.2f} {m['stroke']:7.1f}" if m else '  linkage does not close'))
    print('\nHow far one link can change before the leg no longer closes over a full turn:')
    for k in ('m', 'k', 'c', 'j', 'e', 'h'):
        up, dn = limit(k)
        print(f"  {k}: {100 * (dn - 1):+.1f} % .. {100 * (up - 1):+.1f} %")


def limit(key, S=0.4):
    """Largest and smallest factor on one link for which the linkage still closes over a full turn."""
    out = []
    for lo, hi in ((1.0, 2.0), (1.0, 0.3)):
        for _ in range(30):
            mid = (lo + hi) / 2
            L = {k: v * S for k, v in HOLY.items()}
            L[key] *= mid
            if metrics(L, n=720):
                lo = mid
            else:
                hi = mid
        out.append(lo)
    return out


if __name__ == '__main__':
    main()
