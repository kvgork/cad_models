#!/usr/bin/env python3
"""A4 sorting sheet: the 1:1 outline of every printed part, with its part number, name and quantity.
Print it at 100 % (no "fit to page"), lay the printed parts on their outlines, and build from there.

    python3 tools/sortsheet.py strandbeest_gripper/v6_mirror-legs     (one or more folders)

Output: <folder>/docs/<ASSY-PN>_<name>_sort-sheet_A4.pdf (several pages if needed). Each part is shown
lying in its print orientation (the same as the plate file), seen from above: grey = the part's
outline, dark line = the face that lies on the table. Mirror parts (UP1/UP2) show as mirror images,
so they can't be mixed up. A 50 mm bar on every page checks the print scale.
"""
import glob
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plates  # noqa: E402
import printlist  # noqa: E402

ROOT = printlist.ROOT
PAGE_W, PAGE_H = 210.0, 297.0
MARGIN = 10.0
HEADER = 22.0
GAP = 4.0
LABEL_H = 9.0          # two text lines under each part
CHAR_W = 1.45          # mm per character at the label font size (7 pt)


def boundary_edges(tris2d):
    """Edges used by exactly one triangle: the outline (with holes) of a flat face set."""
    count = {}
    for t in tris2d:
        pts = [tuple(np.round(p, 4)) for p in t]
        for a, b in ((0, 1), (1, 2), (2, 0)):
            e = tuple(sorted((pts[a], pts[b])))
            count[e] = count.get(e, 0) + 1
    return [e for e, n in count.items() if n == 1]


def lay_low(tris):
    """Tall, slender parts (a pin printed standing) are shown lying down: the hull face that gives the
    lowest height, then the smallest footprint rectangle, as plates.lay_flat does."""
    from scipy.spatial import ConvexHull
    pts = tris.reshape(-1, 3)
    hull = ConvexHull(pts)
    best = None
    for eq in hull.equations:
        n = eq[:3] / np.linalg.norm(eq[:3])
        hgt = (pts @ n).max() - (pts @ n).min()
        if best is None or hgt < best[0] - 1e-6:
            best = (hgt, n)
    r = plates.rot_to(best[1], np.array([0.0, 0.0, -1.0]))
    p = pts @ r.T
    xy = p[ConvexHull(p[:, :2]).vertices, :2]
    ba, bar = 0.0, None
    for deg in np.arange(0, 180, 1.0):
        t = np.radians(deg)
        q = xy @ np.array([[np.cos(t), np.sin(t)], [-np.sin(t), np.cos(t)]])
        w, h = q.max(0) - q.min(0)
        if bar is None or w * h < bar:
            ba, bar = t, w * h
    rz = np.array([[np.cos(ba), -np.sin(ba), 0], [np.sin(ba), np.cos(ba), 0], [0, 0, 1]])
    p = p @ rz.T
    p -= p.min(0)
    if p[:, 1].max() > p[:, 0].max():
        p = p[:, [1, 0, 2]] * [1, -1, 1]
        p -= p.min(0)
    return p.reshape(-1, 3, 3)


def part_items(folder):
    exports = os.path.join(ROOT, folder, 'exports')
    stls = {printlist.STL_RE.match(os.path.basename(p)).group(1): p
            for p in sorted(glob.glob(os.path.join(exports, '*.stl')))}
    assy = printlist.assembly_counts(os.path.join(ROOT, folder, 'cad'))
    n = assy[1] if assy else {pn: 1 for pn in stls}
    stem = assy[0][:-5] if assy else os.path.basename(folder)
    reg = printlist.parts.register()
    items = []
    for pn, path in stls.items():
        t = plates.lay_flat(plates.read_stl(path))
        if t[..., 2].max() > 1.5 * max(t[..., 0].max(), t[..., 1].max()):    # printed standing: show it lying
            t = lay_low(plates.read_stl(path))
        r = reg.get(pn, {})
        rev = re.search(r'_([A-Z0-9]+)\.stl$', path).group(1)
        lines = [f"{pn}  {r.get('Name', '?')}  {rev}",
                 f"x{n[pn]}   {r.get('Material / process', '?').split(',')[0]}"]
        w, h = t[..., 0].max(), t[..., 1].max()
        cw = max(w, max(len(s) for s in lines) * CHAR_W)
        items.append(dict(pn=pn, tris=t, w=w, h=h, cw=cw, ch=h + LABEL_H, lines=lines))
    return stem, items


