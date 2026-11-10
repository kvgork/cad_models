#!/usr/bin/env python3
"""Make ready-to-slice build plates: every printed part of a product/version, in the right
quantity, laid flat in its print orientation and packed onto the bed. One .3mf per plate,
which you open directly in Bambu Studio / OrcaSlicer / PrusaSlicer.

    python3 tools/plates.py strandbeest_gripper/v4b_snap-pins            # 256 x 256 bed (X1, P1, A1)
    python3 tools/plates.py strandbeest_gripper/v4b_snap-pins --bed 180  # A1 mini

Output: <folder>/exports/plates/<ASSY-PN>_<name>_plate<N>-<material>_<REV>.3mf plus a top-view PNG per plate.
Normal (rigid) prints and TPU prints always go on separate plates (material from PARTS.md).
Quantities come from tools/printlist.py (the assembly's components, purchased parts left out).

Orientation: the part rests on the largest flat face of its convex hull ("lay on face"). That
puts links, gears and plates on their flat side, D-flat pins on their flat, and a headed pin
without a flat on its head. Check each part in the slicer before printing: this is a heuristic.
"""
import glob
import json
import os
import re
import struct
import sys
import zipfile

import numpy as np
from scipy.spatial import ConvexHull

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import printlist  # noqa: E402

ROOT = printlist.ROOT
GAP = 4.0          # mm between parts
MARGIN = 8.0       # mm from the bed edge


def read_stl(path):
    data = open(path, 'rb').read()
    if len(data) >= 84:
        n = struct.unpack('<I', data[80:84])[0]
        if 84 + 50 * n == len(data):
            rec = np.frombuffer(data[84:], dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))
            return rec['v'].astype(float)
    pts = [list(map(float, m)) for m in re.findall(rb'vertex\s+(\S+)\s+(\S+)\s+(\S+)', data)]
    return np.array(pts, dtype=float).reshape(-1, 3, 3)


def rot_to(a, b):
    """Rotation matrix turning unit vector a onto unit vector b."""
    v, c = np.cross(a, b), float(np.dot(a, b))
    if c < -0.999999:
        axis = np.cross(a, [1, 0, 0]) if abs(a[0]) < 0.9 else np.cross(a, [0, 1, 0])
        axis /= np.linalg.norm(axis)
        return 2 * np.outer(axis, axis) - np.eye(3)
    k = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + k + k @ k / (1 + c)


def lay_flat(tris):
    """Rotate so the largest convex-hull face is on the bed, then turn about Z to the smallest
    footprint rectangle. Returns triangles with min corner at the origin."""
    pts = tris.reshape(-1, 3)
    hull = ConvexHull(pts)
    planes = {}
    for simplex, eq in zip(hull.simplices, hull.equations):
        a, b, c = pts[simplex]
        area = np.linalg.norm(np.cross(b - a, c - a)) / 2
        key = tuple(np.round(eq, 3))
        planes[key] = planes.get(key, 0.0) + area
    # among the 12 biggest hull planes, pick the one with the most real face area on it
    # (a hull plane can span a recess; only faces that touch the bed hold the part)
    nrm = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    tri_area = np.linalg.norm(nrm, axis=1) / 2

    def contact(plane):
        n, d = np.array(plane[:3]), plane[3]
        on = np.all(np.abs(tris @ n + d) < 0.02, axis=1)
        return tri_area[on].sum()
    cands = sorted(planes, key=planes.get, reverse=True)[:12]
    best = max(cands, key=lambda k: (round(contact(k), 1), k[2] < 0))   # tie: keep the modelled bottom
    r = rot_to(np.array(best[:3]) / np.linalg.norm(best[:3]), np.array([0.0, 0.0, -1.0]))
    p = pts @ r.T
    xy = p[ConvexHull(p[:, :2]).vertices, :2]
    best_a, best_area = 0.0, None
    for deg in np.arange(0, 180, 1.0):
        t = np.radians(deg)
        q = xy @ np.array([[np.cos(t), np.sin(t)], [-np.sin(t), np.cos(t)]])
        w, h = q.max(0) - q.min(0)
        if best_area is None or w * h < best_area - 1e-6:
            best_a, best_area = t, w * h
    rz = np.array([[np.cos(best_a), -np.sin(best_a), 0], [np.sin(best_a), np.cos(best_a), 0], [0, 0, 1]])
    p = p @ rz.T
    p -= p.min(0)
    w, h = p[:, 0].max(), p[:, 1].max()
    if h > w:                                   # long side along X: packs better on shelves
        p = p[:, [1, 0, 2]] * [1, -1, 1]        # (x, y) -> (y, -x): a 90 deg turn, not a mirror
        p -= p.min(0)
    return p.reshape(-1, 3, 3)


