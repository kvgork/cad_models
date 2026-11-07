# Part-number register

Scheme: `<PROJ>-<NNNN>`. Parts take 0001–8999 and assemblies 9000–9999. A number is never reused or renumbered. Change that breaks fit or function with the old part → new number. Change that keeps fit → next revision.

Codes: `SO101` (SO-101 arm accessories), `JTNK` (JeTank), `GRIP` (gripper R&D), `LIB` (vendor/library parts, read-only).

Revisions: unreleased print iterations are `X1`, `X2`, … (property `revision`, export name, embossed where room). Release = letter `A`, `B`, … (skip I O Q S X Z) + git tag `<PN>/<REV>`.

| PN | Rev | Description | Product folder | Material / process |
|---|---|---|---|---|
| GRIP-0001 | X1 | BASEPLATE, GRIPPER TESTER | gripper_tester | PLA/PETG, FDM |
| GRIP-0002 | X1 | ADAPTER, GRIPPER, DOVETAIL | gripper_tester | PETG, FDM |
| GRIP-0003 | X1 | FRAME, FINGER, STRANDBEEST | strandbeest_gripper | PETG/ASA, FDM |
| GRIP-0004 | X1 | CRANK, FINGER, STRANDBEEST | strandbeest_gripper | PETG, FDM |
| GRIP-0005 | X1 | LINK, J, STRANDBEEST | strandbeest_gripper | PETG, FDM |
| GRIP-0006 | X1 | LINK, K, STRANDBEEST | strandbeest_gripper | PETG, FDM |
| GRIP-0007 | X1 | LINK, C, STRANDBEEST | strandbeest_gripper | PETG, FDM |
| GRIP-0008 | X1 | LINK, F, STRANDBEEST | strandbeest_gripper | PETG, FDM |
| GRIP-0009 | X1 | TRIANGLE, BDE, STRANDBEEST | strandbeest_gripper | PETG, FDM |
| GRIP-0010 | X1 | TRIANGLE, GHI, FINGERTIP, STRANDBEEST | strandbeest_gripper | PETG, FDM |
| GRIP-0011 | X1 | FRAME, DUAL FINGER, STRANDBEEST | strandbeest_gripper (v2) | PETG/ASA, FDM |
| GRIP-0012 | X1 | GEAR, CRANK, SERVO SIDE, Z20 M1 | strandbeest_gripper (v2) | PETG, FDM |
| GRIP-0013 | X1 | GEAR, CRANK, IDLE SIDE, Z20 M1 | strandbeest_gripper (v2) | PETG, FDM |
| GRIP-0014 | X1 | GEAR, IDLER, Z33 M1 (qty 2) | strandbeest_gripper (v2) | PETG, FDM |
| GRIP-0015 | X1 | LINK, J, HUB, STRANDBEEST V2 (qty 2) | strandbeest_gripper (v2) | PETG, FDM |
| GRIP-0016 | X1 | LINK, K, STRANDBEEST V2 (qty 2) | strandbeest_gripper (v2) | PETG, FDM |
| GRIP-0017 | X1 | LINK, C, STRANDBEEST V2 (qty 2) | strandbeest_gripper (v2) | PETG, FDM |
| GRIP-0018 | X1 | LINK, F, HUB, STRANDBEEST V2 (qty 2) | strandbeest_gripper (v2) | PETG, FDM |
| GRIP-0019 | X1 | TRIANGLE, BDE, FINGER 1, STRANDBEEST V2 | strandbeest_gripper (v2) | PETG, FDM |
| GRIP-0020 | X1 | TRIANGLE, GHI, PAD, FINGER 1, STRANDBEEST V2 | strandbeest_gripper (v2) | PETG, FDM |
| GRIP-0021 | X1 | TRIANGLE, BDE, FINGER 2 (MIRROR), STRANDBEEST V2 | strandbeest_gripper (v2) | PETG, FDM |
| GRIP-0022 | X1 | TRIANGLE, GHI, PAD, FINGER 2 (MIRROR), STRANDBEEST V2 | strandbeest_gripper (v2) | PETG, FDM |
| GRIP-9001 | X1 | ASSY, GRIPPER TESTER, FIT CHECK | gripper_tester | — |
| GRIP-9002 | X1 | ASSY, FINGER, STRANDBEEST (v1: single finger + anvil) | strandbeest_gripper | — |
| GRIP-9003 | X1 | ASSY, GRIPPER, DUAL FINGER, STRANDBEEST V2 (feeder) | strandbeest_gripper | — |
| SO101-0001 | X1 | TIP, JAW, MOVING, CALIBRATION | gripper_tips | red PLA/PETG, FDM |
| SO101-0002 | X1 | TIP, JAW, FIXED, CALIBRATION | gripper_tips | red PLA/PETG, FDM |
| JTNK-0001 | X1 | HOLDER, LIDAR, RPLIDAR C1 | lidar_holder | PETG, FDM |
| JTNK-9001 | X1 | ASSY, LIDAR HOLDER, FIT CHECK | lidar_holder | — |
| LIB-0001 | — | BASE, SO-101 (vendor STEP) | lib/so101 | purchased/vendor |
| LIB-0002 | — | HANDLE, SO-101 LEADER (vendor STEP) | lib/so101 | purchased/vendor |
| LIB-0003 | — | JAW, MOVING, SO-101 (vendor STEP) | lib/so101 | purchased/vendor |
| LIB-0004 | — | PLATE, MOUNTING, WAVESHARE, SO-101 (vendor STEP) | lib/so101 | purchased/vendor |
| LIB-0005 | — | WRIST ROLL, FOLLOWER GRIPPER, SO-101 (vendor STEP) | lib/so101 | purchased/vendor |
| LIB-0006 | — | WRIST ROLL PITCH, SO-101 (vendor STEP) | lib/so101 | purchased/vendor |
| LIB-0007 | — | WRIST ROLL, SO-101 (vendor STEP) | lib/so101 | purchased/vendor |
| LIB-0008 | — | LIDAR, RPLIDAR C1 (vendor STEP) | lib/rplidar_c1 | purchased |
| LIB-0009 | — | SERVO, STS3215 (vendor STEP) | lib/sts3215 | purchased |

Next free: GRIP-0023, GRIP-9004, SO101-0003, JTNK-0002, JTNK-9002, LIB-0010.
