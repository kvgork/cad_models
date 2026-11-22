# articulated_finger / concepts: single-finger concepts (massing stage)

These are concept models: blocks, joint axes, mechanism parts and the real SCS0009 STEP, so you can compare layout and size. **No part numbers and no print kit yet.** After you pick 1–2 concepts, each gets a version folder, part numbers in `PARTS.md` and the full kit. **NEEDS PRINT TEST** applies to everything here.

## Common to all six

| Item | Value |
|---|---|
| Finger | 18 wide (Y) × 16 thick (X); proximal 45, middle 25, distal 22 = **92 mm** from MCP to tip (human index ≈ 91). Flexes in XZ, palm side is −X. |
| Mount | Dovetail 34 → 28 wide, 6 tall, 40 long: the **GRIP-0002 numbers** (the verifier compares them with GRIP-0002's script). It slides into the tester baseplates GRIP-0001 and GRIP-0069. |
| Servo | Feetech SCS0009 (`base/feetech_scs0009`, LIB-0010) in a cradle on the base. Output axis along −Y at z 34.5, tabs seated on the cradle face, 0.5 mm around the case. |
| Hand first | Each concept says what replaces the servo for hand operation. The drive path stays the same, so the later swap to the servo changes only one part. |
| Servo budget | 2.3 kg·cm stall / 0.75 kg·cm rated (datasheet) = 0.226 / 0.074 N·m. A spool or horn of r 6 mm then pulls **37.6 N stall / 12.3 N rated**. |

Colours: grey = base, orange = phalanges, blue = mechanism, black = servo. Pictures look at the back (dorsal) side.

## The six concepts

### New designs

| | **C1 Geared coupled** | **C2 Push-pull spine** | **C3 Rolling contact** |
|---|---|---|---|
| Picture | ![C1](docs/C1_geared-coupled.png) | ![C2](docs/C2_push-pull-spine.png) | ![C3](docs/C3_rolling-contact.png) |
| How it moves | The servo spline **is** the MCP. A gear fixed to the base and idler-gear chains in proximal and middle turn PIP and DIP by the same angle as the MCP: a fixed 1:1:1 curl, driven both ways. | A flexible band (PETG strip or TPU) runs in a palm-side channel to the distal. A servo crank pulls it to curl and pushes it to extend. One actuator, both directions, no spring. | Each joint is two rolling convex surfaces held by crossed straps, with no pin. One palm-side tendon to a servo spool; elastic dorsal straps return it. Rolling halves the wear and the contact point moves with the curl. |
| Hand first | Knob on a dummy servo block that has the same tab holes. | Thumb tab on the band, sliding in a slot in the base. | Pull ring on the tendon. |
| Joints | 1 DOF, fully coupled | 1 DOF, underactuated (curls around objects) | 1 DOF, underactuated |
| Printed parts (approx.) | base, 3 phalanges, about 9 gears, dummy servo block | base, 3 phalanges, band, crank | base, 3 phalanges, spool, 2 strap sets |
| Pros | Exact, repeatable pose from servo position; no tendon or spring to tension | Two-way drive without a return spring; simple parts | New for this repo; joint has no pin to wear; smooth curl |
| Risks | Gears for an 18 mm finger are m0.5 z17, which is below what FDM prints well (repo rule z ≥ 17). Backlash adds up over 3 joints. Tip force at full reach is low: 0.8 N rated / 2.4 N stall. | The band buckles when pushed unless the channel guides it closely; friction in the channel | Straps must be printed in TPU and pretensioned; joint stiffness is hard to predict |

### Based on open-source hands

| | **C4 OpenHand flexure** | **C5 Raptor cord + elastic** | **C6 Amazing rod + four-bar** |
|---|---|---|---|
| Picture | ![C4](docs/C4_openhand-flexure.png) | ![C5](docs/C5_raptor-cord-elastic.png) | ![C6](docs/C6_amazing-rod-fourbar.png) |
| Source | Yale OpenHand T42/M2: underactuated, one tendon, flexure joints. [project page](https://www.eng.yale.edu/grablab/openhand/) (CC BY-NC 3.0: copy the principle, not the files) | e-NABLE Raptor Reloaded: cord on the palm side, elastic on the back, printed pins. [Raptor](https://enablingthefuture.org/upper-limb-prosthetics/the-raptor-hand/) (CC BY-SA 3.0) | Pollen Amazing Hand: SCS0009 horn → rod drive ([repo](https://github.com/pollen-robotics/AmazingHand), Apache-2.0 / CC BY 4.0). BiDexHand: four-bar couples DIP to PIP ([repo](https://github.com/wengmister/BiDexHand), MIT). |
| How it moves | Rigid PETG segments with one TPU flexure strip through all joints (Yale casts urethane; we print TPU). One tendon from the tip to a servo spool. The flexure springs it open. | Pin joints. A Dyneema cord on the palm side goes to a spool; an elastic cord on the back opens the finger. | Servo horn → push rod → lever on the proximal (MCP). A coupler from the base to the middle and a crossed link from proximal to distal make PIP and DIP follow, so one servo curls all three joints. |
| Hand first | Pull ring on the tendon. | Slider with a ratchet, as on the Raptor, or a pull ring. | Hand crank on a dummy servo block. |
| Joints | 1 DOF, underactuated | 1 DOF, underactuated | 1 DOF, coupled (linkage sets the curl) |
| Printed parts (approx.) | base, 3 phalanges, TPU strip, spool | base, 3 phalanges, 3 pins, spool or slider | base, 3 phalanges, horn, rod, 2 links, pins |
| Pros | Fewest parts; well proven; shapes itself to objects; no pins | Simplest to print and assemble; the hand stage is natural; proven at scale | Rigid, both ways, repeatable; uses the servo the Amazing Hand was built for; motion can be checked with joint.sweep |
| Risks | TPU flexures creep and print differently per printer; the off-axis stiffness is low | Cord creep and slack (needs a re-tension point); the elastic sets the opening force the servo must beat | Most parts and pins; four-bar lengths need a fit (like strandbeest v8); rod, lever and links beside the finger make it about 24 mm wide overall |

### Add-on: soft TPU fin-ray pads

**C7 Raptor + fin-ray pads.** This is C5 with one swappable TPU fin-ray pad on the palm side of each phalanx, which acts as the finger's flesh.

| Outside (palm side) | Section through the pads (y = 0) |
|---|---|
| ![C7](docs/C7_raptor-finray-pads.png) | ![C7 section](docs/C7_section.png) |

- **What it does:** each pad is a small fin ray in the bending plane.
  - A 1.0 back flank sits on the phalanx and a 1.0 front flank touches the object.
  - 0.8 ribs on a 4 mm pitch join them, leaning 15° toward the tip, with chamfered ends.
  - When the object presses on the front flank, the ribs fold and the flank wraps around the object instead of meeting it at a point. That gives more contact area, as flesh does.
  - Pads are 6.0 deep and 18 wide. Lengths are 40.5 (proximal), 22 (middle) and 12.5 (distal).
  - They stop 1.5 short of each joint (3 at the MCP), so curling doesn't jam them.
- **Swapping:** the pad clips on like a phone case.
  - Two side lips (1.1 thick) run back along the phalanx sides in a recess. The recess keeps the outside flush at 18 mm.
  - The lips end in hook teeth that drop into side grooves.
  - The recess ends hold the pad along the finger.
  - To remove a pad, peel one lip out and pull. To fit one, press it on. It needs no tools, and the pins and cords stay in place.
  - Seat gaps are 0.1 all round: TPU presses into place.
- **Material:** about 4.8 cm³ of TPU for all three pads, about 6 g. Print each pad lying on its side (cells upright) so the ribs and flanks print as walls.
- **Variants to test:** rib angle (0–30°), rib pitch, flank thickness and Shore hardness (TPU 90A / 95A). Each pad is a separate print, so variants are cheap. The same clip interface can go on C3–C6 later.
- **Cost:** the finger becomes 22 mm thick (16 core + 6 pad). Thin the core later if needed.

## Recommendation

1. **C5 Raptor cord + elastic** is the best first build:
   - It has the fewest risky fits.
   - Hand pull works on day one, and the servo spool is a straight swap.
   - It gives a baseline for force and curl.
2. **C6 rod + four-bar** is the best second build:
   - It is rigid, drives both ways and its pose is repeatable.
   - It shows what the SCS0009 can do when its position control sets the finger pose.
   - Our linkage tools (`fourbar.py`, `joint.sweep`) can check its motion.

C1 is attractive but its gears are too small for FDM at this width. C2 and C3 are good second-round experiments once C5 has given numbers to compare against.

**C7 is the natural next step on C5:** build C5 with the pad interface from the start (C7), then compare the bare finger with the padded one by swapping pads.

## Checks (`python3 articulated_finger/tools/verify_concepts.py`, 57/57 PASS)

Per concept:
- No feature errors or warnings. Only the vendor STEP's tolerance note is ignored.
- The finger (middle + distal) is 18.0 wide.
- The finger is 100 long including the root wrap; C4 has no root wrap, so it is 91.
- The dovetail parameters equal GRIP-0002's.
- The SCS0009 STEP is placed, with all 4 bodies.
- **Servo vs every printed body:** the servo is lifted 0.05 off its seat for this check, so a real overlap still shows.
  - The two designed contacts read exactly 0.05: the tabs on the cradle, and the spool/crank/horn on the spline top (drawn 0.1 off).
  - Everything else is at least 0.3 away. The closest is the case in its pocket at 0.49.
- **Printed vs printed:** no overlap and no contact; the closest pair is 0.1.
  - The same kernel reading of 0 shows up between each C7 pad and its phalanx (at the recess mouth, x = palm face), so C7 adds proof that it is not real:
    - an exact boolean interference check of all printed bodies finds none;
    - the recess and groove volume removed from each phalanx (compared with C5) equals the computed 0.1-oversize seat: 415.14 / 226.44 / 129.54 mm³;
    - each pad's size is checked from its bbox.
  - Exception: in C4 the kernel reads 0 between the TPU strip and the base at the slot mouth edge. The slot's volume check shows a 0.1 gap all round (1.7 × 16.2 × 5.1 = 140.45 mm³ removed), so it is not a real contact.

Log: `verify.log`.

## Not checked

- **Motion.** No joints, no `joint.sweep`, no range of motion, and the tendon/rod geometry over the stroke is not checked. Massing is straight pose only.
- **Fit on the real baseplate.** The dovetail numbers are equal to GRIP-0002's, but the cradle overhang (+Y, up to y 40) has not been checked against the baseplate's +Y lock rail and thumb screw.
- **Forces.** The servo numbers above are hand calculations from the datasheet; they are not checked against friction or elastic return.
- **Printability.** Massing only: no orientation, overhangs, fits, fasteners or pin holes sized.
- **C7 pads:**
  - Not checked how the pads deform under load: there is no FEA and no test.
  - Not checked whether TPU lips hold under shear while grasping.
  - Not checked whether the pads hit each other or the next phalanx when the finger curls (motion not modelled).
- **Licences.** These are taken from the project pages; check them again before copying anything beyond the principle.

## Files

- `../tools/gen_concepts.py`: writes `cad/C<n>_<name>.json` (the shared base + one function per concept).
- `cad/*.sc`: built with `solidcraft-cli run cad/<x>.json --save cad/<x>.sc`.
- `../tools/verify_concepts.py`: the checks above.
- `docs/*.png`: one picture per concept, a sanity check only.
