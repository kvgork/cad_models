# Strandbeest gripper v8: four-bar legs (GRIP-9016)

X3 (second coupler fix), first build in progress. **NEEDS PRINT TEST.** This is [v7](../v7_sandwich/README.md) made simpler and smaller. The jaw motion is kept: same parallel jaws, same clamp gap, same opening and the same flat clamp-and-pull stroke. Each 7-link Jansen leg is replaced by a **four-bar linkage**: an eccentric on the crank gear, a coupler that carries the jaw, and a rocker. Overview of all versions: [../README.md](../README.md).

Strictly speaking it is no longer a Strandbeest: the jaw follows the same clamp stroke, but the return path above it has a different shape.

![done](docs/build/step9_done_iso.png)

## What changed

| | v7 | v8 |
|---|---|---|
| Leg | Jansen, 7 links + crank arm, 9 joints | **four-bar**: eccentric crank, coupler, rocker (4 joints) |
| Gears | 9 (4 cranks Z20, 2 Z33, 2 Z20 idlers, wheel) | **6** (4 cranks Z46 with the eccentric, 2 Z24 idlers) |
| Prints | 96 | **37** |
| Part numbers | 31 | **17** + assembly |
| Mechanism size | frame 161 × 168, 52 mm high | **97 × 135, 36.7 mm high** (knob shaft barb) |
| Jaws | 135 mm, 54 mm slot | **105 mm**, hole + 2 mm slot |
| Top plates | 2 plates on 8 pillars | **1 plate** on the 4 rocker columns, no pillars |
| Fasteners | none | none |

**Jaw motion, v7 vs v8** (v7 numbers from `jansen.py` at S = 0.4; v8 from `../tools/fourbar.py` and checked in CAD below):

| | v7 (Jansen) | v8 (four-bar) |
|---|---|---|
| Clamp gap / fully open | 1.53 / 19.50 mm | 1.53 / 19.44 mm |
| Opening per jaw | 8.98 mm | 8.96 mm |
| Clamp-and-pull stroke | 19.9 mm | 20.5 mm |
| Gap error over that stroke (per jaw) | 0.189 mm | **0.153 mm** |
| Same, any one link length off by ±0.1 mm | 0.270 mm | **0.200 mm** |
| Crank turn spent in the clamp | 132° | 124.5° |
| Return path | flat loop, 27 mm long | teardrop, 37 mm long |
| Smallest transmission angle | lower | 51° |

The jaw opens and closes with the same gap, stroke and flatness, and the four-bar is less sensitive to print errors. The only real difference is the return path above the clamp stroke: it is 10 mm longer, so the jaws travel further back while open.

## How it works

**Leg (four-bar, fit by `fourbar.py`).** Lengths in mm: crank (eccentricity) 8.77, coupler J1–B 16.75, rocker Q–B 25.07, ground O–Q 28.27, jaw pin P at 11.48 / 29.87 in the coupler frame. The fit asked for the same jaw opening and clamp stroke as v7, and for room for the real parts: the rocker column outside the ring sweep, the rocker clear of the plate stub, and the jaw path below the linkage. It was then refit so that a 0.1 mm error on any link length still keeps the clamp flat (the first fit lost the flat with a 0.1 mm error).

**Eccentric instead of a crank pin.** The coupler sweeps right over the crank centre O, so a pin at J1 would leave no room for a crank shaft going up to the top plate. So the coupler has a **ring** (Ø29.9 outside) that runs on an **eccentric boss** (Ø25.2) on top of the crank gear, and a Ø5 shaft runs straight through gear and boss from the base to the top plate. **Every turning axis is held at both ends:** crank shafts in the base and the top plate (plate stub down to the boss), rockers on a frame journal with a plate stub on top.

**One top plate, no pillars.** Each rocker pivot Q is a column: frame post Ø7 up to the rocker, a Ø6 journal the rocker turns on, and the plate's Ø7 stub on top of it. A snap pin runs from under the base through the column and the plate. The 4 columns carry the plate. The plate has a window over the gripping slot, and the base has a notch under it, so the slot between the jaws is open from above and below from x ≈ 29 mm to the jaw tips.

**Legs and fingers.** Leg B is leg A moved 48.74 mm along the stroke, with the same crank angle: the crank gears A and B mesh with the Z24 idler X between them. The jaw has a hole at leg A's pin and a 2 mm slot at leg B's pin, so print errors don't bind the parallelogram. Finger 2 is finger 1 mirrored about the clamp line. The two idlers mesh with each other on the clamp line, which keeps the fingers in time: A1–X1–B1, X1–X2, X2–A2, X2–B2.

