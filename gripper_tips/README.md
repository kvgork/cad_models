# gripper_tips — SO101-0001, SO101-0002

Two snap-on caps that cover the tips of the standard SO-101 follower gripper jaws. They are meant to be printed in red and used as calibration markers.

| PN | Source → exports | Fits | Built in the frame of |
|---|---|---|---|
| SO101-0001 | `cad/SO101-0001.json` → `exports/SO101-0001_X1.{step,stl,3mf}` | `Moving_Jaw_SO101` | `lib/so101/LIB-0003.step` (the finger runs along −Y) |
| SO101-0002 | `cad/SO101-0002.json` → `exports/SO101-0002_X1.{step,stl,3mf}` | the fixed jaw on `Wrist_Roll_Follower_SO101` | `lib/so101/LIB-0005.step` (the finger runs along +Z) |

Each cap is modelled in its jaw's own STEP coordinates. Insert the jaw STEP at its origin and the cap sits exactly where it belongs.

## How it fits

- **Cavity:** a section-scanned envelope of the jaw tip plus `clr` (0.2 mm). The cap covers about 26 mm on the moving jaw and 19 mm on the fixed jaw.
- **Taper fit:** both jaws taper toward the tip in width and thickness, so the cap slides on from the tip and wedges to a repeatable stop. The gripping face of each jaw steps outward toward the tip, so the cap's front wall is straight and leaves a gap of up to 4 mm behind the steps.
- **Snap:** two 1.2 mm bumps on opposite inner walls click into the jaw's existing Ø1.5 through-hole:
  - moving jaw: hole axis Z at (x −1.19, y −58.66)
  - fixed jaw: hole axis Y at (x −13.69, z 88.33)

  The bumps reach 0.25 mm into the hole (`bump_h − clr`).
- **Slits:** two 1.2 × 8 mm slits at the mouth let the walls carrying the bumps flex.
- **Removal:** pull the cap off toward the tip.

## Print

- Print with the open mouth down on the bed and no supports. All overhangs are 37° or less from vertical.
- Use red PLA or PETG, with walls of 2 or more perimeters (the wall is 1.6 mm).

## Tuning

- If the cap is too tight, raise `clr` to 0.25–0.3 mm.
- If the snap is too stiff, lower `bump_h`.
- If the snap is too weak, raise `bump_h` or lengthen the slits with `slit_len`.

## Notes

- The section geometry comes from the SO-ARM100 STEP files (`lib/so101/`).
- `inspect.clearance` fails on the vendor jaw bodies (a boolean step fails), so the fit was checked with `inspect.section` at the bump holes and the mid-planes.
