#!/usr/bin/env python3
"""Make ready-to-slice build plates: every printed part of a product/version, in the right
quantity, laid flat in its print orientation and packed onto the bed. One Bambu Studio project
.3mf per plate (printer, plate type and filament from tools/printer.json) plus a top-view PNG.

    python3 tools/plates.py strandbeest_gripper/v4b_snap-pins            # printer.json printer (X2D)
    python3 tools/plates.py strandbeest_gripper/v4b_snap-pins --plain    # plain 3MF only, no Bambu Studio
    python3 tools/plates.py strandbeest_gripper/v4b_snap-pins --bed 180  # other square bed (implies no nozzle limits)

Output: <folder>/exports/plates/<ASSY-PN>_<name>_plate<N>-<material>_<REV>.3mf
Normal (rigid) prints and TPU prints always go on separate plates (material from PARTS.md).
Quantities come from tools/printlist.py (the assembly's components, purchased parts left out).

Placement: inside printer.json "printable" (the area every nozzle reaches; X2D x >= 20.5), edge_margin
from its edges, gap between parts, brim_room more around tall slender parts; the block is centred.
Each plate is sliced by the Bambu Studio CLI as a check: a refused slice stops the run, slicer
warnings (floating regions, cantilevers) are printed at the end.

Orientation: the part rests on the largest real flat face ("lay on face"), or on the direction given
in <folder>/print_orient.json. Check each part in the slicer before printing: this is a heuristic.
"""
import glob
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import uuid
import zipfile

import numpy as np
from scipy.spatial import ConvexHull

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import printlist  # noqa: E402

ROOT = printlist.ROOT
PRINTER = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'printer.json')))
GAP = float(PRINTER['gap'])             # mm between parts
BRIM = float(PRINTER.get('brim_room', 0))  # extra room around tall, slender parts (they get a brim)
MARGIN = float(PRINTER['edge_margin'])  # mm inside the printable area
AREA = [float(v) for v in PRINTER['printable']]   # x0, y0, x1, y1 that every nozzle reaches (X2D: x >= 20.5)


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


def orient_overrides(folder):
    """Optional <folder>/print_orient.json: {PN: [x, y, z]}, the model direction that faces the bed.
    For parts where the biggest flat face is the wrong one (e.g. an open cap that must print mouth down)."""
    path = os.path.join(ROOT, folder, 'print_orient.json')
    return {k: v for k, v in json.load(open(path)).items() if not k.startswith('_')} if os.path.exists(path) else {}


def lay_flat(tris, down=None):
    """Rotate so the largest convex-hull face is on the bed (or the given model direction `down`),
    then turn about Z to the smallest footprint rectangle. Returns triangles with min corner at the origin."""
    pts = tris.reshape(-1, 3)
    if down is not None:
        return _footprint(pts @ rot_to(np.array(down, float) / np.linalg.norm(down), np.array([0.0, 0.0, -1.0])).T)
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
    return _footprint(pts @ r.T)


def _footprint(p):
    """Turn about Z to the smallest footprint rectangle, long side along X, min corner at the origin."""
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


def pack(items, area):
    """Shelf packing inside area = [x0, y0, x1, y1] (minus MARGIN). items: [(name, tris)] with tris at
    the origin. Returns plates of [(name, tris moved)], each plate's block centred on the area."""
    x0, y0, x1, y1 = area
    usable_w, usable_h = x1 - x0 - 2 * MARGIN, y1 - y0 - 2 * MARGIN
    items = sorted(items, key=lambda it: (-it[1][..., 1].max(), -it[1][..., 0].max()))
    plates = []
    for name, tris in items:
        w, h, z = tris[..., 0].max(), tris[..., 1].max(), tris[..., 2].max()
        if z > 2 * min(w, h):                     # tall and slender: needs a brim, keep neighbours clear of it
            tris = tris + [BRIM, BRIM, 0]
            w, h = w + 2 * BRIM, h + 2 * BRIM
        if w > usable_w or h > usable_h:
            raise SystemExit(f'{name}: {w:.0f} x {h:.0f} mm does not fit the {usable_w:.0f} x {usable_h:.0f} mm printable area')
        placed = False
        for plate in plates:
            for shelf in plate['shelves']:
                if shelf['x'] + w <= usable_w and h <= shelf['h']:
                    plate['parts'].append((name, tris + [MARGIN + shelf['x'], MARGIN + shelf['y'], 0]))
                    shelf['x'] += w + GAP
                    placed = True
                    break
            if not placed and plate['top'] + h <= usable_h:
                plate['shelves'].append({'y': plate['top'], 'h': h, 'x': w + GAP})
                plate['parts'].append((name, tris + [MARGIN, MARGIN + plate['top'], 0]))
                plate['top'] += h + GAP
                placed = True
            if placed:
                break
        if not placed:
            plates.append({'shelves': [{'y': 0.0, 'h': h, 'x': w + GAP}], 'top': h + GAP,
                           'parts': [(name, tris + [MARGIN, MARGIN, 0])]})
    for plate in plates:                          # centre the block on the printable area
        allp = np.concatenate([t.reshape(-1, 3) for _, t in plate['parts']])
        lo, hi = allp.min(0), allp.max(0)
        shift = [x0 + (x1 - x0 - (hi[0] - lo[0])) / 2 - lo[0], y0 + (y1 - y0 - (hi[1] - lo[1])) / 2 - lo[1], 0]
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