**Same part, both fingers.** The coupler, rocker and jaw are symmetric, so finger 2 uses the same parts: the couplers turned over, the jaw as is. Only the 4 crank gears are different parts, because each one has its own tooth phase relative to the eccentric. They are labelled A1 / B1 / A2 / B2.

**Joint coordinates at θ = 0** (leg A1, mm; base plane, x along the stroke, O_A1 = origin). A four-bar can also be assembled in its mirror branch. Check B against this table: B must be on the same side of the line J1–Q as here.

| O | J1 | B | Q | P |
|---|---|---|---|---|
| (0, 0) | (8.77, 0) | (−7.98, −0.34) | (−15.70, 23.51) | (−2.10, −30.10) |

Leg B1: + (48.74, 0). Finger 2: y → −74.24 − y. Idlers X1 (24.37, −25.12) and X2 (24.37, −49.12).

**Z stack:** base 0–4 | gears 4.5–9.5 (idlers to 9.0) | eccentric flange 9.5–10 + boss to 13.5 | couplers 10–13.5 | rockers 14–17.5, jaws 14–22 | top plate 22.5–26.5 | knob 27–35.

## Print list

<!-- printlist:start -->
<!-- generated by tools/printlist.py; do not edit by hand -->
**37 prints from 17 STL files.** Quantities counted from the assembly `cad/GRIP-9016_assy-four-bar.json` (purchased parts left out). The `.3mf` and `.step` of each part are next to the STL.

| Qty | File (`exports/`) | Part | Material |
|---|---|---|---|
| 1 | `GRIP-0107_frame-four-bar_X1.stl` | FRAME, FOUR-BAR, 4 Q COLUMNS, STRANDBEEST V8 | PETG, FDM |
| 1 | `GRIP-0108_top-plate-four-bar_X1.stl` | PLATE, TOP, CRANK + ROCKER BEARINGS, SLOT WINDOW, STRANDBEEST V8 | PETG, FDM |
| 1 | `GRIP-0109_knob-double-d_X1.stl` | KNOB, THUMB, KNURLED D40, DOUBLE-D BORE, STRANDBEEST V8 | PETG, FDM |
| 1 | `GRIP-0110_gear-crank-a1-eccentric_X1.stl` | GEAR, CRANK, A1, Z46 M1, ECCENTRIC BOSS, STRANDBEEST V8 | PETG, FDM |
| 1 | `GRIP-0111_gear-crank-b1-eccentric_X1.stl` | GEAR, CRANK, B1, Z46 M1, ECCENTRIC BOSS, STRANDBEEST V8 | PETG, FDM |
| 1 | `GRIP-0112_gear-crank-a2-eccentric_X1.stl` | GEAR, CRANK, A2, Z46 M1, ECCENTRIC BOSS, STRANDBEEST V8 | PETG, FDM |
| 1 | `GRIP-0113_gear-crank-b2-eccentric_X1.stl` | GEAR, CRANK, B2, Z46 M1, ECCENTRIC BOSS, STRANDBEEST V8 | PETG, FDM |
| 2 | `GRIP-0114_gear-idler-z24_X1.stl` | GEAR, IDLER, Z24 M1, FINGER SYNC | PETG, FDM |
| 4 | `GRIP-0115_coupler-eccentric_X3.stl` | COUPLER, ECCENTRIC RING, FOUR-BAR (FINGER 2 FLIPPED) | PETG, FDM |
| 4 | `GRIP-0116_rocker-q-b_X1.stl` | ROCKER, Q-B, FOUR-BAR | PETG, FDM |
| 2 | `GRIP-0117_jaw-four-bar_X1.stl` | JAW, PARALLEL, HOLE + SHORT SLOT, STRANDBEEST V8 | PETG, FDM |
| 3 | `GRIP-0118_shaft-crank-double-d_X1.stl` | SHAFT, CRANK, D5, DOUBLE-D, SNAP, STRANDBEEST V8 | PETG, FDM |
| 1 | `GRIP-0119_shaft-crank-knob_X1.stl` | SHAFT, CRANK, D5, DOUBLE-D, SNAP, KNOB LENGTH, STRANDBEEST V8 | PETG, FDM |
| 4 | `GRIP-0120_snap-pin-2f-q-column_X1.stl` | PIN, SNAP, PRINTED, D3, 2 FLATS, Q COLUMN + TOP PLATE | PETG, FDM |
| 4 | `GRIP-0121_pin-press-head-b_X1.stl` | PIN, PRESS, HEADED, D3, 2 FLATS, B (COUPLER-ROCKER) | PETG, FDM |
| 4 | `GRIP-0122_pin-press-head-p_X1.stl` | PIN, PRESS, HEADED, D3, 2 FLATS, P (COUPLER-JAW) | PETG, FDM |
| 2 | `GRIP-0123_snap-pin-2f-idler-down_X1.stl` | PIN, SNAP, PRINTED, D3, 2 FLATS, Z24 IDLER, HEAD IN GEAR | PETG, FDM |
<!-- printlist:end -->

