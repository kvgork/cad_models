# finray_tests: hand-driven test gripper with slide-in fin-ray fingers (GRIP-9010)

X1, not printed yet. **NEEDS PRINT TEST.** A parallel gripper you close with a thumb knob, made to compare fin-ray finger designs on objects of 10–60 mm. The fingers slide in from the top on a dovetail, so you can swap designs in seconds. Five finger designs come with it: a baseline, one made to wrap around objects, one made to grip harder, and an angle-only pair (A at +15° and −15°) that isolates the rib angle.

![top view](docs/GRIP-9010_assy-finray-gripper_top.png)

*Top view, from the bottom of the picture up: the gripper with design A mounted, then design B, then design C (parked in front, not mounted). The pictures predate the angle-only pair, which is parked further in front in the CAD.*

![iso](docs/GRIP-9010_assy-finray-gripper_iso.png)

## How it works

- **Drive:** turn the knob. It turns an M6 screw that is held in the end wall and runs in a nut inside jaw A, so jaw A moves 1 mm per turn. Clockwise, seen from the knob, opens the jaws; counter-clockwise closes them.
- **Symmetry:** jaw A's rack turns a z18 pinion in the base, and the pinion moves jaw B's rack the other way. Both jaws close evenly about the centre line, so the object doesn't shift sideways.
- **Range:** grip faces 2 mm apart (closed) to 70 mm (open). That is 34 knob turns end to end.
- **Fingers:** each finger has a dovetail tongue on its root and slides down into the groove in a jaw from above, until it sits on the groove floor. Grip forces push the finger sideways, not up, so friction holds it. The left finger is the same part as the right one, turned over: print 2 of each design.
- **Squeeze control:** with an M6 screw (1 mm pitch) you can feel and repeat the squeeze. For a fair comparison, count knob turns past first contact (for example, contact + 3 turns = 6 mm of total squeeze).

## The fin-ray designs

All five have the same outline, so they swap directly and grip at the same place: 60 mm long, 20 mm wide at the root, a 2 mm tip and 20 mm tall. Each is printed in TPU 90A. Only the inside changes: the number of ribs, their angle and the wall thickness. Thicknesses are on the 0.45 mm extrusion-line grid (2, 3 or 4 lines).

**Rib angle convention:** 0° means the rib is square to the grip face. **+** means the rib leans toward the tip on its way from the grip face to the back face. **−** means it leans toward the root.

| Design | PN | Ribs | Angle | Rib / wall | What it should do (hypothesis to test) |
|---|---|---|---|---|---|
| **A baseline** | GRIP-0057 | 6 | 0° | 0.9 / 1.35 mm | The classic fin ray: the reference for the other two. Wraps moderately, medium grip force. |
| **B wrap** | GRIP-0058 | 5 | +15° | 0.9 / 0.9 mm | **Most compliant.** Few, thin ribs leaning toward the tip let the grip face bend into the object, so it wraps furthest around round or fragile objects (fruit, eggs, cups) at a low squeeze. It holds the least: it can let a heavy object slip or roll. |
| **C stiff** | GRIP-0059 | 7 | −15° | 1.35 / 1.8 mm | **Most force.** Thicker walls (1.8 mm) and more, thicker ribs should give a higher grip force for the same knob squeeze, so it should hold boxes and heavy items best. It conforms less, touching a round object over a shorter stretch, and could mark soft objects. Whether the −15° lean adds to that is **not known** (see below). |
| **A+15** | GRIP-0067 | 6 | +15° | 0.9 / 1.35 mm | **Angle only.** A with only the rib angle changed. Compared with A and A−15 it shows which lean is stiffer *in this profile*. |
| **A−15** | GRIP-0068 | 6 | −15° | 0.9 / 1.35 mm | **Angle only.** The mirror of A+15. |

