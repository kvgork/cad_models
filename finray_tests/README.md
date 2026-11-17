# finray_tests: test rigs for fin-ray gripper fingers

Hand-driven rigs to compare fin-ray finger designs (TPU 90A, 60 mm long). Each version folder is a complete print kit: README with print list, exports, plate files, sorting sheet.

| Version | Folder | Assembly | What it tests | Status |
|---|---|---|---|---|
| v1 parallel | [`v1_parallel/`](v1_parallel/README.md) | GRIP-9010 assy-finray-gripper | Five finger designs (A, B, C, A+15, A−15) on dovetail roots, closed by a thumb screw: both jaws move straight toward each other | X1, CAD-checked, NEEDS PRINT TEST |

`tools/` is shared by all versions: one generator and one check script per version: `gen_finray.py` / `verify_finray.py` for v1.

Build one version: `tools/build.sh finray_tests/v1_parallel`.
