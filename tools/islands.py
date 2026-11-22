"""Voxel check for layer islands with nothing below them (what Bambu Studio calls "floating regions").

    python3 tools/islands.py <part.stl> [dx dy dz]      (run from the repo root; d = model direction facing the bed,
                                                          as in print_orient.json; default: the STL as it lies)

Prints each island (layer z, cells, x/y range in the bed frame, origin at the part's min corner). 0.25 mm grid,
0.2 mm layers: a quick way to find which feature the slicer means (articulated_finger v1, 2026-11-22).
"""
import sys, numpy as np
sys.path.insert(0, 'tools')
import plates
T = plates.read_stl(sys.argv[1]).astype(float)
if len(sys.argv) > 2:
    d = np.array([float(v) for v in sys.argv[2:5]])
    R = plates.rot_to(d, np.array([0, 0, -1.0]))
    T = T @ np.array(R).T
T -= T.reshape(-1, 3).min(0)
h = 0.25
mx = T.reshape(-1, 3).max(0)
xs = np.arange(h / 2, mx[0], h); ys = np.arange(h / 2, mx[1], h)
nz = int(mx[2] / 0.2) + 1
occ = np.zeros((len(xs), len(ys), nz), bool)
A, B, C = T[:, 0], T[:, 1], T[:, 2]
for i, x in enumerate(xs):
    for j, y in enumerate(ys):
        # barycentric in XY
        v0 = B[:, :2] - A[:, :2]; v1 = C[:, :2] - A[:, :2]; v2 = np.array([x, y]) - A[:, :2]
        den = v0[:, 0] * v1[:, 1] - v1[:, 0] * v0[:, 1]
        ok = np.abs(den) > 1e-12
        u = np.where(ok, (v2[:, 0] * v1[:, 1] - v1[:, 0] * v2[:, 1]) / np.where(ok, den, 1), -1)
        v = np.where(ok, (v0[:, 0] * v2[:, 1] - v2[:, 0] * v0[:, 1]) / np.where(ok, den, 1), -1)
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1)
        if not hit.any():
            continue
        z = np.sort(A[hit, 2] + u[hit] * (B[hit, 2] - A[hit, 2]) + v[hit] * (C[hit, 2] - A[hit, 2]))
        z = np.unique(np.round(z, 4))
        for a, b in zip(z[0::2], z[1::2]):
            occ[i, j, int(a / 0.2 + 0.5):int(b / 0.2 + 0.5)] = True
from collections import deque
for k in range(1, nz):
    L = occ[:, :, k]; seen = np.zeros_like(L)
    for i0, j0 in zip(*np.nonzero(L)):
        if seen[i0, j0]:
            continue
        q = deque([(i0, j0)]); seen[i0, j0] = True; cells = []
        while q:
            i, j = q.popleft(); cells.append((i, j))
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                a, b = i + di, j + dj
                if 0 <= a < L.shape[0] and 0 <= b < L.shape[1] and L[a, b] and not seen[a, b]:
                    seen[a, b] = True; q.append((a, b))
        if not any(occ[i, j, k - 1] for i, j in cells):
            c = np.array(cells)
            print(f'island z {k * 0.2:.1f}: {len(cells)} cells, x {xs[c[:, 0].min()]:.1f}..{xs[c[:, 0].max()]:.1f} y {ys[c[:, 1].min()]:.1f}..{ys[c[:, 1].max()]:.1f}')
