# articulated_finger: single articulated test finger (hand-driven first, then a Feetech SCS0009)

One human-size finger (92 mm, three joints) that slides onto the gripper tester baseplates (GRIP-0001 / GRIP-0069) on the GRIP-0002 dovetail. It is driven by hand first and later by an SCS0009 micro bus servo (`base/feetech_scs0009`).

## Versions

### Printable test versions (X1, CAD-checked, NEEDS PRINT TEST)

| Version | Picture | Assembly | What | Plate | Generator / check |
|---|---|---|---|---|---|
| [v1_raptor-cord](v1_raptor-cord/README.md) | <img src="v1_raptor-cord/docs/build/step6_done_front.png" width="180" alt="v1"> | GRIP-9020 assy-finger-raptor-cord | C5 made printable: 3 pin joints with stop spurs (−2 … 93° per joint, MCP to 114°), palm cord to a pull ring, elastic on the back. The servo slides in later and drives a spool on its spline. 9 prints. | `plate1-petg` ~35 g, ~108 min | `tools/gen_v1.py` / `tools/verify_v1.py` (14/14) |
| [v2_rod-fourbar](v2_rod-fourbar/README.md) | <img src="v2_rod-fourbar/docs/build/step11_curled.png" width="180" alt="v2"> | GRIP-9021 assy-finger-rod-fourbar | C6 made printable: one DOF, coupled. Horn → push rod → MCP lever; crossed links make PIP and DIP follow (horn 0 → 96° gives MCP 80°, PIP 90°, DIP 70°). Hand first: a printed dummy servo carries the horn, which has a hand lever. 18 prints. | `plate1-petg` ~42 g, ~126 min | `tools/fingerlinks.py` + `tools/gen_v2.py` / `tools/verify_v2.py` (12/12) |

### Concepts

All seven are **concepts** (massing models, no part numbers, no print kit yet); details, pros/risks and checks in [`concepts/README.md`](concepts/README.md) (57/57 CAD checks).

| Concept | Picture | Based on | How it moves | Model |
|---|---|---|---|---|
| **C1 Geared coupled** | <img src="concepts/docs/C1_geared-coupled.png" width="180" alt="C1"> | new | Servo spline is the MCP; idler-gear chains turn PIP and DIP by the same angle (fixed 1:1:1 curl, driven both ways). Gears m0.5 z17: too small for FDM at 18 mm width. | [`C1_geared-coupled.json`](concepts/cad/C1_geared-coupled.json) |
| **C2 Push-pull spine** | <img src="concepts/docs/C2_push-pull-spine.png" width="180" alt="C2"> | new | Flexible band in a palm-side channel; servo crank pulls to curl, pushes to extend. Underactuated, no spring. | [`C2_push-pull-spine.json`](concepts/cad/C2_push-pull-spine.json) |
| **C3 Rolling contact** | <img src="concepts/docs/C3_rolling-contact.png" width="180" alt="C3"> | new | Pinless rolling joints held by crossed straps; palm tendon to a spool, elastic dorsal straps return it. | [`C3_rolling-contact.json`](concepts/cad/C3_rolling-contact.json) |
| **C4 OpenHand flexure** | <img src="concepts/docs/C4_openhand-flexure.png" width="180" alt="C4"> | Yale OpenHand T42/M2 | Rigid PETG segments on one TPU flexure strip; one tendon to a spool, flexure springs it open. Fewest parts. | [`C4_openhand-flexure.json`](concepts/cad/C4_openhand-flexure.json) |
| **C5 Raptor cord + elastic** | <img src="concepts/docs/C5_raptor-cord-elastic.png" width="180" alt="C5"> | e-NABLE Raptor Reloaded | Pin joints, Dyneema cord palm side to a spool, elastic cord on the back. **Recommended first build.** | [`C5_raptor-cord-elastic.json`](concepts/cad/C5_raptor-cord-elastic.json) |
| **C6 Amazing rod + four-bar** | <img src="concepts/docs/C6_amazing-rod-fourbar.png" width="180" alt="C6"> | Pollen Amazing Hand + BiDexHand | Servo horn → push rod → MCP lever; four-bar couplers make PIP and DIP follow. Rigid, both ways. **Recommended second build.** | [`C6_amazing-rod-fourbar.json`](concepts/cad/C6_amazing-rod-fourbar.json) |
| **C7 Raptor + fin-ray pads** | <img src="concepts/docs/C7_raptor-finray-pads.png" width="180" alt="C7"> | C5 + finray_tests | C5 with a swappable clip-on TPU fin-ray pad on each phalanx (finger flesh). | [`C7_raptor-finray-pads.json`](concepts/cad/C7_raptor-finray-pads.json) |

C5 and C6 were picked (2026-11-22) and are now the printable versions above; the other concepts stay as massing models.
