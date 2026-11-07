"""Read the part register (PARTS.md at the repo root): part number -> short name, folder.

    from parts import name, fname
    fname('GRIP-0015')            -> 'GRIP-0015_link-j-hub'
    export('GRIP-0015', 'X1', 'stl') -> 'GRIP-0015_link-j-hub_X1.stl'
"""
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
_REG = None


def register():
    global _REG
    if _REG is None:
        _REG = {}
        head = None
        for line in open(os.path.join(ROOT, 'PARTS.md'), encoding='utf-8'):
            if not line.startswith('|'):
                continue
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if cells[0] == 'PN':
                head = cells
                continue
            if head and cells[0] and not cells[0].startswith('---'):
                _REG[cells[0]] = dict(zip(head, cells))
    return _REG


def name(pn):
    return register()[pn]['Name']


def fname(pn):
    """File / component base name: <PN>_<name>."""
    return f"{pn}_{name(pn)}"


def export(pn, rev, ext):
    return f"{fname(pn)}_{rev}.{ext}"
