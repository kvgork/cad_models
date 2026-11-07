# Strandbeest gripper v2: dual finger feeder (GRIP-9003)

X1, not printed yet — **NEEDS PRINT TEST**. Overview of all versions: [../README.md](../README.md).

![v2 iso](docs/GRIP-9003_assy-dual-finger_iso.png)

| Clamped, crank 0° | Opening, crank 120° | Open, crank 200° |
|---|---|---|
| ![](docs/GRIP-9003_assy-dual-finger_crank_0.png) | ![](docs/GRIP-9003_assy-dual-finger_crank_120.png) | ![](docs/GRIP-9003_assy-dual-finger_crank_200.png) |

## How it works

**Two mirrored legs.** Two Jansen legs (holy numbers × 0.4) are mirrored across the line between them, so their feet (Ø11 pads) meet at the bottom of the loop. The crank turns continuously, and every turn does this:

1. **Clamp and pull.** On the flat bottom of the loop both pads close to their minimum gap. They travel together for **19.9 mm** along the stroke while within 0.4 mm of that gap, over about 134° of the crank.
2. **Release and return.** On the lift each foot rises about 9 mm, opening the pads to **19.5 mm**. They return and close again.

**Feeding direction.** Turn the crank the other way to feed the other way.

**Gear train.** One STS3215 (continuous / multi-turn mode) drives crank 1. Crank 2 turns 1:1 the opposite way through two idlers:
- module 1, crank gears z20, idlers z33, 3 meshes;
- the cranks are 86 mm apart;
- backlash is 0.3 mm on the pitch circle;
- the idlers are 5.5 mm thick, 0.5 mm lower than the crank gears, so the J1 hubs on the cranks clear their tooth tips.

**Clamp gap.** The gap is fixed by geometry: `2·(43.0 − 36.73) − pad_d`, which is **1.53 mm** with `pad_d` = 11. It is rigid, so an item thicker than the gap stalls the servo. Change `PAD_D` in `gen_dual.py` and rebuild to set it.

## Checked in CAD (`../tools/verify_dual.py`: 14/14 PASS)

| Check | Result |
|---|---|
| Joints | 22 revolute + 3 gear links; no conflicts |
| Crank 1 drive | full turn, every 30° step moved |
| Crank 2 | follows the exact mirror (0.0001 mm) |
| Both fingers vs `jansen.py` | within 0.0016 mm over a full turn |
| Clamp gap / opening | 1.53 mm / 19.50 mm |
| Feed stroke while clamped | 19.9 mm |
| Both pads move together along x | within 0.0004 mm |
| Gear meshes | no overlap; 0.141 mm minimum clearance, checked at 19 poses over one tooth pitch + every 10° of the full turn |
| Links vs all parts, gears vs frame | no contact over a full turn; ≥ 0.5 mm apart |

The gear meshes are checked statically: `joint.sweep` runs over its collision budget on the tooth meshes in SolidCraft 0.30.1.

## Layer stack (computed by `../tools/layers.py` for the full turn)

| Layer | z (mm) | Parts |
|---|---|---|
| 0 | 18.7–24.7 | crank gears, idlers |
| 1 | 25.2–28.2 | f (with a hub up to g-h-i) |
| 2 | 28.7–31.7 | b-d-e (with a hub up to c) |
| 3 | — | empty: room for nuts and hubs |
| 4 | 35.7–38.7 | c |
| 5 | 39.2–42.2 | g-h-i + pad (z 33.2–48.2) |
| 6 | 42.7–45.7 | j |
| 7 | 46.2–49.2 | k |

- **Hubs instead of loose spacers.** Joint columns with empty layers get a printed hub on the lower link (Ø7), so there are no loose parts.
- **J1 shoulder screw.** J1 is an **ISO 7379 shoulder screw Ø4 × 25, M3 thread**, screwed into a Ø2.5 hole in the crank gear (thread-forming). j and k turn on the 4 mm shoulder.

## Hardware (v2)

| Qty | Item | Where |
|---|---|---|
| 1 | Feetech STS3215, multi-turn / wheel mode | servo sleeve, horn up |
| 2 | M3×6 | crank gear 1 → horn |
| 2 | ISO 7379 shoulder screw Ø4×25, M3 | J1 of each finger |
| 2 | M3×14 + nyloc | idler axles, from below the plate |
| 1 | M3×12 + **thin nut DIN 439** + threadlocker | crank 2 axle; the nut sits in the recess in the gear top, because link j passes over it |
| 2 | M3×30 + nyloc | G (b-d-e, c), from below through the plate and post |
| 2 | M3×22 + nyloc | J2 (b-d-e hub → j) |
| 2 | M3×22 + nyloc | J5 (f hub → g-h-i) |
| 2 | M3×18 + nyloc | J4 (c, g-h-i hub, k) |
| 2 | M3×12 + nyloc | J3 (b-d-e, f) |
| ~24 | M3 washers 0.5 mm | between layers |

Screw lengths are computed from the layer stack: grip + 0.5 mm washer + 4 mm nut, rounded up to a standard length. The J1 shoulder is 24.5 mm long, so Ø4×25 leaves 0.5 mm of play.

## Assembly notes

- **Mirror parts.** Finger 2's triangles are true mirror parts: GRIP-0021 and GRIP-0022, marked **UP2**. Finger 1 uses GRIP-0019 and GRIP-0020, marked **UP1**. The bars are shared.
- **Gear timing:**
  1. Fit the crank gears at pose θ = 0: J1 of each finger points along the stroke away from the servo (see `crank_0` above).
  2. Then fit the idlers.
  3. If the pads don't close at the same moment, lift one idler and shift it one tooth.
- **The k–c near-toggle at 192° is passed every turn.** Clearance stack-up across the pins can make a leg snap to its mirror branch there. Keep the pin holes tight (calibrate `pin_d`). If a leg flips, the mismatch shows at once: the pads stop meeting.