def preview(path, parts, bed, title, area=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon, Rectangle
    fig, ax = plt.subplots(figsize=(6, 6), dpi=110)
    ax.add_patch(Rectangle((0, 0), bed, bed, fill=False, lw=1.5))
    if area is not None:                          # what every nozzle reaches (dashed)
        ax.add_patch(Rectangle((area[0], area[1]), area[2] - area[0], area[3] - area[1], fill=False, lw=0.8, ls='--', color='grey'))
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


# ---- Bambu Studio project file -------------------------------------------------------------
# A plain 3MF opens in Bambu Studio as "geometry only" with whatever printer is selected. To get a
# real project (printer, plate type, filament, plate 1), Bambu Studio's own CLI writes the file.
# Lessons (2026-11-15, Bambu Studio 02.09.01.70 snap):
#  - system presets use "inherits": flatten them, or the CLI silently keeps defaults (PETG came out PLA);
#  - the CLI-exported project has an empty <plate>: add one <model_instance> per object, or it reloads as "empty";
#  - PETG / TPU on the default Cool Plate fails validation: set curr_bed_type;
#  - the snap only reads files under ~ (not /mnt): stage in ~/snap/bambu-studio/common/;
#  - every plate is sliced from the plain 3MF with the same presets: return_code 0 = Bambu accepts it.
WARNINGS = []                                     # Bambu slicer warnings, printed at the end


def bambu_env():
    exe = shutil.which('bambu-studio')
    for d in ('~/snap/bambu-studio/current/.config/BambuStudio', '~/.config/BambuStudio'):
        sysdir = os.path.join(os.path.expanduser(d), 'system', 'BBL')
        if exe and os.path.isdir(sysdir):
            stage = os.path.expanduser('~/snap/bambu-studio/common/cad_models_plates' if '/snap/' in exe
                                       else '~/.cache/cad_models_plates')
            os.makedirs(stage, exist_ok=True)
            return exe, sysdir, stage
    return None


def flat_preset(sysdir, kind, name):
    path = os.path.join(sysdir, kind, f'{name}.json')
    if not os.path.exists(path):
        raise SystemExit(f'Bambu preset not found: {kind}/{name} (tools/printer.json)')
    d = json.load(open(path))
    if d.get('inherits'):
        base = flat_preset(sysdir, kind, d['inherits'])
        base.update(d)
        d = base
    d.pop('inherits', None)
    d['name'], d['from'] = name, 'system'
    return d


def bambu_run(env, args, tries=6):
    """Run the Bambu Studio CLI. It sometimes aborts with heap corruption (negative return code,
    "free(): unaligned chunk"; 3 of 4 runs on one TPU plate): retry those, never a real error."""
    exe, _, stage = env
    res = os.path.join(stage, 'result.json')
    for _ in range(tries):
        r = subprocess.run([exe] + args, cwd=stage, capture_output=True, text=True, timeout=600)
        out = json.load(open(res)) if os.path.exists(res) else {}
        if os.path.exists(res):
            os.remove(res)
        if r.returncode >= 0:
            break
    return r.returncode, out, r.stdout + r.stderr


def bambu_project(env, core, out, mat):
    """Convert a plain 3MF to a Bambu Studio project for printer.json; slice it to check. Returns (g, min)."""
    exe, sysdir, stage = env
    if mat not in PRINTER['filaments']:
        raise SystemExit(f'no Bambu filament preset for material {mat!r}: add it to tools/printer.json')
    proc = flat_preset(sysdir, 'process', PRINTER['process'])
    proc['curr_bed_type'] = PRINTER['bed_type']
    files = {'m.json': flat_preset(sysdir, 'machine', PRINTER['machine']), 'p.json': proc,
             'f.json': flat_preset(sysdir, 'filament', PRINTER['filaments'][mat])}
    for n, d in files.items():
        json.dump(d, open(os.path.join(stage, n), 'w'), indent=1)
    shutil.copy(core, os.path.join(stage, 'in.3mf'))
    common = ['--load-settings', 'm.json;p.json', '--load-filaments', 'f.json', '--arrange', '0', '--orient', '0']
    rc, res, log = bambu_run(env, common + ['--slice', '1', '--outputdir', stage, 'in.3mf'])
    plate = (res.get('sliced_plates') or [{}])[0]
    if rc != 0 or res.get('return_code') != 0:
        msg = [l for l in log.splitlines() if 'glfw' not in l][-3:]
        raise SystemExit(f'{os.path.relpath(out, ROOT)}: Bambu Studio refused to slice it: {res.get("error_string")} {msg}')
    if plate.get('warning_message'):              # e.g. floating regions: a print problem, reported, not fatal
        WARNINGS.append(f'{os.path.relpath(out, ROOT)}: {plate["warning_message"].strip()}')
    grams = sum(f.get('total_used_g', 0) for f in plate.get('filaments', []))
    minutes = plate.get('total_predication', 0) / 60
    for g in glob.glob(os.path.join(stage, '*.gcode')):
        os.remove(g)
    rc, res, log = bambu_run(env, common + ['--export-3mf', 'out.3mf', 'in.3mf'])
    if rc != 0 or res.get('return_code') != 0:
        raise SystemExit(f'{os.path.relpath(out, ROOT)}: Bambu Studio export failed: {res.get("error_string")}')
    normalise_project(os.path.join(stage, 'out.3mf'), out)
    return grams, minutes


def normalise_project(src, dst):
    """Add the plate's object list and make the file reproducible (fixed dates and zip times)."""
    zin = zipfile.ZipFile(src)
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as z:
        for it in sorted(zin.infolist(), key=lambda i: i.filename):
            data = zin.read(it.filename)
            if it.filename == 'Metadata/model_settings.config':
                s = data.decode()
                if '<model_instance>' not in s:
                    ids = re.findall(r'<object id="(\d+)">', s)
                    inst = ''.join(f'    <model_instance>\n      <metadata key="object_id" value="{i}"/>\n'
                                   f'      <metadata key="instance_id" value="0"/>\n'
                                   f'      <metadata key="identify_id" value="{1000 + k}"/>\n    </model_instance>\n'
                                   for k, i in enumerate(ids))
                    s = re.sub(r'(<plate>\n(?:    <metadata [^\n]*\n)*)', lambda m: m.group(1) + inst, s, count=1)
                # random per-part uuids -> stable ones from the part name, so the same plate gives the same bytes
                s = re.sub(r'(<part id="(\d+)" subtype="[^"]*" uuid=")[^"]+("[^>]*>\s*<metadata key="name" value="([^"]*)")',
                           lambda m: m.group(1) + str(uuid.uuid5(uuid.NAMESPACE_URL, f'cad_models/{m.group(4)}/{m.group(2)}')) + m.group(3), s)
                data = s.encode()
            elif it.filename == '3D/3dmodel.model':
                data = re.sub(rb'(<metadata name="(?:CreationDate|ModificationDate)">)[^<]*', rb'\g<1>2026-01-01', data)
            info = zipfile.ZipInfo(it.filename, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)


def main(argv):
    area = AREA
    if '--bed' in argv:                           # another printer: plain square bed, no nozzle limits
        i = argv.index('--bed')
        b = float(argv[i + 1])
        area = [0.0, 0.0, b, b]
        argv = argv[:i] + argv[i + 2:]
    plain = '--plain' in argv                     # only the plain 3MF (no Bambu Studio conversion)
    argv = [a for a in argv if a != '--plain']
    env = None if plain else bambu_env()
    if env is None and not plain:
        print('Bambu Studio not found: writing plain 3MF (opens as geometry only)', file=sys.stderr)
    bed = max(area[2], area[3])
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
            # no assembly: the newest part revision in the kit (X1 < X2 < ... < A < B), so a part bump renames the plate
            revs = [re.search(r'_([A-Z0-9]+)\.stl$', p).group(1) for p in stls.values()]
            stem, rev = os.path.basename(folder), max(revs, key=lambda r: (not r.startswith('X'), len(r), r))
        reg = printlist.parts.register()
        orient = orient_overrides(folder)
        groups = {}                               # material -> items: one material per plate
        for pn in sorted(stls):
            mat = plate_material(reg.get(pn, {}).get('Material / process', '?'))
            flat = lay_flat(read_stl(stls[pn]), orient.get(pn))
            base = os.path.basename(stls[pn])[:-4]
            groups.setdefault(mat, []).extend((f'{base}#{k + 1}', flat) for k in range(n[pn]))
        out = os.path.join(exports, 'plates')
        os.makedirs(out, exist_ok=True)
        for old in glob.glob(os.path.join(out, f'{stem}_plate*')):
            os.remove(old)
        k = 0
        for mat, items in groups.items():
            slug = re.sub(r'[^a-z0-9]+', '-', mat.lower()).strip('-')
            plates = pack(items, area)
            for i, parts in enumerate(plates, 1):
                k += 1
                path = os.path.join(out, f'{stem}_plate{k}-{slug}_{rev}.3mf')
                write_3mf(path, parts)
                note = ''
                if env:
                    g, mins = bambu_project(env, path, path, mat)
                    note = f', Bambu project ({PRINTER["machine"]}, {PRINTER["filaments"][mat]}, {PRINTER["bed_type"]}): ~{g:.0f} g, ~{mins:.0f} min'
                preview(path[:-4] + '.png', parts, bed, f'{stem} plate {k} ({mat}, {i}/{len(plates)}): {len(parts)} parts', area)
                print(f'{os.path.relpath(path, ROOT)}: {len(parts)} parts, {mat}{note}')
        print(f'{folder}: {sum(len(v) for v in groups.values())} parts on {k} plate(s), printable area {area}')
    for w in WARNINGS:
        print(f'BAMBU WARNING {w}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
