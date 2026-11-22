# v2: rod + crossed links finger (GRIP-9021), concept C6 made printable

X1, CAD-checked, not printed yet. **NEEDS PRINT TEST.**

The finger has one degree of freedom: one input curls all three joints along a fixed path.
- A horn on the SCS0009 axis pushes a **rod** up to a lever on the proximal, which flexes the MCP. This is the Pollen Amazing Hand drive.
- A **crossed link** from a lug on the base (B0) to an ear on the middle (M1) makes the PIP follow the MCP.
- A second crossed link from an ear on the proximal (P1) to an ear on the distal (D1) makes the DIP follow the PIP. This is the BiDexHand-style coupling.

It drives both ways and needs no spring. The pose is set by the horn angle.

**Hand first:** a printed dummy servo (GRIP-0156) slides into the cradle, the horn turns on its Ø3.7 stub, and you turn the horn by its lever. **Servo later:** the SCS0009 slides in instead of the dummy, between the fork posts, and the same horn goes on its spline. Nothing else changes.

Picked by the user on 2026-11-22 ("working prototypes, C5 + C6 only") from the massing [concepts](../concepts/README.md). C5 is [v1_raptor-cord](../v1_raptor-cord/README.md).

| As built (straight, from −Y) | Horn at 60° | Servo stage |
|---|---|---|
| ![done](docs/build/step10_done_front.png) | ![curled](docs/build/step11_curled.png) | ![servo](docs/build/servo_stage.png) |

## Spec

| Item | Value |
|---|---|
| Finger | Same phalanx core as v1: 18 wide × 16 thick, joints 45 / 25 / 22 mm apart (MCP→PIP→DIP→tip). The knuckles, pins, extension spurs and MCP fork come from `finger_common.py`. There are no cord channels. |
| Motion (model `fingerlinks.py`, matched by the CAD trace) | Horn 0 → 96.3°: MCP 0 → 80.0°, PIP 0 → 89.9°, DIP 0 → 70.3°, all rising monotonically. The worst transmission angle is 33.2°, so nothing comes near a toggle. With any one link 0.1 mm off, the end angles move by at most PIP 0.6°, DIP 0.7° and horn 0.5°. |
| Link lengths (pin to pin) | rod 35.44, PIP link 47.11, DIP link 27.01, horn radius 12.0 |
| Pivots (straight pose; x = back +, z up from the dovetail bottom) | B0 (11.9, 70.3) on a −Y cheek lug; M1 = PIP + (−11.3, 5.8), on a palm ear on −Y; P1 = PIP + (5.1, 5.0), on a back ear on +Y; D1 = DIP + (−7.3, 4.0), on a palm ear on +Y; L = MCP + (14.4, −4.0), on the lever arm; H on the horn at −75° |
| Range (CAD, joint.find_limits on the horn, every printed part) | −1.4 … 99.0°. The straight end stops on the DIP spur; the curled end stops at the PIP's flex stop (92.8°). That leaves 2.7° past the 96.3° stroke. |
| Layers in Y | −Y side: PIP link −17.3 … −14.3, M1 ear and B0 lug/boss −14.0 … −9.3. +Y side: lever arm 2 … 9, L boss 9 … 12.3, P1/D1 ears 9.3 … 14.0, rod 12.6 … 16.6, DIP link 14.3 … 17.3, horn 16.9 … 22.45 (gear collar at 22.75). Ears sit outside the finger's 18 mm width. Each ear has a pocket round the knuckle pin end it covers, and each link pin's barb is recessed in the ear's inner face. |
| Pins | One-piece snap pins, Ø3.1 with 2 flats, in Ø3.4 holes (0.15 per side). The MCP and PIP/DIP pins are the v1 parts. The new ones are the ear pin (shank 6.2, ×4: M1, P1, D1 and horn H), the B0 pin (8.1) and the lever pin (14.7). |
| Base | Same as v1, using the GRIP-0002 dovetail (numbers checked) with the dovetail centred under the footprint (dt_y 19.25) and 45° undersides. The cradle sits deeper (servo tab plane at y 31.5, v1 15.75), so the horn and rod layers fit between the finger and the servo. The base is 40 × 64.8 × 74.8. No cord or elastic bars. |
| Horn | Hub on the Ø4.0 spline (bore drawn Ø4.1: small vertical holes print 0.1–0.2 small, so it grips). It has a 1.0 plate for an M2 screw and a hand lever 22 long ending in a Ø10 pad. On the dummy's Ø3.7 stub it turns with 0.2 per side. |
| Dummy servo | The SCS0009 case envelope, 0.1 smaller per side than the pocket, with a front block and a Ø3.7 stub where the spline is. Slide fit: no tabs, so it prints with no overhangs. It has a Ø1.6 pilot hole for the optional horn screw. In the CAD it is parked 60 mm +X of the base because it shares the servo's place. |

