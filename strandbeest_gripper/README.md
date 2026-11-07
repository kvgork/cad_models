# strandbeest_gripper: Jansen-linkage gripper

| Version | Assembly | Parts | What | Generator / check |
|---|---|---|---|---|
| **v2** (current) | GRIP-9003 | GRIP-0011…0022 | two mirrored fingers that clamp an item with the leg's lift and carry it with the stride (feeder) | `tools/gen_dual.py` / `tools/verify_dual.py` |
| v1 | GRIP-9002 | GRIP-0003…0010 | one finger pinching against a fixed anvil | `tools/gen_finger.py` / `tools/verify_finger.py` |

v2 parts are new part numbers, not revisions: they don't interchange with v1 (hubs, shoulder holes, gears).

---

## v2: dual finger feeder (GRIP-9003), X1, not printed yet — NEEDS PRINT TEST

![v2 iso](docs/GRIP-9003_iso.png)

| Clamped, crank 0° | Opening, crank 120° | Open, crank 200° |
|---|---|---|
| ![](docs/GRIP-9003_crank_0.png) | ![](docs/GRIP-9003_crank_120.png) | ![](docs/GRIP-9003_crank_200.png) |

### How it works

**Two mirrored legs.** Two Jansen legs (holy numbers × 0.4) are mirrored across the line between them, so their feet (Ø11 pads) meet at the bottom of the loop. The crank turns continuously, and every turn does this:

1. **Clamp and pull.** On the flat bottom of the loop both pads close to their minimum gap. They travel together for **19.9 mm** along the stroke while within 0.4 mm of that gap, over about 134° of the crank.
2. **Release and return.** On the lift each foot rises about 9 mm, opening the pads to **19.5 mm**. They return and close again.

**Feeding direction.** Turn the crank the other way to feed the other way.

**Gear train.** One STS3215 (continuous / multi-turn mode) drives crank 1. Crank 2 turns 1:1 the opposite way through two idlers:
- module 1, crank gears z20, idlers z33, 3 meshes;
- the cranks are 86 mm apart;
- backlash is 0.3 mm on the pitch circle.

**Clamp gap.** The gap is fixed by geometry: `2·(43.0 − 36.73) − pad_d`, which is **1.53 mm** with `pad_d` = 11. It is rigid, so an item thicker than the gap stalls the servo. Change `PAD_D` in `gen_dual.py` and rebuild to set it.

### Checked in CAD (`tools/verify_dual.py`: 14/14 PASS)

| Check | Result |
|---|---|
| Joints | 22 revolute + 3 gear links; no conflicts |
| Crank 1 drive | full turn, every 30° step moved |
| Crank 2 | follows the exact mirror (0.0001 mm) |
| Both fingers vs `jansen.py` | within 0.0016 mm over a full turn |
| Clamp gap / opening | 1.53 mm / 19.50 mm |
| Feed stroke while clamped | 19.9 mm |
| Both pads move together along x | within 0.0004 mm |
| Gear meshes | no overlap; 0.141 mm minimum clearance, checked at 19 poses over one tooth pitch |
| Links vs all parts, gears vs frame | no contact over a full turn; ≥ 0.5 mm apart |

The gear meshes are checked statically: `joint.sweep` runs over its collision budget on the tooth meshes in SolidCraft 0.30.1.

### Layer stack (computed by `tools/layers.py` for the full turn)

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

### Hardware (v2)

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

### Assembly notes

- **Mirror parts.** Finger 2's triangles are true mirror parts: GRIP-0021 and GRIP-0022, marked **UP2**. Finger 1 uses GRIP-0019 and GRIP-0020, marked **UP1**. The bars are shared.
- **Gear timing:**
  1. Fit the crank gears at pose θ = 0: J1 of each finger points along the stroke away from the servo (see `crank_0` above).
  2. Then fit the idlers.
  3. If the pads don't close at the same moment, lift one idler and shift it one tooth.
- **The k–c near-toggle at 192° is passed every turn.** Clearance stack-up across the pins can make a leg snap to its mirror branch there. Keep the pin holes tight (calibrate `pin_d`). If a leg flips, the mismatch shows at once: the pads stop meeting.

---

## v1: single finger + anvil (GRIP-9002)


This is one Strandbeest-style finger driven by an STS3215 servo. It is Theo Jansen's leg ("holy numbers") scaled by **0.4**, with a 6 mm crank. The foot of the leg becomes a fingertip that travels on a nearly straight line and pinches objects against a fixed anvil.

Design background: vault `05-Wiki/research/2026-11-06-strandbeest-jansen-linkage-grippers.md` §4.5, and `00-Inbox/2026-11-07-strandbeest-finger-research.md`.

**Status: X1, not printed yet — NEEDS PRINT TEST** (pin fit, servo sleeve fit, stop strength).

![closed, crank +66°](docs/GRIP-9002_crank_66.png)

| Open: crank −63° | Mid: crank 0° | Closed: crank +66° |
|---|---|---|
| ![](docs/GRIP-9002_crank_-63.png) | ![](docs/GRIP-9002_crank_0.png) | ![](docs/GRIP-9002_crank_66.png) |

### What it does (checked in CAD by `tools/verify_finger.py`, all PASS)

| Quantity | Value |
|---|---|
| Operating crank range | −63° … +66° |
| Fingertip travel | 19.7 mm |
| Straightness | 0.20 mm |
| Grip opening (pad to anvil) | 21.0 mm open → 1.3 mm closed |
| Hard stops | crank tabs hit the frame post at +68.25° and about −65.5° |
| Collisions over the range | none; links 0.5 mm apart (washer gap) |
| Joint centres vs `tools/jansen.py` | ≤ 0.0001 mm |

