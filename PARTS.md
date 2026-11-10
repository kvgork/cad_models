# Part-number register

Scheme: `<PROJ>-<NNNN>`. Parts take 0001–8999 and assemblies 9000–9999. A number is never reused or renumbered. Change that breaks fit or function with the old part → new number. Change that keeps fit → next revision.

Codes: `SO101` (SO-101 arm accessories), `JTNK` (JeTank), `GRIP` (gripper R&D), `LIB` (vendor/library parts, read-only).

Names: every part also has a short lower-case **name** (`a-z 0-9 -`). File and component names are `<PN>_<name>`, for example `GRIP-0015_link-j-hub.json`; exports are `<PN>_<name>_<REV>.<ext>`. This table is the single source of truth: the generators read the Name column.

Revisions: unreleased print iterations are `X1`, `X2`, … (X2 of GRIP-0013…0018, 0023, 0024, 0029…0032, 0034 = X1 + debossed label, used in v5; earlier versions keep X1) (property `revision`, export name, embossed where room). Release = letter `A`, `B`, … (skip I O Q S X Z) + git tag `<PN>/<REV>`.

| PN | Name | Rev | Description | Folder | Material / process |
|---|---|---|---|---|---|
| GRIP-0001 | baseplate | X1 | BASEPLATE, GRIPPER TESTER | gripper_tester | PLA/PETG, FDM |
| GRIP-0002 | gripper-adapter | X1 | ADAPTER, GRIPPER, DOVETAIL | gripper_tester | PETG, FDM |
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
| GRIP-0014 | gear-idler-z33 | X2 | GEAR, IDLER, Z33 M1 (qty 2) | strandbeest_gripper/v2_dual-finger | PETG, FDM |
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
| GRIP-0052 | base-plate | X1 | BASE, FINRAY GRIPPER, RAIL + SCREW WALL + PINION POST | finray_tests | PETG, FDM |
| GRIP-0053 | carriage-a | X1 | CARRIAGE, JAW A, NUT TRAP + RACK, FINRAY GRIPPER | finray_tests | PETG, FDM |
| GRIP-0054 | carriage-b | X1 | CARRIAGE, JAW B, RACK + ARM, FINRAY GRIPPER | finray_tests | PETG, FDM |
| GRIP-0055 | pinion-z18 | X1 | GEAR, PINION, Z18 M1, FINRAY GRIPPER | finray_tests | PETG, FDM |
| GRIP-0056 | knob | X1 | KNOB, THUMB, D32, M6 HEX HEAD | finray_tests | PETG, FDM |
| GRIP-0057 | finray-a-baseline | X1 | FINGER, FIN RAY, A BASELINE, 6 RIBS 0 DEG | finray_tests | TPU 90A, FDM |
| GRIP-0058 | finray-b-wrap | X1 | FINGER, FIN RAY, B WRAP, 5 RIBS +15 DEG THIN | finray_tests | TPU 90A, FDM |
| GRIP-0059 | finray-c-stiff | X1 | FINGER, FIN RAY, C STIFF, 7 RIBS -15 DEG THICK | finray_tests | TPU 90A, FDM |
| GRIP-0060 | frame-twin-hand | X1 | FRAME, TWIN LEG, HAND DRIVE, STRANDBEEST V5 | strandbeest_gripper/v5_parallel-jaws | PETG, FDM |
| GRIP-0061 | snap-pin-idler-z60 | X1 | PIN, SNAP, PRINTED, D3, SHANK 20.2, Z60 IDLER AXLE | strandbeest_gripper/v5_parallel-jaws | PETG, FDM |
| GRIP-9001 | assy-tester-fit-check | X1 | ASSY, GRIPPER TESTER, FIT CHECK | gripper_tester | — |
| GRIP-9002 | assy-single-finger | X1 | ASSY, FINGER, STRANDBEEST (v1: single finger + anvil) | strandbeest_gripper/v1_single-finger | — |
| GRIP-9003 | assy-dual-finger | X1 | ASSY, GRIPPER, DUAL FINGER, STRANDBEEST V2 (feeder) | strandbeest_gripper/v2_dual-finger | — |
| GRIP-9004 | assy-pivot-jaws | X1 | ASSY, GRIPPER, DUAL FINGER, PIVOT JAWS, STRANDBEEST V3A | strandbeest_gripper/v3a_pivot-jaws | — |
| GRIP-9005 | assy-twin-legs | X1 | ASSY, GRIPPER, DUAL FINGER, TWIN LEG PARALLEL JAWS, STRANDBEEST V3B | strandbeest_gripper/v3b_twin-legs | — |
| GRIP-9007 | assy-thumb-wheel | X1 | ASSY, GRIPPER, DUAL FINGER, PIVOT JAWS, THUMB WHEEL, STRANDBEEST V4 | strandbeest_gripper/v4_thumb-wheel | — |
| GRIP-9006 | assy-rigid-nose | X1 | ASSY, GRIPPER, DUAL FINGER, RIGID NOSE, STRANDBEEST V3C | strandbeest_gripper/v3c_rigid-nose | — |
| GRIP-9008 | assy-printed-pins | X1 | ASSY, GRIPPER, THUMB WHEEL, PRINTED PINS, STRANDBEEST V4A | strandbeest_gripper/v4a_printed-pins | — |
| GRIP-9009 | assy-snap-pins | X1 | ASSY, GRIPPER, THUMB WHEEL, SNAP PINS, STRANDBEEST V4B | strandbeest_gripper/v4b_snap-pins | — |
| GRIP-9010 | assy-finray-gripper | X1 | ASSY, GRIPPER, THUMB SCREW, SLIDE-IN FIN RAY FINGERS | finray_tests | — |
| GRIP-9011 | assy-parallel-jaws | X1 | ASSY, GRIPPER, TWIN LEG PARALLEL JAWS, THUMB WHEEL, SNAP PINS, STRANDBEEST V5 | strandbeest_gripper/v5_parallel-jaws | — |
| SO101-0001 | tip-moving-jaw | X1 | TIP, JAW, MOVING, CALIBRATION | gripper_tips | red PLA/PETG, FDM |
| SO101-0002 | tip-fixed-jaw | X1 | TIP, JAW, FIXED, CALIBRATION | gripper_tips | red PLA/PETG, FDM |
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
| LIB-0009 | servo-sts3215 | — | SERVO, STS3215 (vendor STEP) | lib/sts3215 | purchased |

Next free: GRIP-0062, GRIP-9012, SO101-0003, JTNK-0002, JTNK-9002, LIB-0010.