## Fastener BOM

<!-- fasteners:start -->
<!-- generated by tools/printlist.py from fasteners.json; edit that file -->
No fasteners: every pin and axle is printed (snap pins, press pins, double-D crank shafts).

<!-- fasteners:end -->

**Plates:** `exports/plates/` (Bambu Studio projects for the X2D, PETG HF on Textured PEI; `tools/plates.py`). All parts PETG. Print the pins and shafts lying on one of their flats (the plate files do this). Print the gears and couplers flat, the jaws on their bottom face (counterbores up), and the top plate upside down with the stubs up.

**Reprint plate (X3 coupler fix):** `exports/plates/GRIP-9016_assy-four-bar_reprint_plate1-petg_X3.3mf` holds only the 4 X3 couplers (GRIP-0115), ~6 g, ~14 min, slices without warnings. Made with `python3 tools/plates.py strandbeest_gripper/v8_four-bar --only GRIP-0115 --tag reprint`. The full-kit plates are regenerated as X3 too; the X1 and X2 plates are in `exports/_superseded/plates/`.

## Build plan

Sorting sheet with 1:1 outlines: [docs/GRIP-9016_assy-four-bar_sort-sheet_A4.pdf](docs/GRIP-9016_assy-four-bar_sort-sheet_A4.pdf).

**Part sizes.** Hole spacing is centre to centre, from the generator. Overall size is measured on the exported STL files.

| Part | Qty | Holes | Hole spacing (mm) | Overall (mm) |
|---|---|---|---|---|
| GRIP-0107 frame | 1 | 4 O (Ø5.3), 4 Q columns, 2 X | A–B 48.74, finger 1–2 74.24 | 135.3 × 80.4 × 18.0 |
| GRIP-0108 top plate | 1 | 4 O stubs, 4 Q stubs | as frame | 135.3 × 79.4 × 12.5 |
| GRIP-0110…0113 crank gear A1 / B1 / A2 / B2 | 1 each | double-D bore, eccentric boss Ø25.2 | eccentricity 8.77 | 48.0 × 48.0 × 9.0 |
| GRIP-0114 idler Z24 | 2 | Ø3.4, head recess on top | — | 25.9 × 25.9 × 4.5 |
| GRIP-0115 coupler | 4 | ring Ø25.5, B and P Ø3.2 (drawn loose, prints snug) + 0.3 × 45° lead-in both ends | J1–B 16.75, B–P 30.33, J1–P 32.00 | 48.6 × 35.2 × 3.5 |
| GRIP-0116 rocker | 4 | Q Ø6.3 (eye Ø11), B Ø3.4 | 25.07 | 32.9 × 16.7 × 3.5 |
| GRIP-0117 jaw | 2 | hole Ø3.4 + 2 mm slot, counterbores on top | 48.74 | 104.7 × 11.0 × 8.0 |
| GRIP-0118 crank shaft | 3 | — | — | 27.7 × 8.0 × 3.4 |
| GRIP-0119 crank shaft, knob | 1 | — | — | 36.2 × 8.0 × 3.4 |
| GRIP-0109 knob | 1 | double-D bore | — | Ø40 × 8 |
| GRIP-0120 Q column snap pin | 4 | — | — | 28.2 × 5.5 × 2.6 |
| GRIP-0121 B press pin | 4 | — | — | 9.2 × 5.5 × 2.6 |
| GRIP-0122 P press pin | 4 | — | — | 11.7 × 5.5 × 2.6 |
| GRIP-0123 idler snap pin | 2 | — | — | 8.8 × 5.5 × 2.6 |

Orange = the parts added in that step.

### Step 1: frame and idlers

![step 1](docs/build/step1_idlers.png)

Put the two Z24 idlers on the X holes, the head recess up. Push an idler snap pin (GRIP-0123) down through each idler until the barb clicks under the base. The head sits in the idler's recess.

### Step 2: crank gears and crank shafts

![step 2](docs/build/step2_cranks.png)
![step 2 top](docs/build/step2_cranks_top.png)

