# Part-number register

Scheme: `<PROJ>-<NNNN>`. Parts take 0001–8999 and assemblies 9000–9999. A number is never reused or renumbered. Change that breaks fit or function with the old part → new number. Change that keeps fit → next revision.

Codes: `SO101` (SO-101 arm accessories), `JTNK` (JeTank), `GRIP` (gripper R&D), `LIB` (vendor/library parts, read-only).

Names: every part also has a short lower-case **name** (`a-z 0-9 -`). File and component names are `<PN>_<name>`, for example `GRIP-0015_link-j-hub.json`; exports are `<PN>_<name>_<REV>.<ext>`. This table is the single source of truth: the generators read the Name column.

Revisions: unreleased print iterations are `X1`, `X2`, … (X2 of GRIP-0013…0018, 0023, 0024, 0029…0032, 0034 = X1 + debossed label, used in v5; earlier versions keep X1) (property `revision`, export name, embossed where room). Release = letter `A`, `B`, … (skip I O Q S X Z) + git tag `<PN>/<REV>`.

| PN | Name | Rev | Description | Folder | Material / process |
|---|---|---|---|---|---|
| GRIP-0001 | baseplate | X1 | BASEPLATE, GRIPPER TESTER | gripper_tester | PLA/PETG, FDM |
| GRIP-0002 | gripper-adapter | X1 | ADAPTER, GRIPPER, DOVETAIL | gripper_tester, gripper_tester/v2_fe-urt2 | PETG, FDM |
| GRIP-0003 | frame | X1 | FRAME, FINGER, STRANDBEEST | strandbeest_gripper/v1_single-finger | PETG/ASA, FDM |
| GRIP-0004 | crank | X1 | CRANK, FINGER, STRANDBEEST | strandbeest_gripper/v1_single-finger | PETG, FDM |
| GRIP-0005 | link-j | X1 | LINK, J, STRANDBEEST | strandbeest_gripper/v1_single-finger | PETG, FDM |
| GRIP-0006 | link-k | X1 | LINK, K, STRANDBEEST | strandbeest_gripper/v1_single-finger | PETG, FDM |
| GRIP-0007 | link-c | X1 | LINK, C, STRANDBEEST | strandbeest_gripper/v1_single-finger | PETG, FDM |
| GRIP-0008 | link-f | X1 | LINK, F, STRANDBEEST | strandbeest_gripper/v1_single-finger | PETG, FDM |
| GRIP-0009 | triangle-bde | X1 | TRIANGLE, BDE, STRANDBEEST | strandbeest_gripper/v1_single-finger | PETG, FDM |
| GRIP-0010 | triangle-ghi-fingertip | X1 | TRIANGLE, GHI, FINGERTIP, STRANDBEEST | strandbeest_gripper/v1_single-finger | PETG, FDM |
| GRIP-0011 | frame-dual | X1 | FRAME, DUAL FINGER, STRANDBEEST | strandbeest_gripper/v2_dual-finger | PETG/ASA, FDM |
| GRIP-0012 | gear-crank-servo | X1 | GEAR, CRANK, SERVO SIDE, Z20 M1 | strandbeest_gripper/v2_dual-finger | PETG, FDM |
| GRIP-0013 | gear-crank-idle | X2 | GEAR, CRANK, IDLE SIDE, Z20 M1 | strandbeest_gripper/v2_dual-finger | PETG, FDM |
| GRIP-0014 | gear-idler-z33 | X2 | GEAR, IDLER, Z33 M1 (qty 2) | strandbeest_gripper/v2_dual-finger, strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0015 | link-j-hub | X2 | LINK, J, HUB, STRANDBEEST V2 (qty 2) | strandbeest_gripper/v2_dual-finger | PETG, FDM |
| GRIP-0016 | link-k | X2 | LINK, K, STRANDBEEST V2 (qty 2) | strandbeest_gripper/v2_dual-finger | PETG, FDM |
| GRIP-0017 | link-c | X2 | LINK, C, STRANDBEEST V2 (qty 2) | strandbeest_gripper/v2_dual-finger | PETG, FDM |
| GRIP-0018 | link-f-hub | X2 | LINK, F, HUB, STRANDBEEST V2 (qty 2) | strandbeest_gripper/v2_dual-finger | PETG, FDM |
| GRIP-0019 | triangle-bde-finger1 | X1 | TRIANGLE, BDE, FINGER 1, STRANDBEEST V2 | strandbeest_gripper/v2_dual-finger | PETG, FDM |
| GRIP-0020 | triangle-ghi-pad-finger1 | X1 | TRIANGLE, GHI, PAD, FINGER 1, STRANDBEEST V2 | strandbeest_gripper/v2_dual-finger | PETG, FDM |
| GRIP-0021 | triangle-bde-finger2 | X1 | TRIANGLE, BDE, FINGER 2 (MIRROR), STRANDBEEST V2 | strandbeest_gripper/v2_dual-finger | PETG, FDM |
| GRIP-0022 | triangle-ghi-pad-finger2 | X1 | TRIANGLE, GHI, PAD, FINGER 2 (MIRROR), STRANDBEEST V2 | strandbeest_gripper/v2_dual-finger | PETG, FDM |
| GRIP-0023 | triangle-ghi-hub-finger1 | X2 | TRIANGLE, GHI, F HUB, FINGER 1, STRANDBEEST V3 (v3a/v3b; qty 1 in v3a, 2 in v3b) | strandbeest_gripper/v3a_pivot-jaws, v3b_twin-legs | PETG, FDM |
| GRIP-0024 | triangle-ghi-hub-finger2 | X2 | TRIANGLE, GHI, F HUB, FINGER 2 (MIRROR), STRANDBEEST V3 | strandbeest_gripper/v3a_pivot-jaws, v3b_twin-legs | PETG, FDM |
| GRIP-0025 | jaw-pivot | X1 | JAW, PIVOT, 25 MM, STRANDBEEST V3A (qty 2) | strandbeest_gripper/v3a_pivot-jaws | PETG, FDM |
| GRIP-0026 | triangle-ghi-nose-finger1 | X1 | TRIANGLE, GHI, PAD + NOSE, FINGER 1, STRANDBEEST V3C | strandbeest_gripper/v3c_rigid-nose | PETG, FDM |
| GRIP-0027 | triangle-ghi-nose-finger2 | X1 | TRIANGLE, GHI, PAD + NOSE, FINGER 2 (MIRROR), STRANDBEEST V3C | strandbeest_gripper/v3c_rigid-nose | PETG, FDM |
| GRIP-0028 | frame-twin | X1 | FRAME, TWIN LEG, STRANDBEEST V3B | strandbeest_gripper/v3b_twin-legs | PETG/ASA, FDM |
| GRIP-0029 | gear-crank-twin-finger1 | X2 | GEAR, CRANK, TWIN LEG, FINGER 1, Z20 M1 | strandbeest_gripper/v3b_twin-legs | PETG, FDM |
| GRIP-0030 | gear-idler-z60 | X2 | GEAR, IDLER, Z60 M1 (qty 2) | strandbeest_gripper/v3b_twin-legs | PETG, FDM |
| GRIP-0031 | jaw-twin | X2 | JAW, TWIN LEG, 91 MM, STRANDBEEST V3B (qty 2) | strandbeest_gripper/v3b_twin-legs | PETG, FDM |
| GRIP-0032 | gear-crank-twin-finger2 | X2 | GEAR, CRANK, TWIN LEG, FINGER 2, Z20 M1 | strandbeest_gripper/v3b_twin-legs | PETG, FDM |
| GRIP-0033 | frame-hand | X1 | FRAME, DUAL FINGER, HAND DRIVE, STRANDBEEST V4 | strandbeest_gripper/v4_thumb-wheel | PETG, FDM |
| GRIP-0034 | gear-crank-axle | X2 | GEAR, CRANK, ON AXLE, Z20 M1 (replaces the horn-mounted GRIP-0012) | strandbeest_gripper/v4_thumb-wheel | PETG, FDM |
| GRIP-0035 | thumb-wheel | X1 | WHEEL, THUMB, KNURLED D50, GEAR Z40 M1 | strandbeest_gripper/v4_thumb-wheel | PETG, FDM |
| GRIP-0036 | pin-j3 | X1 | PIN, PRINTED, D3, SHANK 8.5, J3 | strandbeest_gripper/v4a_printed-pins | PETG, FDM |
| GRIP-0037 | pin-j4 | X1 | PIN, PRINTED, D3, SHANK 15.5, J4 | strandbeest_gripper/v4a_printed-pins | PETG, FDM |
| GRIP-0038 | pin-j2-j5 | X1 | PIN, PRINTED, D3, SHANK 19, J2 + J5 | strandbeest_gripper/v4a_printed-pins | PETG, FDM |
| GRIP-0039 | pin-crank-axle | X1 | PIN, PRINTED, D3, SHANK 21.5, CRANK AXLE | strandbeest_gripper/v4a_printed-pins | PETG, FDM |
| GRIP-0040 | pin-gear-axle | X1 | PIN, PRINTED, D3, SHANK 23.5, IDLER + WHEEL AXLE | strandbeest_gripper/v4a_printed-pins | PETG, FDM |
| GRIP-0041 | pin-jaw | X1 | PIN, PRINTED, D3, SHANK 25, JAW PIVOT | strandbeest_gripper/v4a_printed-pins | PETG, FDM |
| GRIP-0042 | pin-g | X1 | PIN, PRINTED, D3, SHANK 38, G | strandbeest_gripper/v4a_printed-pins | PETG, FDM |
| GRIP-0043 | pin-j1-shoulder | X1 | PIN, PRINTED, SHOULDER D4 X 24.5, PRESS TIP, J1 | strandbeest_gripper/v4a_printed-pins | PETG, FDM |
| GRIP-0044 | cap-pin | X1 | CAP, PRESS-ON, FOR D3 PRINTED PIN | strandbeest_gripper/v4a_printed-pins | PETG, FDM |
| GRIP-0045 | snap-pin-j3 | X1 | PIN, SNAP, PRINTED, D3, SHANK 6.7, J3 | strandbeest_gripper/v4b_snap-pins | PETG, FDM |
| GRIP-0046 | snap-pin-j4 | X1 | PIN, SNAP, PRINTED, D3, SHANK 13.7, J4 | strandbeest_gripper/v4b_snap-pins | PETG, FDM |
| GRIP-0047 | snap-pin-j2-j5 | X1 | PIN, SNAP, PRINTED, D3, SHANK 17.2, J2 + J5 | strandbeest_gripper/v4b_snap-pins | PETG, FDM |
| GRIP-0048 | snap-pin-crank-axle | X1 | PIN, SNAP, PRINTED, D3, SHANK 19.7, CRANK AXLE | strandbeest_gripper/v4b_snap-pins | PETG, FDM |
| GRIP-0049 | snap-pin-gear-axle | X1 | PIN, SNAP, PRINTED, D3, SHANK 21.4, IDLER + WHEEL AXLE | strandbeest_gripper/v4b_snap-pins | PETG, FDM |
| GRIP-0050 | snap-pin-jaw | X1 | PIN, SNAP, PRINTED, D3, SHANK 23.2, JAW PIVOT | strandbeest_gripper/v4b_snap-pins | PETG, FDM |
| GRIP-0051 | snap-pin-g | X1 | PIN, SNAP, PRINTED, D3, SHANK 35.9, G | strandbeest_gripper/v4b_snap-pins | PETG, FDM |
| GRIP-0052 | base-plate | X1 | BASE, FINRAY GRIPPER, RAIL + SCREW WALL + PINION POST | finray_tests/v1_parallel | PETG, FDM |
| GRIP-0053 | carriage-a | X1 | CARRIAGE, JAW A, NUT TRAP + RACK, FINRAY GRIPPER | finray_tests/v1_parallel | PETG, FDM |
| GRIP-0054 | carriage-b | X1 | CARRIAGE, JAW B, RACK + ARM, FINRAY GRIPPER | finray_tests/v1_parallel | PETG, FDM |
| GRIP-0055 | pinion-z18 | X1 | GEAR, PINION, Z18 M1, FINRAY GRIPPER | finray_tests/v1_parallel | PETG, FDM |
| GRIP-0056 | knob | X1 | KNOB, THUMB, D32, M6 HEX HEAD | finray_tests/v1_parallel | PETG, FDM |
| GRIP-0057 | finray-a-baseline | X1 | FINGER, FIN RAY, A BASELINE, 6 RIBS 0 DEG | finray_tests/v1_parallel | TPU 90A, FDM |
| GRIP-0058 | finray-b-wrap | X1 | FINGER, FIN RAY, B WRAP, 5 RIBS +15 DEG THIN | finray_tests/v1_parallel | TPU 90A, FDM |
| GRIP-0059 | finray-c-stiff | X1 | FINGER, FIN RAY, C STIFF, 7 RIBS -15 DEG THICK | finray_tests/v1_parallel | TPU 90A, FDM |
| GRIP-0060 | frame-twin-hand | X1 | FRAME, TWIN LEG, HAND DRIVE, STRANDBEEST V5 | strandbeest_gripper/v5_parallel-jaws | PETG, FDM |
| GRIP-0061 | snap-pin-idler-z60 | X1 | PIN, SNAP, PRINTED, D3, SHANK 20.2, Z60 IDLER AXLE | strandbeest_gripper/v5_parallel-jaws | PETG, FDM |
| GRIP-0062 | frame-mirror-legs | X1 | FRAME, MIRRORED TWIN LEGS, HAND DRIVE, STRANDBEEST V6 | strandbeest_gripper/v6_mirror-legs | PETG, FDM |
| GRIP-0063 | gear-crank-mirror-finger1 | X1 | GEAR, CRANK, MIRRORED LEG B, FINGER 1, Z20 M1 | strandbeest_gripper/v6_mirror-legs | PETG, FDM |
| GRIP-0064 | gear-crank-mirror-finger2 | X1 | GEAR, CRANK, MIRRORED LEG B, FINGER 2, Z20 M1 | strandbeest_gripper/v6_mirror-legs | PETG, FDM |
| GRIP-0065 | gear-idler-leg-b | X1 | GEAR, IDLER, LEG B DRIVE, 4.3 THICK, M1 | strandbeest_gripper/v6_mirror-legs, strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0066 | jaw-long-slot | X1 | JAW, LONG SLOT, MIRRORED TWIN LEGS, STRANDBEEST V6 | strandbeest_gripper/v6_mirror-legs, strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0067 | finray-a-plus15 | X1 | FINGER, FIN RAY, A ANGLE-ONLY, 6 RIBS +15 DEG | finray_tests/v1_parallel | TPU 90A, FDM |
| GRIP-0068 | finray-a-minus15 | X1 | FINGER, FIN RAY, A ANGLE-ONLY, 6 RIBS -15 DEG | finray_tests/v1_parallel | TPU 90A, FDM |
| GRIP-0069 | baseplate-fe-urt2 | X1 | BASEPLATE, GRIPPER TESTER, FE-URT-2 | gripper_tester/v2_fe-urt2 | PETG, FDM |
| GRIP-0070 | frame-sandwich | X2 | FRAME, SANDWICH, 8 PILLARS, HAND DRIVE, STRANDBEEST V7 | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0071 | top-plate | X1 | PLATE, TOP, CRANK ARM + G + HUB BEARINGS, STRANDBEEST V7 | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0072 | arm-crank-top | X1 | ARM, CRANK, TOP, J1 PRESS HOLE, STRANDBEEST V7 | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0073 | knob-thumb-hex | X1 | KNOB, THUMB, KNURLED D50, HEX SOCKET, STRANDBEEST V7 | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0074 | gear-wheel-hub | X1 | GEAR, THUMB WHEEL, Z40 M1, HUB + HEX KEY THROUGH TOP PLATE | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0075 | pin-j1-shoulder-double-press | X1 | PIN, PRINTED, SHOULDER D4, PRESS TIPS BOTH ENDS, 2 FLATS, J1 | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0076 | gear-crank-a1-sandwich | X1 | GEAR, CRANK, A1, Z20 M1, SHORT J1 HUB, STRANDBEEST V7 | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0077 | gear-crank-a2-sandwich | X1 | GEAR, CRANK, A2, Z20 M1, SHORT J1 HUB, STRANDBEEST V7 | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0078 | gear-crank-b1-sandwich | X1 | GEAR, CRANK, B1, MIRRORED LEG B, Z20 M1, SHORT J1 HUB, STRANDBEEST V7 | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0079 | gear-crank-b2-sandwich | X1 | GEAR, CRANK, B2, MIRRORED LEG B, Z20 M1, SHORT J1 HUB, STRANDBEEST V7 | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0080 | link-j-v7 | X1 | LINK, J, HUB, STRANDBEEST V7 | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0081 | link-k-v7 | X1 | LINK, K, STRANDBEEST V7 | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0082 | link-c-v7 | X1 | LINK, C, STRANDBEEST V7 | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0083 | link-f-hub-v7 | X1 | LINK, F, HUB, STRANDBEEST V7 | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0084 | triangle-bde-finger1-v7 | X1 | TRIANGLE, BDE, FINGER 1, STRANDBEEST V7 | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0085 | triangle-bde-finger2-v7 | X1 | TRIANGLE, BDE, FINGER 2 (MIRROR), STRANDBEEST V7 | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0086 | triangle-ghi-hub-finger1-v7 | X1 | TRIANGLE, GHI, F HUB, FINGER 1, STRANDBEEST V7 | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0087 | triangle-ghi-hub-finger2-v7 | X1 | TRIANGLE, GHI, F HUB, FINGER 2 (MIRROR), STRANDBEEST V7 | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0088 | snap-pin-2f-crank-axle | X1 | PIN, SNAP, PRINTED, D3, 2 FLATS, SHANK 6.0, CRANK AXLE | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0089 | snap-pin-2f-idler-z20 | X1 | PIN, SNAP, PRINTED, D3, 2 FLATS, SHANK 6.5, Z20 IDLER AXLE | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0090 | snap-pin-2f-j2-j3 | X1 | PIN, SNAP, PRINTED, D3, 2 FLATS, SHANK 6.7, J2 + J3 | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0091 | snap-pin-2f-z33-arm | X1 | PIN, SNAP, PRINTED, D3, 2 FLATS, SHANK 7.7, Z33 IDLER + CRANK ARM | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0092 | snap-pin-2f-j4 | X1 | PIN, SNAP, PRINTED, D3, 2 FLATS, SHANK 10.2, J4 | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0093 | snap-pin-2f-g-top | X1 | PIN, SNAP, PRINTED, D3, 2 FLATS, SHANK 11.2, G UPPER (C) | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0094 | snap-pin-2f-j5-g-low | X1 | PIN, SNAP, PRINTED, D3, 2 FLATS, SHANK 13.7, J5 + G LOWER (BDE) | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0095 | snap-pin-2f-jaw | X1 | PIN, SNAP, PRINTED, D3, 2 FLATS, SHANK 15.2, JAW | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0096 | snap-pin-2f-pillar | X1 | PIN, SNAP, PRINTED, D3, 2 FLATS, SHANK 39.2, PILLAR + TOP PLATE | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0097 | snap-pin-2f-wheel | X1 | PIN, SNAP, PRINTED, D3, 2 FLATS, SHANK 47.7, THUMB WHEEL AXLE | strandbeest_gripper/v7_sandwich | PETG, FDM |
| GRIP-0107 | frame-four-bar | X1 | FRAME, FOUR-BAR, 4 Q COLUMNS, STRANDBEEST V8 | strandbeest_gripper/v8_four-bar | PETG, FDM |
| GRIP-0108 | top-plate-four-bar | X1 | PLATE, TOP, CRANK + ROCKER BEARINGS, SLOT WINDOW, STRANDBEEST V8 | strandbeest_gripper/v8_four-bar | PETG, FDM |
| GRIP-0109 | knob-double-d | X1 | KNOB, THUMB, KNURLED D40, DOUBLE-D BORE, STRANDBEEST V8 | strandbeest_gripper/v8_four-bar | PETG, FDM |
| GRIP-0110 | gear-crank-a1-eccentric | X1 | GEAR, CRANK, A1, Z46 M1, ECCENTRIC BOSS, STRANDBEEST V8 | strandbeest_gripper/v8_four-bar | PETG, FDM |
| GRIP-0111 | gear-crank-b1-eccentric | X1 | GEAR, CRANK, B1, Z46 M1, ECCENTRIC BOSS, STRANDBEEST V8 | strandbeest_gripper/v8_four-bar | PETG, FDM |
| GRIP-0112 | gear-crank-a2-eccentric | X1 | GEAR, CRANK, A2, Z46 M1, ECCENTRIC BOSS, STRANDBEEST V8 | strandbeest_gripper/v8_four-bar | PETG, FDM |
| GRIP-0113 | gear-crank-b2-eccentric | X1 | GEAR, CRANK, B2, Z46 M1, ECCENTRIC BOSS, STRANDBEEST V8 | strandbeest_gripper/v8_four-bar | PETG, FDM |
| GRIP-0114 | gear-idler-z24 | X1 | GEAR, IDLER, Z24 M1, FINGER SYNC | strandbeest_gripper/v8_four-bar | PETG, FDM |
| GRIP-0115 | coupler-eccentric | X1 | COUPLER, ECCENTRIC RING, FOUR-BAR (FINGER 2 FLIPPED) | strandbeest_gripper/v8_four-bar | PETG, FDM |
| GRIP-0116 | rocker-q-b | X1 | ROCKER, Q-B, FOUR-BAR | strandbeest_gripper/v8_four-bar | PETG, FDM |
| GRIP-0117 | jaw-four-bar | X1 | JAW, PARALLEL, HOLE + SHORT SLOT, STRANDBEEST V8 | strandbeest_gripper/v8_four-bar | PETG, FDM |
| GRIP-0118 | shaft-crank-double-d | X1 | SHAFT, CRANK, D5, DOUBLE-D, SNAP, STRANDBEEST V8 | strandbeest_gripper/v8_four-bar | PETG, FDM |
| GRIP-0119 | shaft-crank-knob | X1 | SHAFT, CRANK, D5, DOUBLE-D, SNAP, KNOB LENGTH, STRANDBEEST V8 | strandbeest_gripper/v8_four-bar | PETG, FDM |
| GRIP-0120 | snap-pin-2f-q-column | X1 | PIN, SNAP, PRINTED, D3, 2 FLATS, Q COLUMN + TOP PLATE | strandbeest_gripper/v8_four-bar | PETG, FDM |
| GRIP-0121 | pin-press-head-b | X1 | PIN, PRESS, HEADED, D3, 2 FLATS, B (COUPLER-ROCKER) | strandbeest_gripper/v8_four-bar | PETG, FDM |
| GRIP-0122 | pin-press-head-p | X1 | PIN, PRESS, HEADED, D3, 2 FLATS, P (COUPLER-JAW) | strandbeest_gripper/v8_four-bar | PETG, FDM |
| GRIP-0123 | snap-pin-2f-idler-down | X1 | PIN, SNAP, PRINTED, D3, 2 FLATS, Z24 IDLER, HEAD IN GEAR | strandbeest_gripper/v8_four-bar | PETG, FDM |
| GRIP-9001 | assy-tester-fit-check | X1 | ASSY, GRIPPER TESTER, FIT CHECK | gripper_tester | — |
| GRIP-9002 | assy-single-finger | X1 | ASSY, FINGER, STRANDBEEST (v1: single finger + anvil) | strandbeest_gripper/v1_single-finger | — |
| GRIP-9003 | assy-dual-finger | X1 | ASSY, GRIPPER, DUAL FINGER, STRANDBEEST V2 (feeder) | strandbeest_gripper/v2_dual-finger | — |
| GRIP-9004 | assy-pivot-jaws | X1 | ASSY, GRIPPER, DUAL FINGER, PIVOT JAWS, STRANDBEEST V3A | strandbeest_gripper/v3a_pivot-jaws | — |
| GRIP-9005 | assy-twin-legs | X1 | ASSY, GRIPPER, DUAL FINGER, TWIN LEG PARALLEL JAWS, STRANDBEEST V3B | strandbeest_gripper/v3b_twin-legs | — |
| GRIP-9007 | assy-thumb-wheel | X1 | ASSY, GRIPPER, DUAL FINGER, PIVOT JAWS, THUMB WHEEL, STRANDBEEST V4 | strandbeest_gripper/v4_thumb-wheel | — |
| GRIP-9006 | assy-rigid-nose | X1 | ASSY, GRIPPER, DUAL FINGER, RIGID NOSE, STRANDBEEST V3C | strandbeest_gripper/v3c_rigid-nose | — |
| GRIP-9008 | assy-printed-pins | X1 | ASSY, GRIPPER, THUMB WHEEL, PRINTED PINS, STRANDBEEST V4A | strandbeest_gripper/v4a_printed-pins | — |
| GRIP-9009 | assy-snap-pins | X1 | ASSY, GRIPPER, THUMB WHEEL, SNAP PINS, STRANDBEEST V4B | strandbeest_gripper/v4b_snap-pins | — |
| GRIP-9010 | assy-finray-gripper | X1 | ASSY, GRIPPER, THUMB SCREW, SLIDE-IN FIN RAY FINGERS | finray_tests/v1_parallel | — |
| GRIP-9011 | assy-parallel-jaws | X1 | ASSY, GRIPPER, TWIN LEG PARALLEL JAWS, THUMB WHEEL, SNAP PINS, STRANDBEEST V5 | strandbeest_gripper/v5_parallel-jaws | — |
| GRIP-9012 | assy-mirror-legs | X1 | ASSY, GRIPPER, MIRRORED TWIN LEGS, LONG PARALLEL JAWS, STRANDBEEST V6 | strandbeest_gripper/v6_mirror-legs | — |
| GRIP-9013 | assy-tester-fe-urt2-fit-check | X1 | ASSY, GRIPPER TESTER, FE-URT-2, FIT CHECK | gripper_tester/v2_fe-urt2 | — |
| GRIP-9014 | assy-sandwich | X1 | ASSY, GRIPPER, SANDWICH FRAME, MIRRORED TWIN LEGS, STRANDBEEST V7 | strandbeest_gripper/v7_sandwich | — |
| GRIP-9016 | assy-four-bar | X1 | ASSY, GRIPPER, FOUR-BAR LEGS, ECCENTRIC CRANKS, STRANDBEEST V8 | strandbeest_gripper/v8_four-bar | — |
| SO101-0001 | tip-moving-jaw | X1 | TIP, JAW, MOVING, CALIBRATION | gripper_tips/v1_full-cap | red PLA/PETG, FDM |
| SO101-0002 | tip-fixed-jaw | X1 | TIP, JAW, FIXED, CALIBRATION | gripper_tips/v1_full-cap | red PLA/PETG, FDM |
| SO101-0003 | tip-moving-jaw-open | X1 | TIP, JAW, MOVING, CALIBRATION, OPEN GRIP FACE | gripper_tips/v2_open-inside | red PLA/PETG, FDM |
| SO101-0004 | tip-fixed-jaw-open | X1 | TIP, JAW, FIXED, CALIBRATION, OPEN GRIP FACE | gripper_tips/v2_open-inside | red PLA/PETG, FDM |
| JTNK-0001 | lidar-holder | X1 | HOLDER, LIDAR, RPLIDAR C1 | lidar_holder | PETG, FDM |
| JTNK-9001 | assy-lidar-fit-check | X1 | ASSY, LIDAR HOLDER, FIT CHECK | lidar_holder | — |
| LIB-0001 | so101-base | — | BASE, SO-101 (vendor STEP) | lib/so101 | purchased/vendor |
| LIB-0002 | so101-handle | — | HANDLE, SO-101 LEADER (vendor STEP) | lib/so101 | purchased/vendor |
| LIB-0003 | so101-moving-jaw | — | JAW, MOVING, SO-101 (vendor STEP) | lib/so101 | purchased/vendor |
| LIB-0004 | so101-waveshare-plate | — | PLATE, MOUNTING, WAVESHARE, SO-101 (vendor STEP) | lib/so101 | purchased/vendor |
| LIB-0005 | so101-wrist-roll-follower | — | WRIST ROLL, FOLLOWER GRIPPER, SO-101 (vendor STEP) | lib/so101 | purchased/vendor |
| LIB-0006 | so101-wrist-roll-pitch | — | WRIST ROLL PITCH, SO-101 (vendor STEP) | lib/so101 | purchased/vendor |
| LIB-0007 | so101-wrist-roll | — | WRIST ROLL, SO-101 (vendor STEP) | lib/so101 | purchased/vendor |
| LIB-0008 | rplidar-c1 | — | LIDAR, RPLIDAR C1 (vendor STEP) | lib/rplidar_c1 | purchased |
| LIB-0009 | servo-sts3215 | — | SERVO, STS3215 (vendor STEP) | lib/sts3215, base/feetech_sts3215 (identical copy) | purchased |
| LIB-0010 | servo-scs0009 | — | SERVO, SCS0009, MICRO SERIAL BUS (vendor STEP) | base/feetech_scs0009 | purchased |

Next free: GRIP-0124, GRIP-9017, SO101-0005, JTNK-0002, JTNK-9002, LIB-0011.