- The closing direction is +crank (counter-clockwise seen from above).
- The foot plate turns about 30° while gripping. The pad is round and centred on joint F, so the contact point does not move.

### Move it in SolidCraft

1. Open `cad/GRIP-9002.sc`.
2. Drag the crank (GRIP-0004), or drive the joint `O_crank` (limits −65.25 … +68.25). The other 9 revolute joints follow; it is one closed loop.
3. From the CLI: `joint.drive {"joint":"O_crank","value":40}`. Use `motion.trace` on the pad to see the stroke.

### Files

| PN | Part | Layer (z) | Print |
|---|---|---|---|
| GRIP-0003 | frame: servo sleeve, G post, anvil column | z −21.4…45 | sleeve opening up; PETG/ASA (servo runs warm); supports only under the anvil arm if needed |
| GRIP-0004 | crank disc + 2 stop tabs (on the servo horn) | 0 (18.7–24.7) | flat; PETG |
| GRIP-0006 | link k (J1–J4) | 1 | flat |
| GRIP-0009 | triangle b-d-e (G–J2–J3), **"UP" debossed** | 1 | flat, UP on top |
| GRIP-0005 | link j (J1–J2) | 2 | flat |
| GRIP-0007 | link c (G–J4) | 2 | flat |
| GRIP-0008 | link f (J3–J5) | 2 | flat |
| GRIP-0010 | triangle g-h-i (J4–J5–F) + Ø10 fingertip pad | 3 | plate down, pad up |

- **Source:** `tools/gen_finger.py` writes `cad/GRIP-9002.json`. Then `tools/build.sh strandbeest_gripper` builds `cad/GRIP-9002.sc` and `exports/<PN>_X1.{step,stl,3mf}`.
- **Kinematics:** `tools/jansen.py` (it asserts the published scale-1 reference: stride 67.9 / height 22.5 / ymin −91.8).
- **Verification:** `tools/verify_finger.py` (runs `cad/GRIP-9002.verify.json`).
- **Parameters** (in the script): `link_t` 3, `gap` 0.5, `pin_d` 3.4, `head_d` 6.5, `fit_clr` 0.2, `wall` 2.5, `pad_d` 10. The link width (7 mm) is a generator constant, because slot width takes numbers only in SolidCraft 0.30.1.

### Hardware

| Qty | Item | Where |
|---|---|---|
| 1 | Feetech STS3215 | in the sleeve, horn up |
| 2 | M3×6 | crank → horn (the two horn holes away from J1) |
| 1 | M3×16 socket head + nyloc | J1: head in the pocket under the crank, up through k and j |
| 1 | M3×30 + nyloc | G: from below through the frame bore and post, up through b-d-e and c |
| 1 | M3×16 + nyloc | J4 (k, c, g-h-i) |
| 3 | M3×12 + nyloc | J2, J3, J5 |
| ~14 | M3 washers, 0.5 mm (DIN 125) | between every layer pair on every pin |

Every pin is a free M3 screw in Ø3.4 holes. **Snug the nyloc nuts but do not clamp them:** the links must turn freely. If the pins wobble, print a coupon and lower `pin_d` to 3.2–3.3.

### Assembly (order matters)

1. Push the servo into the sleeve, horn up and cable through the notch. **Set the servo to its centre position first.**
2. Put the J1 screw up through the crank, with its head in the pocket. Then fit the crank on the horn with 2 × M3×6, J1 pointing to bearing 168.4°. That is pose θ = 0: the coordinates below.
3. Stack the links in layer order with a washer between each layer.
   - **b-d-e has "UP" on top.**
   - The linkage can physically be assembled as its mirror image, which still moves but does not grip. Check the joint positions against this table at θ = 0, in the servo STEP frame (mm, axis at (12.5, 0)):

   | O | J1 | J2 | J3 | J4 | J5 | G | F (pad) |
   |---|---|---|---|---|---|---|---|
   | 12.50, 0.00 | 6.62, 1.21 | 19.39, −14.18 | 41.15, −9.21 | 26.72, 15.67 | 37.97, 6.23 | 28.02, 0.00 | 36.79, 32.48 |

4. Fit the G screw from below, through the bore, last.

### Servo setup

- **Angle limits:** crank −63° … +66° from the θ = 0 position. That is 2° or more inside the stops, so the servo never stalls into them.
- **Direction:** check that a positive step closes the finger (counter-clockwise from above). If it opens instead, invert the direction in the servo config.
- **Grip force:** set it indirectly with Torque_Limit; the STS3215 has no torque mode. Expect roughly 25–46 N per finger by the vault's estimate, unmeasured. Pin friction is the first thing to measure.

### Warnings

- **Do not turn the crank by hand beyond the stops.** Near crank 192° the k–c loop has only a 0.48 mm margin to toggle and can snap to its mirror branch. The tabs exist to prevent that.
- **Tab stop accuracy:** the measured stop is −65.73° against the designed −65.25°. The difference is within the mesh gap tolerance of the check (0.107 mm, about 0.5° at the tab).
- **Crank counterbores:** the horn-screw counterbores on the crank cut 0.55 mm into the central access hole. The screw heads still seat on the remaining ring.
- **Not modelled:** screws, washers and nuts. The servo sleeve is a friction fit with no retention screw (v1).

### Next (v1 notes)

Two mirrored fingers on one servo with a 1:1 gear pair, instead of the anvil. Re-optimise the link lengths for even grip force (vault §4.5). Add a soft Fin Ray-style pad.