The shafts and column pins go in from below; their heads sit in counterbores in the base, so the frame stays flat on the table. Lift one corner to push each one in.

Lay each crank gear on its O hole: **A1** at the knob corner, **B1** next to it along the stroke, **A2** and **B2** on the other finger (the labels are on the gear face). **Every eccentric boss points the same way, toward the jaw tips (+x)**, as in the top view. Mesh them with the idlers. If a gear doesn't drop in, lift it and try the next tooth: keep the boss pointing +x.

Then push a crank shaft up from below through each O hole into its gear: the **long shaft (GRIP-0119) at A1**, the three short shafts (GRIP-0118) at B1, A2 and B2. Turn each shaft until its flats find the gear's double-D hole and push it home (head in its counterbore). The shafts now hold the gears in place and stand up as guides for the top plate.

### Step 3: column pins

![step 3](docs/build/step3_column-pins.png)

Push a Q column snap pin (GRIP-0120) up from below through each of the 4 Q columns, head in its counterbore. The barbs stick out above the columns.

### Step 4: couplers

![step 4](docs/build/step4_couplers.png)

Drop a coupler ring over each eccentric boss (the shaft is inside the boss). It rests on the 0.5 mm flange. Finger 2's couplers are the same part **turned over** (mirror image). The long arm with the P hole points toward the clamp line.

### Step 5: rockers

![step 5](docs/build/step5_rockers.png)

Put each rocker's big eye over its Q journal (the column pin is inside it) and its small hole over the coupler's B hole. Press a B pin (GRIP-0121) down through the rocker into the coupler until it is **flush with the coupler's underside**. The head stays 0.2 mm above the rocker so the rocker can turn.

### Step 6: jaws

![step 6](docs/build/step6_jaws.png)

Lay each jaw on its finger's two P holes: the round hole on leg A, the short slot on leg B, counterbores up. Press a P pin (GRIP-0122) through each into the coupler, flush underneath. The head sits in the counterbore.

### Step 7: top plate

![step 7](docs/build/step7_top-plate.png)

Lower the top plate (stubs down) over the 8 pin tips: 4 shafts and 4 column pins. The O stubs go over the eccentric bosses. Press the plate down over each pin in turn with your thumb until all 8 barbs click above the plate (the A1 shaft goes on up through the plate for the knob). The pins now hold base and plate together.

### Step 8: knob

![step 8](docs/build/step8_knob.png)

Push the knob down over the long A1 shaft, turning it until the double-D bore finds the flats, until the barb clicks above the knob.

### Step 9: check

![step 9](docs/build/step9_done_top.png)

1. Turn the knob a full turn slowly: nothing binds, and both jaws stay parallel.
2. The jaws close to about 1.5 mm and stay closed while they pull back 20 mm. Then they open to about 19 mm.
3. If a jaw tilts, legs A and B of that finger are out of time: take the plate off and move crank B by one tooth (boss +x at the same moment as A).

## Checks (`python3 strandbeest_gripper/tools/verify_v8.py`)

Run on the built `.sc` (2026-11-15). 27 checks:

