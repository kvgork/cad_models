# base/feetech_sts3215: Feetech STS3215 serial-bus servo (the SO-101 servo; read-only model)

![STS3215](LIB-0009_servo-sts3215.png)

| PN | File | sha256 (16) |
|---|---|---|
| LIB-0009 | `LIB-0009_servo-sts3215.step` (unchanged) | cacd717c2f22bec8 |

- **Same file as `lib/sts3215/`.** This is a byte-identical copy, which Git LFS stores once. `lib/` keeps its copy because the strandbeest v1–v3 generators insert it from there; new designs should use this folder.
- **Derived meshes:** `.stl` and `.3mf`, in the same coordinates.

## Source and licence

- **Fetched from:** TheRobotStudio SO-ARM100, `STEP/SO100/STS3215_03a.step`, https://github.com/TheRobotStudio/SO-ARM100 (Apache-2.0), on 2026-11-07.
- **Not Feetech's own file.** It is the SO-ARM project's model and **includes the standard Ø20 horn disc**, so there is no bare spline in it. step.parts has no STS3215 (checked 2026-11-13), and the Seeed / Feetech download hubs only have datasheets.
- **Datasheet used for the cross-check:** Feetech STS3215 product specification, rev A/0, 2020-04-10, §9 outline drawing (machine-translated copy hosted by Core Electronics: https://core-electronics.com.au/attachments/uploads/sts3215-smart-servo-datasheet-translated.pdf). Not stored here.

## Key data (datasheet)

| Item | Value |
|---|---|
| Case | 45.2 × 24.7 × 35 mm, 55 g |
| Output | 25T spline, OD 5.9, horn screw M3 × 6 |
| Encoder | 12-bit magnetic: 4096 steps / 360°, 0.088° per step |
| Bus | TTL half-duplex serial, 2 × 5264-3P connectors (GND, V, signal) |
| Case screws | 8 × PA2.0 self-tapping; rear cover PA3.0 × 5 |

## The servos of the SO-101 arm (all the same case; this one model fits every joint)

| Joint | Leader arm (7.4 V) | Follower arm |
|---|---|---|
| 1 shoulder pan (base) | STS3215 **C044**, 1:191 | 1:345 |
| 2 shoulder lift | STS3215 **C001**, 1:345 | 1:345 |
| 3 elbow flex | STS3215 **C044**, 1:191 | 1:345 |
| 4 wrist flex | STS3215 **C046**, 1:147 | 1:345 |
| 5 wrist roll | STS3215 **C046**, 1:147 | 1:345 |
| 6 gripper | STS3215 **C046**, 1:147 | 1:345 |

- **Follower versions differ by kit:**
  - C001 (7.4 V) in the standard kit;
  - C018 or C047 (12 V) in the Pro kit.
- **Sources:** [LeRobot SO-101 docs](https://huggingface.co/docs/lerobot/so101), [Seeed SO-ARM course ch. 4](https://wiki.seeedstudio.com/robotics/soarm_physical_ai_course_chapter_4/), [Seeed Feetech datasheet hub](https://wiki.seeedstudio.com/feetech_servo/).
- **Same case for every variant:** the versions differ only in gear ratio, voltage and gear material.

## Interfaces (measured on the STEP with `model.faces`; model frame, Z = output axis direction)

| Interface | Model (mm) | Drawing (mm) |
|---|---|---|
| Output axis | x 12.5, y 0, along +Z | 12.5 from the case centre ✓ |
| Case footprint | x ±22.7, y ±12.4 (45.4 × 24.8) | 45.23 × 24.73 (model +0.17 / +0.07) |
| Case top | z 14.4 at the output end, 17.0 at the rear | |
| Case bottom | main face at z −17.7 | |
| Case height | 32.1 at the output end, 34.7 at the rear | 32 / 35 ✓ (within 0.3) |
| Horn (included) | Ø20 disc, z 16.2 … 18.7; 4 × Ø2.5 holes on a Ø14 circle at 45°; centre screw head to z 20.2 | |
| Rear axis boss | Ø9 at (12.5, 0), bottom at z −19.4 (1.7 below the main bottom) | drawing: Ø6 axis, "4.1" |
| Connectors | 2 × 3 pin holes at x −1.55, y ±2.8 / ±5.2 / ±7.6 (2.4 pitch) | 5264 3P |
| Rear bosses | Ø4 at (−20.7, ±10.4) | |

**Not resolved:**
- The drawing's 4.1 mm below the case doesn't match the model's 1.7 mm rear boss. It is probably measured from a recessed face. If a part sits under the servo, measure a real servo.
- The model includes the horn, so the drawing's 3.4 mm spline protrusion can't be checked on it.

## Place it (output axis at the origin)

The output axis on +Z through the origin, z = 0 on the **case top at the output end** (the face a bracket presses against), the case extending toward −X:

```json
{"command": "file.insert_step", "params": {"path": "base/feetech_sts3215/LIB-0009_servo-sts3215.step", "name": "LIB-0009_servo-sts3215"}},
{"command": "occurrence.move", "params": {"occurrence": "LIB-0009_servo-sts3215:1", "move_grounded": true,
  "matrix": [[1, 0, 0, -12.5], [0, 1, 0, 0], [0, 0, 1, -14.4]]}}
```

Checked 2026-11-13. In that frame:

| Feature | Position (mm) |
|---|---|
| Case | x −35.2 … 10.2, y ±12.4 |
| Horn top | z 4.3 |
| Horn screw head | z 5.8 |
| Case bottom | main face at z −32.1, rear boss at −33.8 |