## Parts

| PN | Part | Qty | Size (STL, mm) | Pin spacing (generator) | Print orientation |
|---|---|---|---|---|---|
| GRIP-0148 | base-finger-rod | 1 | 40.0 × 64.8 × 74.8 | MCP to B0: 15.4 | dovetail down |
| GRIP-0149 | phalanx-proximal-rod | 1 | 26.4 × 23.0 × 64.4 | MCP–PIP 45; MCP–L 15.0; PIP–P1 7.1 | on its palm (−X down) |
| GRIP-0150 | phalanx-middle-rod | 1 | 23.3 × 23.0 × 43.4 | PIP–DIP 25; PIP–M1 12.7 | on its back (+X down) |
| GRIP-0151 | phalanx-distal-rod | 1 | 19.3 × 23.0 × 32.4 | DIP–D1 8.3; DIP to tip 22 | on its back |
| GRIP-0152 | horn-rod-scs0009 | 1 | 24.7 × 5.6 × 38.6 | axis–H 12.0, lever 22 | flat (−Y down) |
| GRIP-0153 | rod-push-mcp | 1 | 18.3 × 4.0 × 40.6 | 35.44 | flat |
| GRIP-0154 | link-pip-coupler | 1 | 30.2 × 3.0 × 48.0 | 47.11 | flat |
| GRIP-0155 | link-dip-coupler | 1 | 19.4 × 3.0 × 31.0 | 27.01 | flat |
| GRIP-0156 | dummy-servo-scs0009 | 1 | 12.9 × 28.8 × 24.1 | — | on its back face, stub up |
| GRIP-0144 | snap-pin-2f-finger-mcp (v1 part) | 1 | 27.9 long | — | on a flat |
| GRIP-0145 | snap-pin-2f-finger-knuckle (v1 part) | 2 | 21.3 long | — | on a flat |
| GRIP-0157 | snap-pin-2f-link-ear | 4 | 9.4 long | — | on a flat |
| GRIP-0158 | snap-pin-2f-link-base | 1 | 11.3 long | — | on a flat |
| GRIP-0159 | snap-pin-2f-lever | 1 | 17.9 long | — | on a flat |

The rod, PIP link and DIP link are easy to tell apart by length: 35.4, 47.1 and 27.0 between their holes. The three new pin lengths are 9.4, 11.3 and 17.9. Print orientations are in `print_orient.json`. The A4 [sorting sheet](docs/GRIP-9021_assy-finger-rod-fourbar_sort-sheet_A4.pdf) shows every part at 1:1.

## Print list

<!-- printlist:start -->
<!-- generated by tools/printlist.py; do not edit by hand -->
**18 prints from 14 STL files.** Quantities counted from the assembly `cad/GRIP-9021_assy-finger-rod-fourbar.json` (purchased parts left out). The `.3mf` and `.step` of each part are next to the STL.