**Why these effects are expected (revised 2026-11-14 after a verified literature review, vault page `05-Wiki/research/2026-11-14-fin-ray-grasping.md`):**
- **Walls and material matter more than rib angle.** In the studies, flank (wall) thickness and TPU hardness set the force level (bending stiffness grows with wall thickness cubed; TPU 95A held 5.6–7.6× more than 60A on one finger). Rib angle changes force by tens of percent. So B's and C's expected differences come mainly from their walls and rib count, not their angles.
- **B and C cannot isolate the angle.** Each changes 3–4 things at once (rib count, angle, rib thickness, wall thickness). A+15 and A−15 change only the angle; compare those with A.
- **The rib-angle direction is an open question.** No paper defines the sign of its rib angle in the text, only in figures. Read through its figure, the "negative, stiffer" ribs in [Dong et al., arXiv 2303.12987](https://arxiv.org/pdf/2303.12987) lean toward the *tip* in this README's convention, the opposite of C. Its own numbers also give the negative angle the *lowest* buckling force (−10° 1.15 N, 0° 1.2 N, +10° 1.35 N), against its prose.
- **Correction: C is not "close to the optimum" of [arXiv 2606.03798](https://arxiv.org/pdf/2606.03798).** That paper's best contact force is 9.884 N (3.57 N was only its width sweep), its −15° has no defined sign, and its finger is different (100 mm tall, TPU 95A).
- **Classic layout:** in this profile the back face slopes about 16.7°, so the symmetric Festo-style rib layout would be about +8°, not A's 0°.
- **The effects above are hypotheses; measuring them is what this rig is for.**

**Suggested test (per design, same objects; revised 2026-11-14):**
1. **Squeeze sweep:** close until the fingers first touch the object, then measure at 2, 4, 6 and 8 knob turns past contact (1 mm per jaw per turn; 12 if the object allows). Festo rates its 50 mm fingers to about 12 mm indentation, so 3 turns is too little to show the differences. Plot each result against squeeze: holding force flattens as squeeze rises, so one squeeze level can mislead.
2. **Contact point:** grip at mid-finger (25–30 mm from the root) and mark it on every finger. Test the pen at the tip as well, where fin rays are weakest.
3. **Hold:** pull the object out upward slowly with a luggage scale and note the peak force. Use at least 2 printed samples per design, 3 pulls each, the same pause after closing, and repeat the first pull at the end to catch permanent set.
4. **Sideways and twist:** also pull the object along the 20 mm finger height and twist it. This is the documented fin-ray failure; the 10 mm pen is the critical case.
5. **Wrap:** photograph from above with a scale bar and measure the contact length along each grip face.
6. **Objects:** a 40 mm ball or fruit, a 30 mm cube (square and at 45°), a 10 mm pen, a 60 mm cup, plus a soft object (foam ball or ripe fruit). Rib differences show mostly on objects about as soft as the finger.
7. **Friction:** test all designs bare first. If you add grip tape, add it to all of them.
8. **Failures:** note the type (tip opening, root bulge, back-wall S-bend, ribs touching, twist, slip) and the room temperature. Don't test straight after printing or drying.
9. Write the results into this README. The CAD values stay **NEEDS PRINT TEST** until then.

## Print list

<!-- printlist:start -->
<!-- generated by tools/printlist.py; do not edit by hand -->
**15 prints from 10 STL files.** Quantities counted from the assembly `cad/GRIP-9010_assy-finray-gripper.json` (purchased parts left out). The `.3mf` and `.step` of each part are next to the STL.

| Qty | File (`exports/`) | Part | Material |
|---|---|---|---|
| 1 | `GRIP-0052_base-plate_X1.stl` | BASE, FINRAY GRIPPER, RAIL + SCREW WALL + PINION POST | PETG, FDM |
| 1 | `GRIP-0053_carriage-a_X1.stl` | CARRIAGE, JAW A, NUT TRAP + RACK, FINRAY GRIPPER | PETG, FDM |
| 1 | `GRIP-0054_carriage-b_X1.stl` | CARRIAGE, JAW B, RACK + ARM, FINRAY GRIPPER | PETG, FDM |
| 1 | `GRIP-0055_pinion-z18_X1.stl` | GEAR, PINION, Z18 M1, FINRAY GRIPPER | PETG, FDM |
| 1 | `GRIP-0056_knob_X1.stl` | KNOB, THUMB, D32, M6 HEX HEAD | PETG, FDM |
| 2 | `GRIP-0057_finray-a-baseline_X1.stl` | FINGER, FIN RAY, A BASELINE, 6 RIBS 0 DEG | TPU 90A, FDM |
| 2 | `GRIP-0058_finray-b-wrap_X1.stl` | FINGER, FIN RAY, B WRAP, 5 RIBS +15 DEG THIN | TPU 90A, FDM |
| 2 | `GRIP-0059_finray-c-stiff_X1.stl` | FINGER, FIN RAY, C STIFF, 7 RIBS -15 DEG THICK | TPU 90A, FDM |
| 2 | `GRIP-0067_finray-a-plus15_X1.stl` | FINGER, FIN RAY, A ANGLE-ONLY, 6 RIBS +15 DEG | TPU 90A, FDM |
| 2 | `GRIP-0068_finray-a-minus15_X1.stl` | FINGER, FIN RAY, A ANGLE-ONLY, 6 RIBS -15 DEG | TPU 90A, FDM |
<!-- printlist:end -->

## Print plates (Bambu Studio)

The PETG parts and the TPU fingers are on separate plates:

- **`exports/plates/GRIP-9010_assy-finray-gripper_plate1-petg_X1.3mf`:** base, both carriages, pinion and knob, in PETG.
  - The base and carriages print bottom down, without supports. The rail channel roof (14.7 mm) and the jaw B arm (29 mm) are bridges.
- **`exports/plates/GRIP-9010_assy-finray-gripper_plate2-tpu-90a_X1.3mf`:** all ten fingers (2 × A, B, C, A+15, A−15), in TPU 90A.
  - The fingers lie flat on their profile, so every rib is a vertical wall.
  - Settings: 2–3 walls, slow (≈ 25 mm/s). Infill hardly matters: the ribs are walls.
  - On the X2D: print TPU on the **main (left) hotend only** (the auxiliary hotend cannot feed TPU), standard 0.4 mm nozzle (not high-flow; Bambu TPU 85A needs 0.6 mm, so it does not fit these 0.9 mm ribs). Feed from the AMS HT rear outlet through the TPU Feed Assist Module, or from a spool above the toolhead; no AMS auto-feed. Dry in the AMS HT at 75 °C for 18 h first: wet TPU weakens the 0.9 mm ribs. Profile *Bambu TPU 90A @BBL X2D 0.4 nozzle*, max volumetric speed 2.8 mm³/s (don't raise). Material options: vault page `05-Wiki/research/2026-11-14-tpu-filaments-for-grippers.md`.

## Fastener BOM

<!-- fasteners:start -->
<!-- generated by tools/printlist.py from fasteners.json; edit that file -->
The M6 screw is the lead screw: one knob turn = 1 mm per jaw. Lengths from the model: the M6x70 runs from the knob to 3 mm short of jaw B at full close; the M3x8 grips 7.5 mm into the Ø2.5 hole in the pinion post (thread-forming).

**Shopping list**

| Qty | Item |
|---|---|
| 1 | M3 washer (DIN 125) |
| 1 | M3×8 socket head screw (ISO 4762) |
| 1 | M6 hex nut (ISO 4032) |
| 1 | M6 nyloc nut (DIN 985) |
| 1 | M6×70 hex screw, full thread (ISO 4017) |

**Where they go**

| Qty | Fasteners (each) | Where |
|---|---|---|
| 1 | M6×70 hex screw, full thread (ISO 4017) | lead screw: head pressed into the knob, through the end wall and jaw A |
| 1 | M6 nyloc nut (DIN 985) | inside the end wall: holds the screw axially; snug, not tight, so it still turns |
| 1 | M6 hex nut (ISO 4032) | jaw A nut trap (drop in from the top) |
| 1 | M3×8 socket head screw (ISO 4762) + M3 washer (DIN 125) | pinion retainer, on the post |
<!-- fasteners:end -->

## Assembly

1. **Pinion:** put the pinion on the post in the base, then the M3 washer and M3×8 screw on the post top. The washer sits on the post, 0.3 mm above the pinion, so the pinion turns freely.
2. **Nut:** drop the M6 nut into the slot in jaw A (GRIP-0053), from the top.
3. **Jaws:** slide both jaws onto the rail from the open end (+X). Jaw A goes on first and goes furthest, to the wall side. Jaw B's rack goes under the pinion and its arm over the pinion screw head.
   - **Timing:** set both jaws the same distance from the centre before the racks engage the pinion.
4. **Screw:** press the M6×70 hex head into the knob. Push the screw through the wall, put on the nyloc nut (snug, not tight), and screw it into jaw A's nut.
5. **Fingers:** slide the fingers into the grooves from above. They are interchangeable left and right.

## Fit (NEEDS PRINT TEST)

| Fit | CAD | If it is wrong |
|---|---|---|
| Jaws on the dovetail rail | 0.25 mm per side (`SLIDE`) | Sticky: sand the rail flanks, or raise it to 0.3. Wobbly: 0.2. |
| Finger tongue in groove (TPU in PETG) | 0.15 mm per side (`FIT`) | Too tight: 0.2 (TPU swells a bit). Falls out: 0.10. |
| Pinion bore on the post | Ø6.3 on Ø6 | |
| M6 head in the knob | 10.1 mm across flats on a 10 mm head | Loose: a drop of CA glue. |
| Rack and pinion | 0.3 mm backlash, closest gap 0.141 mm (CAD) | If it binds, lift the pinion and check that both jaws are timed the same. |

Change the values in `tools/gen_finray.py` and rebuild.

## Checks (`python3 finray_tests/tools/verify_finray.py`)

All 13 checks pass (2026-11-08; re-run 2026-11-14 after adding A+15 / A−15):

| Check | Result |
|---|---|
| Joints | 13 joints and 3 motion links (screw, rack → pinion, pinion → rack), no conflicts, nothing floating |
| Jaws move symmetrically about x = 0 over the whole stroke | max \|xA + xB\| 0.0000 mm, no movement off the X axis |
| Grip-face range | 1.00 … 35.00 mm per side (gap 2 … 70 mm) |
| Thumb screw | one knob turn = 1.00 mm |
| Rack and pinion ratio | 9 mm of rack = 57.30° on the pinion (r = 9) |
| Stroke sweeps (jaws and fingers vs base and each other) | no collision; closest 0.25 mm (the rail clearance) |
| Rack and pinion mesh at 10 positions (a tooth pitch + both stroke ends) | no overlap, closest 0.141 mm |
| Closed / open finger gap | 2.00 / 70.00 mm |
| Finger tongues in grooves | no overlap |
| Screw, nyloc, nut and knob vs jaws and base at both ends | no overlap. The nyloc touches the wall face, as intended |
| Finger volumes vs hand calculation | A 6591.1 vs 6591.2, B 5504.9 vs 5504.9, C 8254.9 vs 8254.9, A+15 6555.7 vs 6555.7, A−15 6698.1 vs 6698.1 mm³ (STL, 2026-11-14) |

**Not checked:**
- How the fingers bend: the fin-ray effect itself. There is no FEA; the print test answers it.
- Rail friction, TPU swelling and screw torque.
- Only design A is checked mounted. The other four have the same outline and tongue, so the fit, gap and sweep results carry over.

## Files

- `cad/GRIP-9010_assy-finray-gripper.json`: generated by `tools/gen_finray.py`. Build it with `tools/build.sh finray_tests`. The fin-ray designs are in its `DESIGNS` table, so a fourth design is one more line plus a new part number.
- `tools/verify_finray.py`: the checks above.
- `exports/`: the complete print kit; `exports/plates/` holds the ready-to-slice plates.
- `docs/`: pictures.
