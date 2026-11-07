"""Z-layer assignment for the planar Jansen finger stack.

Every link lives on one layer. A layer assignment is valid when, over the whole
crank range:
  - two links on the same layer never come closer than BAR_W + CLR in plane;
  - a pin column passing through an intermediate layer (spacer tube, OD 6) never
    comes within reach of a link on that layer;
  - the M3 nut on top of a column (layer above its top link) and the screw head
    under it (layer below its bottom link) never come within reach of a link on
    those layers;
  - the frame post at G (from the base plate up to the lowest G link) is clear of
    links on the layers it passes.
Prints the assignment with the fewest layers.

    python3 layers.py [theta_min theta_max]      (default: full turn)
"""
import itertools
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from jansen import pose  # noqa: E402

S = 0.4
BAR_W = 7.0
CLR = 1.0
SPACER_R = 3.2        # spacer tube OD 6 + clearance
NUT_R = 3.4           # M3 nyloc 6.4 across corners / 2 + 0.2
HEAD_R = 3.0          # M3 socket head 5.5 / 2 + 0.25
POST_R = 3.5

BODIES = {'crank': ['O', 'J1'], 'j': ['J1', 'J2'], 'k': ['J1', 'J4'], 'c': ['G', 'J4'],
          'bde': ['G', 'J2', 'J3'], 'f': ['J3', 'J5'], 'ghi': ['J4', 'J5', 'F']}
PINS = {'J1': ['crank', 'j', 'k'], 'J2': ['j', 'bde'], 'J3': ['bde', 'f'],
        'J4': ['k', 'c', 'ghi'], 'J5': ['f', 'ghi'], 'G': ['bde', 'c']}


def _pt_seg(x, a, b):
    ax, ay = b[0] - a[0], b[1] - a[1]
    L = ax * ax + ay * ay
    t = 0 if L == 0 else max(0, min(1, ((x[0] - a[0]) * ax + (x[1] - a[1]) * ay) / L))
    return math.hypot(x[0] - a[0] - t * ax, x[1] - a[1] - t * ay)


def _cross(p, q, a, b):
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) - (B[1] - A[1]) * (C[0] - A[0])
    return ccw(p, q, a) * ccw(p, q, b) < 0 and ccw(a, b, p) * ccw(a, b, q) < 0


def _inside(pt, poly):
    if len(poly) < 3:
        return False
    s = None
    for i in range(3):
        a, b = poly[i], poly[(i + 1) % 3]
        c = (b[0] - a[0]) * (pt[1] - a[1]) - (b[1] - a[1]) * (pt[0] - a[0])
        if s is None:
            s = c > 0
        elif (c > 0) != s:
            return False
    return True


def _edges(poly):
    return [(poly[0], poly[1])] if len(poly) == 2 else [(poly[i], poly[(i + 1) % 3]) for i in range(3)]


def shape_dist(P, Q):
    """Distance between two link centre-line shapes (segment or triangle)."""
    if any(_inside(x, Q) for x in P) or any(_inside(x, P) for x in Q):
        return 0.0
    best = 1e9
    for a, b in _edges(P):
        for c, d in _edges(Q):
            if _cross(a, b, c, d):
                return 0.0
            best = min(best, _pt_seg(a, c, d), _pt_seg(b, c, d), _pt_seg(c, a, b), _pt_seg(d, a, b))
    return best


def pt_shape(x, P):
    if _inside(x, P):
        return 0.0
    return min(_pt_seg(x, a, b) for a, b in _edges(P))


def analyse(angles, s=S):
    poses = [pose(math.radians(t), s) for t in angles]
    names = list(BODIES)
    same_layer_conflict = set()
    for A, B in itertools.combinations(names, 2):
        for p in poses:
            if shape_dist([p[n] for n in BODIES[A]], [p[n] for n in BODIES[B]]) < BAR_W + CLR:
                same_layer_conflict.add((A, B))
                break
    near = {}       # (pin, body) -> closest approach of the pin centre to the body's centre line
    for P in PINS:
        for X in names:
            near[(P, X)] = min(pt_shape(p[P], [p[n] for n in BODIES[X]]) for p in poses)
    return same_layer_conflict, near


def valid(L, conflict, near, nl):
    if any(L[a] == L[b] for a, b in conflict):
        return False
    for P, owners in PINS.items():
        lo, hi = min(L[o] for o in owners), max(L[o] for o in owners)
        if P == 'G':
            lo_reach = 0                        # post comes up from the base plate under layer 0
        else:
            lo_reach = lo
        for X in BODIES:
            if X in owners:
                continue
            lx, d = L[X], near[(P, X)] - BAR_W / 2 - CLR
            if lo_reach <= lx < lo and P == 'G' and d < POST_R:
                return False
            if lo < lx < hi and d < SPACER_R:
                return False
            if lx == hi + 1 and d < NUT_R:
                return False
            # J1's head sits in a pocket under the crank; others hang below the bottom link
            if P not in ('J1', 'G') and lx == lo - 1 and d < HEAD_R:
                return False
    return True


def solve(conflict, near, max_layers=8):
    names = [n for n in BODIES if n != 'crank']
    for nl in range(3, max_layers + 1):
        best = None
        for combo in itertools.product(range(1, nl), repeat=len(names)):
            L = dict(zip(names, combo))
            L['crank'] = 0
            if not valid(L, conflict, near, nl):
                continue
            span = sum(max(L[o] for o in ow) - min(L[o] for o in ow) for ow in PINS.values())
            if best is None or span < best[0]:
                best = (span, L)
        if best:
            return nl, best[1]
    return None, None


if __name__ == '__main__':
    lo, hi = (float(sys.argv[1]), float(sys.argv[2])) if len(sys.argv) > 2 else (0.0, 359.0)
    n = int((hi - lo) / 1.0) + 1
    angles = [lo + i * (hi - lo) / (n - 1) for i in range(n)]
    conflict, near = analyse(angles)
    nl, L = solve(conflict, near)
    print('range %.0f..%.0f: %s layers %s' % (lo, hi, nl, L))
