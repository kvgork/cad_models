# gripper_tips: red calibration tips for the SO-101 gripper

Snap-on tips for the two jaws of the standard SO-101 follower gripper, printed in red and used as calibration markers. Each version folder is a complete print kit (README with print list, exports, plate file, sorting sheet).

| Version | Folder | Parts | Covers | Status |
|---|---|---|---|---|
| v1 full cap | [`v1_full-cap/`](v1_full-cap/README.md) | SO101-0001 moving jaw, SO101-0002 fixed jaw | the whole tip, gripping face included | X1, CAD-checked |
| v2 open inside | [`v2_open-inside/`](v2_open-inside/README.md) | SO101-0003 moving jaw, SO101-0004 fixed jaw | outside only: the gripping face stays bare, so the grip isn't affected | X1, CAD-checked, NEEDS PRINT TEST |

## Comparison

| | v1 | v2 |
|---|---|---|
| Shape | closed cap | U-clip, front wall removed |
| Material on the gripping face | 1.6 mm wall + 0.2 mm gap | none: stops 0.5 mm behind it |
| Snap | 1.2 mm bumps in the jaw's Ø1.5 hole, 2 slits | same bumps, 1 slit (back) |
| Volume moving / fixed (mm³) | 2385.8 / 1542.7 | 1679.9 / 1046.1 |
| Hold on the finger | taper wedge + bumps | bumps + tip end only |

Both are modelled in their jaw's own STEP frame (`lib/so101/LIB-0003` moving jaw, `LIB-0005` wrist-roll follower), so inserting the jaw at its origin puts the tip in place.

Build one version: `tools/build.sh gripper_tips/v1_full-cap` (or `v2_open-inside`).
