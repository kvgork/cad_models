# cad_models

These are personal CAD models built with SolidCraft. Each one is a parametric command script; the design files and exports are generated from it.

| Product | Parts | What |
|---|---|---|
| [gripper_tester](gripper_tester/README.md) | GRIP-0001, GRIP-0002, GRIP-9001 | Bench baseplate + dovetail adapter for swapping SO-101 grippers; Waveshare board mount |
| [gripper_tips](gripper_tips/README.md) | SO101-0001, SO101-0002 | Snap-on red calibration caps for the SO-101 gripper jaws |
| [lidar_holder](lidar_holder/README.md) | JTNK-0001, JTNK-9001 | RPLIDAR C1 riser for the JeTank |
| [strandbeest_gripper](strandbeest_gripper/README.md) | GRIP-0003…0010, GRIP-9002 | Jansen-linkage (Strandbeest) finger v1, STS3215-driven |

- Part numbers and revisions: [PARTS.md](PARTS.md).
- Pinned tool versions: [TOOLS.md](TOOLS.md).
- Vendor models: `lib/` (read-only, each group has a `SOURCE.md`).

## Layout

```
<product>/
  README.md        what it is, interfaces, print notes
  cad/<PN>.json    command script = source of truth (parametric)
  cad/<PN>.sc      built design (open in the GUI); regenerated
  cad/<PN>.check.json   overlay: fit/clearance check on top of a part
  exports/<PN>_<REV>.{step,stl,3mf}   generated; never hand-edit
  exports/_superseded/                old exports, kept
  tools/           generator / analysis scripts (optional)
lib/<group>/LIB-NNNN.<ext> + SOURCE.md
tools/build.sh     rebuild everything (`--assemblies` also runs overlays)
```

## Build

```bash
tools/build.sh                     # all parts
tools/build.sh gripper_tips        # one product
tools/build.sh --assemblies        # also fit-check overlays (~10 min)
```