| Qty | File (`exports/`) | Part | Material |
|---|---|---|---|
| 1 | `GRIP-0144_snap-pin-2f-finger-mcp_X1.stl` | PIN, SNAP, PRINTED, D3, 2 FLATS, MCP (BASE CHEEKS + PROXIMAL) | PETG, FDM |
| 2 | `GRIP-0145_snap-pin-2f-finger-knuckle_X1.stl` | PIN, SNAP, PRINTED, D3, 2 FLATS, PIP / DIP KNUCKLE | PETG, FDM |
| 1 | `GRIP-0148_base-finger-rod_X1.stl` | BASE, ARTICULATED FINGER V2, CENTRED DOVETAIL, SCS0009 CRADLE (DEEP), MCP FORK, B0 LUG | PETG, FDM |
| 1 | `GRIP-0149_phalanx-proximal-rod_X1.stl` | PHALANX, PROXIMAL 45, KNUCKLE FORK, MCP LEVER ARM, P1 EAR, ARTICULATED FINGER V2 | PETG, FDM |
| 1 | `GRIP-0150_phalanx-middle-rod_X1.stl` | PHALANX, MIDDLE 25, KNUCKLE TONGUE + FORK, M1 EAR, ARTICULATED FINGER V2 | PETG, FDM |
| 1 | `GRIP-0151_phalanx-distal-rod_X1.stl` | PHALANX, DISTAL 22, KNUCKLE TONGUE, ROUND TIP, D1 EAR, ARTICULATED FINGER V2 | PETG, FDM |
| 1 | `GRIP-0152_horn-rod-scs0009_X1.stl` | HORN, ROD DRIVE, ON SCS0009 SPLINE OR DUMMY STUB, HAND LEVER | PETG, FDM |
| 1 | `GRIP-0153_rod-push-mcp_X1.stl` | ROD, PUSH, HORN TO MCP LEVER, ARTICULATED FINGER V2 | PETG, FDM |
| 1 | `GRIP-0154_link-pip-coupler_X1.stl` | LINK, CROSSED, BASE B0 TO MIDDLE M1 (PIP FOLLOWS MCP) | PETG, FDM |
| 1 | `GRIP-0155_link-dip-coupler_X1.stl` | LINK, CROSSED, PROXIMAL P1 TO DISTAL D1 (DIP FOLLOWS PIP) | PETG, FDM |
| 1 | `GRIP-0156_dummy-servo-scs0009_X1.stl` | DUMMY, SCS0009 ENVELOPE, D3.7 STUB, HAND OPERATION BEARING FOR THE HORN | PETG, FDM |
| 4 | `GRIP-0157_snap-pin-2f-link-ear_X1.stl` | PIN, SNAP, PRINTED, D3, 2 FLATS, SHANK 6.2, LINK EARS + HORN | PETG, FDM |
| 1 | `GRIP-0158_snap-pin-2f-link-base_X1.stl` | PIN, SNAP, PRINTED, D3, 2 FLATS, SHANK 8.1, PIP LINK ON BASE LUG | PETG, FDM |
| 1 | `GRIP-0159_snap-pin-2f-lever_X1.stl` | PIN, SNAP, PRINTED, D3, 2 FLATS, SHANK 14.7, ROD ON MCP LEVER | PETG, FDM |
<!-- printlist:end -->

<!-- fasteners:start -->
<!-- generated by tools/printlist.py from fasteners.json; edit that file -->
No screws for the hand stage: every joint uses a printed snap pin, and the dummy servo is a 0.1-per-side slide fit in the cradle. Optional: one M2 screw holds the horn on the dummy's stub (pilot hole) or, at the servo stage, on the spline. Servo stage: the SCS0009 comes with its tab screws. Horn screw length from the model: head in a 1.6 counterbore, through the 1.0 plate, 0.35 gap, ~4 mm into the spline's 5 mm core hole, NEEDS CHECK.

**Shopping list**

| Qty | Item |
|---|---|
| 1 | M2×6 pan or socket head screw (NEEDS CHECK) |
| 2 | M2×6 self-tapping screw (supplied with the SCS0009) |

**Where they go**

| Qty | Fasteners (each) | Where |
|---|---|---|
| 1 | M2×6 pan or socket head screw (NEEDS CHECK) | horn onto the dummy stub (hand) or the SCS0009 spline (servo), head in the horn's -Y counterbore |
| 2 | M2×6 self-tapping screw (supplied with the SCS0009) | servo stage only: SCS0009 tabs into the cradle face (Ø1.6 pilot holes) |
<!-- fasteners:end -->

## Print plate

`exports/plates/GRIP-9021_assy-finger-rod-fourbar_plate1-petg_X1.3mf` holds all 18 parts on one PETG plate (X2D, Textured PEI). Bambu Studio estimates **~42 g, ~126 min**, and its slice gave no warnings. A voxel scan of every STL in its print orientation found no floating layer islands. The pins lie on a flat.

![plate](exports/plates/GRIP-9021_assy-finger-rod-fourbar_plate1-petg_X1.png)

## Build plan

Each part goes on with its own pins straight away, so nothing loose waits for a pin. All snap pins push in from the head side until the barb clicks.

