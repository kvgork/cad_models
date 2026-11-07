# cad_models

3D-printable robot parts and mechanisms, designed in SolidCraft as **parametric command scripts**. Every model is a JSON script that SolidCraft replays to build the design and its STEP / STL / 3MF exports. Most parts are for the [SO-101](https://github.com/TheRobotStudio/SO-ARM100) robot arm and a JeTank robot.

![Strandbeest gripper v2: two mirrored Jansen-linkage fingers driven by one servo](strandbeest_gripper/v2_dual-finger/docs/GRIP-9003_assy-dual-finger_iso.png)

## Products

| Product | What it is | Status |
|---|---|---|
| [gripper_tester](gripper_tester/README.md) | Bench baseplate with a dovetail slide for swapping SO-101 grippers, plus a mount for the Waveshare servo board | X1, CAD-checked |
| [gripper_tips](gripper_tips/README.md) | Snap-on calibration caps for the two SO-101 gripper jaws (print in red) | X1, CAD-checked |
| [lidar_holder](lidar_holder/README.md) | Riser that mounts an RPLIDAR C1 on the JeTank | X1, CAD-checked |
| [strandbeest_gripper](strandbeest_gripper/README.md) | Gripper built from Theo Jansen's Strandbeest leg. Six versions: one finger (v1), a two-finger feeder (v2), three long-jaw variants (v3a/b/c) and a hand-operated thumb-wheel version (v4) | X1, CAD-checked, not printed yet |

"CAD-checked" means the kinematics, fits and collisions were verified in SolidCraft by the scripts in the repo. Nothing in an X1 has been printed and measured yet.

## Printing

Ready-to-print files are in each product's `exports/` folder (or `<version>/exports/` for products with several versions). The file name tells you what the part is:

```
GRIP-0015_link-j-hub_X1.stl
└─ part no.└─ name   └─ revision (X1 = first unreleased print iteration)
```

- **Materials:** use PETG or ASA for loaded parts and parts next to servos; PLA is fine for fit checks.
- **Print settings and hardware:** each README lists print orientation, screws, inserts and assembly order.
- **All parts:** [PARTS.md](PARTS.md) lists every part number with its name, folder and material.

## Getting the files

The binary files (`.sc`, `.step`, `.stl`, `.3mf`, `.png`) are stored with **Git LFS**. Install it before cloning:

```bash
git lfs install
git clone git@github.com:kvgork/cad_models.git
```

Without LFS you get small pointer files instead of models.

## Editing and rebuilding

Requires SolidCraft **0.30.1** (`solidcraft-cli`); see [TOOLS.md](TOOLS.md).

```bash
tools/build.sh                                   # rebuild every part and its exports
tools/build.sh gripper_tips                      # one product
tools/build.sh strandbeest_gripper/v2_dual-finger  # one version of a product
tools/build.sh --assemblies                      # also run the fit-check overlays (slow)
```

- **The `.json` script is the source of truth.** Change parameters there, or in the Python generator for the strandbeest gripper, then rebuild. Never hand-edit exports.
- **Mechanisms have verification scripts.** For example, `python3 strandbeest_gripper/tools/verify_dual.py` drives the joints, checks the kinematics against the analytic model and sweeps for collisions.

## Layout and naming

```
<product>/
  README.md                         what it is, interfaces, print notes, hardware
  cad/<PN>_<name>.json              command script = source of truth (parametric)
  cad/<PN>_<name>.sc                built design (open in SolidCraft); regenerated
  cad/<PN>_<name>.check.json        fit / clearance check on top of a part
  exports/<PN>_<name>_<REV>.{step,stl,3mf}   generated print / exchange files
  tools/                            generators and verification scripts (if any)
<product>/v<N>_<name>/              products with several design versions: one complete
                                    folder per version (README, cad/, exports/, docs/)
lib/<group>/<LIB-NNNN>_<name>.*     third-party vendor models (read-only) + SOURCE.md
tools/build.sh, tools/parts.py      build script; PARTS.md reader
PARTS.md   TOOLS.md   CLAUDE.md     part register · pinned tools · conventions for AI-assisted work
```

**Part numbers:**
- `<PROJ>-<NNNN>`, where PROJ is `GRIP` (gripper R&D), `SO101`, `JTNK` (JeTank) or `LIB` (vendor).
- 0001–8999 are parts and 9000–9999 are assemblies.
- A change that keeps fit gets a new revision (`X2`…, then `A`, `B` at release). A change that breaks fit gets a new number.

## License

My own designs, scripts and documentation are released under the **MIT License**: see [LICENSE](LICENSE). The vendor models in `lib/` keep their own licenses, listed in each `lib/<group>/SOURCE.md`:
- SO-ARM100 and STS3215 models: Apache-2.0, from TheRobotStudio.
- RPLIDAR C1 model: SLAMTEC vendor terms.