def paginate(items):
    usable_w = PAGE_W - 2 * MARGIN
    usable_h = PAGE_H - 2 * MARGIN - HEADER
    pages, cur, x, y, row_h = [], [], 0.0, 0.0, 0.0
    for it in sorted(items, key=lambda i: (-i['ch'], i['pn'])):
        if it['cw'] > usable_w or it['ch'] > usable_h:
            raise SystemExit(f"{it['pn']}: {it['w']:.0f} x {it['h']:.0f} mm does not fit an A4 page")
        if x + it['cw'] > usable_w:                     # next row
            x, y, row_h = 0.0, y + row_h + GAP, 0.0
        if y + it['ch'] > usable_h:                     # next page
            pages.append(cur)
            cur, x, y, row_h = [], 0.0, 0.0, 0.0
        cur.append((it, MARGIN + x, PAGE_H - MARGIN - HEADER - y))
        x += it['cw'] + GAP
        row_h = max(row_h, it['ch'])
    if cur:
        pages.append(cur)
    return pages


def render(folder, stem, pages, title):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.collections import LineCollection, PolyCollection
    out = os.path.join(ROOT, folder, 'docs', f'{stem}_sort-sheet_A4.pdf')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with PdfPages(out, metadata={'Title': f'{stem} sorting sheet', 'Creator': 'cad_models tools/sortsheet.py',
                                 'CreationDate': None, 'ModDate': None}) as pdf:
        for k, page in enumerate(pages, 1):
            fig = plt.figure(figsize=(PAGE_W / 25.4, PAGE_H / 25.4))
            ax = fig.add_axes([0, 0, 1, 1])             # 1 data unit = 1 mm on paper
            ax.set_xlim(0, PAGE_W)
            ax.set_ylim(0, PAGE_H)
            ax.set_aspect('equal')
            ax.axis('off')
            top = PAGE_H - MARGIN
            ax.text(MARGIN, top - 3, title[0], fontsize=10, weight='bold', va='top')
            ax.text(MARGIN, top - 8, title[1], fontsize=7, va='top')
            ax.text(MARGIN, top - 12.5, f'Sorting sheet, page {k}/{len(pages)}. Print at 100 % (no "fit to page"); '
                    'lay each part on its outline. Seen from above, as printed.', fontsize=6, va='top')
            # 50 mm scale check
            x0, yb = PAGE_W - MARGIN - 50, top - 3
            ax.plot([x0, x0 + 50], [yb, yb], color='black', lw=1.2)
            for xx in (x0, x0 + 50):
                ax.plot([xx, xx], [yb - 1.5, yb + 1.5], color='black', lw=1.2)
            ax.text(x0 + 25, yb - 2, 'this bar must measure 50 mm', fontsize=6, ha='center', va='top')
            for it, x, y in page:
                t = it['tris']
                # place: part top-left at (x, y), label under it
                ox, oy = x, y - it['h']
                xy = t[..., :2] + [ox, oy]
                ax.add_collection(PolyCollection(xy, facecolors='#d9d9d9', edgecolors='#d9d9d9', linewidths=0.15))
                bottom = t[np.all(np.abs(t[..., 2]) < 0.02, axis=1)]
                if len(bottom):
                    segs = [[(a[0] + ox, a[1] + oy), (b[0] + ox, b[1] + oy)] for a, b in boundary_edges(bottom[..., :2])]
                    ax.add_collection(LineCollection(segs, colors='#333333', linewidths=0.35))
                ax.text(x, oy - 1.5, it['lines'][0], fontsize=7, weight='bold', va='top')
                ax.text(x, oy - 5.2, it['lines'][1], fontsize=7, va='top')
            pdf.savefig(fig)
            plt.close(fig)
    return out


def main(argv):
    for folder in [a.rstrip('/') for a in argv]:
        stem, items = part_items(folder)
        if not items:
            continue
        reg = printlist.parts.register()
        pn = stem.split('_')[0]
        title = (stem, reg.get(pn, {}).get('Description', folder))
        pages = paginate(items)
        out = render(folder, stem, pages, title)
        print(f'{os.path.relpath(out, ROOT)}: {len(items)} parts on {len(pages)} page(s)')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