| Step | Picture |
|---|---|
| 1. Base. | ![1](docs/build/step1_base.png) |
| 2. Slide the dummy servo into the cradle, stub first out (hand stage). | ![2](docs/build/step2_dummy.png) |
| 3. Proximal between the base cheeks, then the MCP pin (GRIP-0144) from −Y. The lever arm points to the back (+X). | ![3](docs/build/step3_proximal.png) |
| 4. Middle onto the proximal's fork, then a knuckle pin (GRIP-0145) from −Y. | ![4](docs/build/step4_middle.png) |
| 5. Distal onto the middle's fork, then the second knuckle pin. | ![5](docs/build/step5_distal.png) |
| 6. DIP link (27.0) on the +Y side: an ear pin (GRIP-0157) from +Y through the link into the proximal's P1 ear, and another into the distal's D1 ear. The barbs click into the ears' inner counterbores. | ![6](docs/build/step6_dip-link.png) |
| 7. PIP link (47.1) on the −Y side (view from −Y): the B0 pin (GRIP-0158) from −Y through the link and the base lug, then an ear pin from −Y into the middle's M1 ear. | ![7](docs/build/step7_pip-link.png) |
| 8. Rod (35.4) onto the lever: the lever pin (GRIP-0159) from +Y through the rod's top hole and the L boss. | ![8](docs/build/step8_rod.png) |
| 9. Horn onto the dummy's stub (optional M2×6 screw), lever toward the palm side. Then an ear pin from the rod's counterbored −Y side through the rod's bottom hole into the horn (the barb clicks in the horn's +Y counterbore). | ![9](docs/build/step9_horn.png) |
| 10. Done. Turn the horn lever: the finger curls, and all three joints move together. | ![10](docs/build/step10_done_back.png) |

**Servo stage:** take off the horn, slide out the dummy, slide in the SCS0009 (tabs on the cradle face, 2 supplied screws) and put the horn on the spline with the M2 screw. Centre the servo first: horn 0° (finger straight) is the stop on the spurs, and the stroke is 96.3° of the servo's 300°.

## Checks (`python3 articulated_finger/tools/verify_v2.py`)

Run on the built `.sc` on 2026-11-22: 12 checks, **12 PASS**. The link model `python3 articulated_finger/tools/fingerlinks.py` asserts its own targets and is also run by the generator.

| Check | Result |
|---|---|
| No feature errors or warnings (vendor STEP tolerance note ignored) | PASS: none |
| Dovetail parameters == GRIP-0002 | PASS |
| Joints solve: no conflicts, nothing floating (the SCS0009 import is placed, not jointed) | PASS: 10 revolute, 18 rigid |
| Horn driven 0 … 96.3° in 10 steps: everything moved, nothing held, and MCP / PIP / DIP match fingerlinks.py within 0.5° | PASS: max error 0.000°; end MCP 80.0, PIP 89.9, DIP 70.3 |
| Horn range to first contact (joint.find_limits, every printed part, linkage following) | PASS: −1.4 … 99.0°. The straight end stops at distal/middle (the DIP spur); the curled end stops at middle/proximal (the PIP flex stop). |
| Printed parts at horn 0 / 32 / 64 / 96°: clearance plus exact boolean interference, nothing unchecked, ≥ 0.09 | PASS ×4: closest 0.100 each time (pin heads 0.1 off their faces); interference 0 |
| SCS0009, lifted 0.05: tab seat 0.05; horn ≥ 0.05 (bore on the spline); everything else ≥ 0.3 | PASS: seat 0.050, spline in horn 0.075, horn face to collar 0.25 |
| Servo slides in and out along Y between the fork posts with the horn off (50 mm, 25 steps): no overlap, ≥ 0.3 to the base | PASS: closest 0.499 |
| Dummy servo in the pocket (0.1 per side): exact interference none; stub in the horn bore ≥ 0.15 | PASS: interference 0, stub 0.20 |

**Two clearance readings are exempted, each proven another way.** The kernel reads 0 at two cut mouths: the MCP pin's flat edge where it passes the cheek face, and the dummy's case corner at the pocket mouth on the cradle face. In both places the parts are 0.15 / 0.1 apart by construction, and the exact `inspect.interference` check at the same poses finds no overlap (the CLAUDE.md mouth-edge lesson).

## Not checked

- **Forces:** the servo torque (0.226 N·m stall) through horn r 12 gives about 19 N on the rod. Pin bending, ear strength and link buckling were not checked. The ear pins bear on only 2.8 mm of ear.
- **Print fit:** the Ø3.4 holes are horizontal teardrops in the phalanges and base, and vertical in the links, rod and horn. Nothing is printed yet. The horn's Ø4.1 spline bore grip and its Ø3.7 stub play are guesses. The dummy's 0.1-per-side slide fit may be too tight or too loose.
- **Fit on the real tester baseplate:** the base is 64.8 deep in Y, and the cradle reaches y 50.8, past the dovetail. It has not been checked against the baseplate's +Y lock rail and thumb screw (as for v1).
- **The horn screw** M2×6 length (NEEDS CHECK), and whether the M2 pilot in the dummy's Ø3.7 stub (1.05 wall) splits.
- **Hand feel:** the hand lever is 22 long, and its pad moves through 96° near the palm side. It may be awkward to reach once mounted on the tester.
- **Servo control:** the horn's zero and its direction on the real SCS0009.