| Check | Result | |
|---|---|---|
| joints solve: no conflicts, nothing floating | {'rigid': 20, 'pin_slot': 2, 'revolute': 20} | PASS |
| full crank turn driven by O_A1: every 30 deg step moved, nothing held | 12 steps | PASS |
| 12 joint traces (J1, B, P of 4 legs) match fourbar.py (<= 0.01 mm) | 0.00023 mm (crank turns CCW for +O_A1) | PASS |
| jaw 1 keeps its orientation over the full turn (<= 0.02 deg) | 0.0001 deg | PASS |
| jaw 2 keeps its orientation over the full turn (<= 0.02 deg) | 0.0001 deg | PASS |
| jaw faces parallel: gap at the pin == gap near the tip (91 mm apart) (<= 0.02 mm) | max diff 0.0002 mm | PASS |
| clamp gap 1.53 +- 0.05 mm, open >= 19 mm | 1.53 .. 19.44 mm (v7: 1.53 .. 19.50) | PASS |
| feed stroke while clamped (gap within +0.4) >= 19.5 mm | 20.5 mm (v7 19.9) | PASS |
| leg-B pin stays centred in its 2 mm jaw slot (<= 0.05 mm) | 0.0002 mm | PASS |
| mesh A1 / X1: no overlap, >= 0.1 mm over one pitch + full turn | 0.142 mm | PASS |
| mesh X1 / B1: no overlap, >= 0.1 mm over one pitch + full turn | 0.142 mm | PASS |
| mesh X1 / X2: no overlap, >= 0.1 mm over one pitch + full turn | 0.142 mm | PASS |
| mesh X2 / A2: no overlap, >= 0.1 mm over one pitch + full turn | 0.142 mm | PASS |
| mesh X2 / B2: no overlap, >= 0.1 mm over one pitch + full turn | 0.142 mm | PASS |
| gears vs frame + top plate: no contact over a full turn, closest >= 0.45 mm | 0.500 mm | PASS |
| coupler A1 vs all (not its crank): no contact over a full turn, closest >= 0.45 mm | 0.500 mm | PASS |
| rocker A1 vs all (not the frame): no contact over a full turn, closest >= 0.45 mm | 0.500 mm | PASS |
| coupler B1 vs all (not its crank): no contact over a full turn, closest >= 0.45 mm | 0.500 mm | PASS |
| rocker B1 vs all (not the frame): no contact over a full turn, closest >= 0.45 mm | 0.500 mm | PASS |
| coupler A2 vs all (not its crank): no contact over a full turn, closest >= 0.45 mm | 0.500 mm | PASS |
| rocker A2 vs all (not the frame): no contact over a full turn, closest >= 0.45 mm | 0.486 mm | PASS |
| coupler B2 vs all (not its crank): no contact over a full turn, closest >= 0.45 mm | 0.500 mm | PASS |
| rocker B2 vs all (not the frame): no contact over a full turn, closest >= 0.45 mm | 0.486 mm | PASS |
| jaw 1 vs all: no contact over a full turn, closest >= 0.45 mm | 0.500 mm | PASS |
| jaw 2 vs all: no contact over a full turn, closest >= 0.45 mm | 0.500 mm | PASS |
| 19 pins / shafts / knob vs all parts at 12 crank angles: no overlap (X3: B / P pins drawn loose in the couplers); only pin-in-coupler pairs may be unchecked | 73+ pairs per angle, 0 overlaps; unchecked 0 | PASS |
| close pairs left out of the sweeps (coupler ring on its boss, rocker eye on its journal) at 12 crank angles: no overlap, none unchecked | 12+ pairs per angle, 0 overlaps, 0 unchecked, closest 0.000 mm (ring / journal play 0.15, thrust faces touch) | PASS |

## Fit (NEEDS PRINT TEST)

- **Pins:** 0.15 mm play per side in the Ø3.4 holes (pins Ø3.1 with two 0.25 mm flats). Snap barbs Ø4.0 over Ø3.4 (as v4b–v7).
- **B and P pins in the coupler (coupler X3, 2026-11-22):** Ø3.1 pins in Ø3.2 coupler holes (drawn 0.05 mm loose per side), with a 0.3 × 45° lead-in on both ends of each hole, 3.5 mm long. X1 (Ø2.9) and X2 (Ø3.05) were both too tight in the build: the B pins went into the rockers but not the couplers. Small vertical holes print about 0.1–0.2 mm small, so the X3 hole should print about Ø3.0–3.1, a snug fit. If the pins are loose, put a drop of CA glue in the coupler (not in the rocker); if still too tight, drill Ø3.1.
- **Eccentric:** coupler ring Ø25.54 on the Ø25.24 boss (0.15 per side). Its friction radius is about 13 mm, much bigger than a crank pin's, so the knob needs more torque than v7's. Grease it.
- **Crank shaft:** Ø5 with two flats 3.4 apart. It turns in Ø5.3 holes in the base and the plate stub, and keys the gear and the knob in 5.3 × 3.7 double-D holes. The barb (Ø5.9 over Ø5.3) clicks above the plate.
- **Rocker on the column:** eye Ø6.3 on the Ø6 journal.

## Not checked

- Anything printed: the fits above, the press pins, the snap barbs on the Ø5 shafts, and how the parts flex.
- Friction and torque at the knob (eccentric ring, 4 of them).
- Stiffness: the plate with its window, the 18 mm frame columns under a side load on the jaws, and the idler snap pins (held from the base only; they carry only tooth load).
- Gear strength (PETG, M1, 5 mm face).
- The gears stick out past the frame outline at the sides: no guard.

## Files

- `cad/GRIP-9016_assy-four-bar.json`: generated by `../tools/gen_v8.py` from `../tools/fourbar.py`.
- `cad/GRIP-9016_assy-four-bar.verify.json`: written by `../tools/verify_v8.py`.
- `exports/`: the complete print kit; `exports/plates/` holds the plates.
- `docs/build/`: the build-plan pictures (`../tools/build_guide_v8.py`).
- `fasteners.json`: no fasteners.
