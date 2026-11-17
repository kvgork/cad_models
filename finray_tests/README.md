# finray_tests: test rigs for fin-ray gripper fingers

Hand-driven rigs to compare fin-ray finger designs (TPU 90A, 60 mm long). Each version folder is a complete print kit: README with print list, exports, plate files, sorting sheet.

| Version | Folder | Assembly | What it tests | Status |
|---|---|---|---|---|
| v1 parallel | [`v1_parallel/`](v1_parallel/README.md) | GRIP-9010 assy-finray-gripper | Five finger designs (A, B, C, A+15, A−15) on dovetail roots, closed by a thumb screw: both jaws move straight toward each other | X1, CAD-checked, NEEDS PRINT TEST |
| v2 multi-actuation | [`v2_multi-actuation/`](v2_multi-actuation/README.md) | GRIP-9017 assy-finray-multi-actuation | One base, swappable actuation modules, fingers with an open root and two pinned corner bosses. Stage 1: finger A, **parallel** and **pull** (pull the inner root corner back, 0–6 mm). Angular and back-face pusher modules and the other rib layouts follow | X1, CAD-checked, NEEDS PRINT TEST |
| v2b C-socket | [`v2b_c-socket/`](v2b_c-socket/README.md) | GRIP-9018 assy-finray-c-socket | v2 parallel rig with C-socket holders: fingers with Ø5 corner cylinders slide in from the top (root test) | X1, CAD-checked, NEEDS PRINT TEST |

`tools/` is shared by all versions: one generator and one check script per version (`gen_finray.py` / `verify_finray.py` for v1, `gen_finray_v2.py` / `verify_finray_v2.py` / `build_guide_finray_v2.py` for v2 and v2b).

Build one version: `tools/build.sh finray_tests/v1_parallel` (or `v2_multi-actuation`, `v2b_c-socket`).