def pack(items, bed):
    """Shelf packing. items: [(name, tris)] with tris at the origin. Returns plates of
    [(name, tris moved)]."""
    usable = bed - 2 * MARGIN
    items = sorted(items, key=lambda it: (-it[1][..., 1].max(), -it[1][..., 0].max()))
    plates = []
    for name, tris in items:
        w, h = tris[..., 0].max(), tris[..., 1].max()
        if w > usable or h > usable:
            raise SystemExit(f'{name}: {w:.0f} x {h:.0f} mm does not fit a {bed:.0f} mm bed')
        placed = False
        for plate in plates:
            for shelf in plate['shelves']:
                if shelf['x'] + w <= usable and h <= shelf['h']:
                    plate['parts'].append((name, tris + [MARGIN + shelf['x'], MARGIN + shelf['y'], 0]))
                    shelf['x'] += w + GAP
                    placed = True
                    break
            if not placed and plate['top'] + h <= usable:
                plate['shelves'].append({'y': plate['top'], 'h': h, 'x': w + GAP})
                plate['parts'].append((name, tris + [MARGIN, MARGIN + plate['top'], 0]))
                plate['top'] += h + GAP
                placed = True
            if placed:
                break
        if not placed:
            plates.append({'shelves': [{'y': 0.0, 'h': h, 'x': w + GAP}], 'top': h + GAP,
                           'parts': [(name, tris + [MARGIN, MARGIN, 0])]})
    for plate in plates:                          # centre the block on the bed
        allp = np.concatenate([t.reshape(-1, 3) for _, t in plate['parts']])
        lo, hi = allp.min(0), allp.max(0)
        shift = [(bed - (hi[0] - lo[0])) / 2 - lo[0], (bed - (hi[1] - lo[1])) / 2 - lo[1], 0]
        plate['parts'] = [(n, t + shift) for n, t in plate['parts']]
    return [p['parts'] for p in plates]


def write_3mf(path, parts):
    objs, items = [], []
    for i, (name, tris) in enumerate(parts, 1):
        v, idx = np.unique(np.round(tris.reshape(-1, 3), 5), axis=0, return_inverse=True)
        f = idx.reshape(-1, 3)
        f = f[(f[:, 0] != f[:, 1]) & (f[:, 1] != f[:, 2]) & (f[:, 0] != f[:, 2])]
        vs = ''.join(f'<vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x, y, z in v)
        ts = ''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in f)
        objs.append(f'<object id="{i}" name="{name}" type="model"><mesh><vertices>{vs}</vertices>'
                    f'<triangles>{ts}</triangles></mesh></object>')
        items.append(f'<item objectid="{i}"/>')
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n'
             '<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
             '<metadata name="Application">cad_models tools/plates.py</metadata>'
             f'<resources>{"".join(objs)}</resources><build>{"".join(items)}</build></model>')
    ct = ('<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/'
          'package/2006/content-types"><Default Extension="rels" ContentType="application/'
          'vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" '
          'ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/'
            'package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in (('[Content_Types].xml', ct), ('_rels/.rels', rels), ('3D/3dmodel.model', model)):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))   # fixed: same plate -> same bytes
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)


def preview(path, parts, bed, title):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon, Rectangle
    fig, ax = plt.subplots(figsize=(6, 6), dpi=110)
    ax.add_patch(Rectangle((0, 0), bed, bed, fill=False, lw=1.5))
    for name, tris in parts:
        xy = tris.reshape(-1, 3)[:, :2]
        hull = xy[ConvexHull(xy).vertices]
        ax.add_patch(Polygon(hull, alpha=0.55))
        cx, cy = hull.mean(0)
        ax.text(cx, cy, name.split('_')[0][5:], ha='center', va='center', fontsize=6)
    ax.set_xlim(-5, bed + 5)
    ax.set_ylim(-5, bed + 5)
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=9)
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)


def plate_material(m):
    """Plate group: flexible filament (TPU/TPE) always on its own plate; rigid parts share one.
    'PETG/ASA' and 'PLA/PETG' mean either is fine, so they print with the PETG parts."""
    m = m.split(',')[0].strip()
    if 'TPU' in m or 'TPE' in m:
        return m
    return 'PETG' if 'PETG' in m else m


def main(argv):
    bed = 256.0
    if '--bed' in argv:
        i = argv.index('--bed')
        bed = float(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    for folder in [a.rstrip('/') for a in argv]:
        exports = os.path.join(ROOT, folder, 'exports')
        assy = printlist.assembly_counts(os.path.join(ROOT, folder, 'cad'))
        stls = {printlist.STL_RE.match(os.path.basename(p)).group(1): p
                for p in sorted(glob.glob(os.path.join(exports, '*.stl')))}
        if not stls:
            continue
        if assy:
            src, n = assy
            stem = src[:-5]
            cmds = json.load(open(os.path.join(ROOT, folder, 'cad', src), encoding='utf-8'))
            meta = next((c['params'].get('values', {}) for c in cmds if c.get('command') == 'document.metadata.set'), {})
            rev = meta.get('revision', 'X1')            # the assembly's revision, not one part's
        else:
            n = {pn: 1 for pn in stls}
            stem, rev = os.path.basename(folder), 'X1'
        reg = printlist.parts.register()
        groups = {}                               # material -> items: one material per plate
        for pn in sorted(stls):
            mat = plate_material(reg.get(pn, {}).get('Material / process', '?'))
            flat = lay_flat(read_stl(stls[pn]))
            base = os.path.basename(stls[pn])[:-4]
            groups.setdefault(mat, []).extend((f'{base}#{k + 1}', flat) for k in range(n[pn]))
        out = os.path.join(exports, 'plates')
        os.makedirs(out, exist_ok=True)
        for old in glob.glob(os.path.join(out, f'{stem}_plate*')):
            os.remove(old)
        k = 0
        for mat, items in groups.items():
            slug = re.sub(r'[^a-z0-9]+', '-', mat.lower()).strip('-')
            plates = pack(items, bed)
            for i, parts in enumerate(plates, 1):
                k += 1
                path = os.path.join(out, f'{stem}_plate{k}-{slug}_{rev}.3mf')
                write_3mf(path, parts)
                preview(path[:-4] + '.png', parts, bed, f'{stem} plate {k} ({mat}, {i}/{len(plates)}): {len(parts)} parts')
                print(f'{os.path.relpath(path, ROOT)}: {len(parts)} parts, {mat}')
        print(f'{folder}: {sum(len(v) for v in groups.values())} parts on {k} plate(s) of {bed:.0f} x {bed:.0f} mm')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
