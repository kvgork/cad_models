# base/feetech_scs0009: Feetech SCS0009 micro bus servo (read-only vendor model)

![SCS0009](LIB-0010_servo-scs0009.png)

| PN | File | sha256 (16) |
|---|---|---|
| LIB-0010 | `LIB-0010_servo-scs0009.step` (unchanged vendor file) | f1360e6fcecabffc |

## Source and licence

- **Origin:** the file is Feetech's own CAD: Pro/ENGINEER assembly `SCS009-20201118-S_ASM`, with factory part names `SJ-WK00-0037-BOTTOMCASE`, `-0039-COREMIDDLE`, `-0038-TOPCASE` and `SJ-CL00-0027-OUTPUTGEAR`.
- **Fetched from:** step.parts, https://www.step.parts/parts/feetech_scs0009, on 2026-11-13. The file is stored at github.com/earthtojake/step.parts, commit c6113328a5695b976a010a203a90fe86191769bf, `catalog/step/feetech_scs0009.step`.
- **Licence:** step.parts distributes it under the MIT licence (© 2026 earthtojake). Keep this notice with the file.
- **Datasheet used for the cross-check:** Feetech SCS0009 product specification, rev A/0, 2020-11-23 (hosted by Switch Science: https://pages.switch-science.com/comparison/files/feetech/serial-scs/SCS0009_datasheet.pdf). Not stored here.

## Key data (datasheet)

6 V, 2.3 kg·cm stall / 0.75 kg·cm rated, 1:416 metal gears, 300° in servo mode (0.293°/step), TTL half-duplex serial bus (5264-3P connector: GND, V, signal), 13.2 g. Output spline 20T, OD 3.95, horn screw M2 × 4.

## Interfaces (measured on the STEP with `model.faces`; vendor frame, Y = up)

| Interface | Vendor frame (mm) | Datasheet |
|---|---|---|
| Output axis | x 0, z −5.7, along +Y | output axis 5.7 from the body centre ✓ |
| Spline | Ø4.0, top at y 27.0; M2 core hole Ø1.6 from y 22.0 down | 20T OD 3.95 ✓ |
| Gear dome (top case) | collar around the spline tops out at y 24.1 | 25.25 above the bottom = y 23.8: the collar is **0.3 mm higher** than the drawing |
| Case | x ±6.05, z ±11.65; flat bottom at y −1.45 (measured: 223 mm² of face; small feet reach −1.51) | 12.1 × 23.3 ✓ |
| Mounting tabs | z ±16.25 (32.5 tip to tip), y 15.35 … 16.95 (1.6 thick) | 32.5 ✓; 16.8 … 18.4 above the bottom ✓ |
| Tab holes | Ø2.0 at x 0, z ±14.25 (28.5 apart) | 2 × Ø2 at ±14.25 ✓ |
| Case screws | 4 × Ø1.1 at x ±4.8, z ±10.4 | |
| Total height | −1.45 … 27.0 = 28.45 | 28.45 ✓ |

Case, tabs, tab holes, output axis, spline and total height agree with the datasheet within 0.05 mm. Two exceptions: the collar around the spline is 0.3 mm taller than the drawing's 25.25, and small feet reach 0.06 mm below the flat bottom. Keep 0.5 mm clearance around the case in any holder.

## Place it Z-up (the usual frame in this repo)

The output axis along +Z through the origin, z = 0 on the **underside of the mounting tabs** (the face that sits on a mounting plate), the case length along Y:

```json
{"command": "file.insert_step", "params": {"path": "base/feetech_scs0009/LIB-0010_servo-scs0009.step", "name": "LIB-0010_servo-scs0009"}},
{"command": "occurrence.move", "params": {"occurrence": "LIB-0010_servo-scs0009:1", "move_grounded": true,
  "matrix": [[1, 0, 0, 0], [0, 0, -1, -5.7], [0, 1, 0, -15.35]]}}
```

Checked 2026-11-13. In that frame:

| Feature | Position (mm) |
|---|---|
| Output gear | centred on x = y = 0 |
| Spline top | z 11.65 |
| Case | x ±6.05, y −17.35 … 5.95, flat bottom at z −16.80 (feet −16.86) |
| Tabs | y −21.95 … 10.55 |
| Tab holes | x 0, y −19.95 and 8.55 |

A mounting plate needs a 12.1 × 23.3 cutout, plus clearance, through which the case hangs, and two M2 (or Ø2 self-tapping) holes at y −19.95 / 8.55.

## Derived files

`LIB-0010_servo-scs0009.stl` and `.3mf` were exported by solidcraft-cli 0.30.1 from the STEP, in the same coordinates, at fine quality. Use them for visualisation, simulation and slicer previews; for CAD and fit checks, use the STEP. The picture uses the Z-up placement above.
