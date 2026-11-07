# CLAUDE.md

Personal CAD models (SO-101 arm, JeTank, gripper R&D), built with SolidCraft and kept in git.

These rules come from the Second Brain vault (`/home/koen/Documents/Vaults/Local/05-Wiki/research/`):
- `2026-11-06-cad-project-structure-best-practices.md`: naming, folders, git, revisions
- `2026-11-06-ai-assisted-cad-claude.md`: the SolidCraft MCP verification loop
- `2026-11-06-cad-rapid-prototyping-3d-printing.md`: print iterations and FDM parameters

If a rule here conflicts with those notes, the notes win; update this file to match.

## Tools (pinned, see TOOLS.md; never upgrade without asking)

- SolidCraft 0.30.1 (`solidcraft-cli` in `~/.local/bin`). Format 48 files do not open in older builds. No nightly or RC builds for committed files.
- git with git-lfs (patterns in `.gitattributes`).

## Layout

```
<product>/README.md              what it is, interfaces, print notes
<product>/cad/<PN>.json          command script: the source of truth (parametric)
<product>/cad/<PN>.sc            built design, regenerated from the script (LFS)
<product>/cad/<PN>.check.json    overlay: fit/clearance check run with --in <part>.sc
<product>/exports/<PN>_<REV>.{step,stl,3mf}   generated only; never hand-edit
<product>/exports/_superseded/   replaced exports are moved here, never deleted
<product>/tools/                 generator or analysis scripts (python), repo-relative paths
lib/<group>/LIB-NNNN.<ext> + SOURCE.md   vendor parts, READ-ONLY
tools/build.sh                   rebuild all (`--assemblies` runs overlays, ~10 min)
PARTS.md                         part-number register; TOOLS.md pinned versions
```

## Naming and revisions

- **Native file name = part number, never the revision:** `<PROJ>-<NNNN>`, using only `A–Z 0–9 - _`.
  - PROJ is `SO101`, `JTNK`, `GRIP` or `LIB`.
  - 0001–8999 are parts and 9000–9999 are assemblies.
  - Never reuse or renumber a part number.
- **New part number:** take the next free one from `PARTS.md`, add a row there, and tell the user it was allocated.
- **Export name:** `<PN>_<REV>.<ext>`.
  - Unreleased print iterations are `X1`, `X2`, ….
  - A release takes a letter `A`, `B`, … (skip I O Q S X Z) and a git tag `<PN>/<REV>`.
  - A change that breaks fit or function with the old part gets a **new part number**. A change that keeps fit gets the next revision.
- **First command of every part script:** `document.metadata.set` with `part_number`, `description` (`NOUN, MODIFIER`, upper case), `revision` and `project`.
- **Assemblies:** set `component.metadata.set` (`part_number`, `description`, `bom_type`; `purchased` for `lib/` parts) on every component.
- **Names inside the model:** every feature, body, parameter and interface gets a name. Parameters get a comment that says the design intent.

## git

- `.sc .step .stp .stl .3mf .pdf .png` go through LFS (`.gitattributes`). Never commit before `git lfs env` works.
- `cad/*.json` use `diff merge=binary`: never let git auto-merge a command script.
- Commit **before** every export that will be printed; the export and the print log refer to that commit.
- Commit the script and its regenerated `.sc`/exports together.
- A SolidCraft version bump is its own commit.
- Ignored: `.agent-state/`, `*.bak`, `.~*.lock`.

## Modelling with SolidCraft

- **Script first.** Write or edit `<PN>.json`, then `tools/build.sh <product>` or `solidcraft-cli run cad/<PN>.json --save cad/<PN>.sc`.
  - Script paths are relative to the repo root.
  - Exports are steps in the script.
  - The `.sc` is never the master.
- **Parametric:** sizes, fits and positions are named parameters or expressions. No magic numbers in features.
- **Feature order:** fully define sketches, sketch on planes, origin-centred. Order is base → add/cut → holes → fillets and chamfers last.
- **Picks:** picking an edge or face by a coordinate breaks when dimensions change. Re-verify after every parameter change.
- **Assemblies and mechanisms:**
  - Ground one fixed reference.
  - Use `joint.create` (revolute, slider…) with limits.
  - Check motion with `joint.drive`, `motion.trace` and `joint.sweep` (collisions over the range).
- **`solidcraft-cli` subcommands:**
  - `run x.json --save x.sc [--in base.sc] [--results] [--json-out f]`
  - `eval x.sc` (bodies, bbox, volume, timeline errors)
  - `snapshot --in x.sc --out shot.png --view iso`
  - `commands` (the full catalog; grep it)
- **Fit checks:** `file.insert_step` the `lib/` part, place it with `occurrence.move` (`"<name>:1"`, `move_grounded: true`, a 3×4 `matrix`), then run `inspect.clearance` with `against: [...]`. Without `against` it checks 0 pairs. Against big vendor STEPs it is slow (~10 min) and can return `unchecked`; confirm those pairs with `inspect.section`.

## Verification loop (required before saying a part is done)

1. **Spec first.** Write down the envelope, interface positions and diameters, wall thickness and expected volume/bbox in the README or the request.
2. **Build in small stages:**
   - MCP: `batch` with `expect` (bodies, bbox, `volume_mm3`).
   - CLI: `eval` after each stage.
3. **Measure:** `measure`/`eval` after each stage. Get hole and boss positions from `body_topology` (cylinder origin, axis, radius), never from volume or a picture. A cut that leaves the volume unchanged missed.
4. **Parameter range:** `check_parameters` (MCP) or a `parameters.change` run confirms the model rebuilds across the parameter range.
5. **Fit and motion:** `inspect.clearance` / `inspect.section` for fit; `joint.sweep` for mechanisms.
6. **Screenshot last:** a sanity check, never proof. Never claim a dimension from an image.
7. **Export:** re-eval the export, report the numbers against the spec in a table, and say plainly what was not checked.

## FDM printability (defaults; calibrate per printer and material, then write the measured value back)

- **Walls:** `nozzle 0.4`, `line_w 0.45`, `layer_h 0.2`. Walls on the perimeter grid (0.9 / 1.35 / 1.8 mm); nothing under one perimeter.
- **Clearances:** `fdm_clearance 0.2` (sliding). Moving parts 0.3. Rotating pin holes for M3: Ø3.4 (ISO 273 medium).
- **Heat-set inserts:** M3 hole Ø4.0–4.2, blind, ≥ 1 mm deeper than the insert. Use inserts for anything unscrewed twice.
- **Orientation and overhangs:**
  - Chamfer bed-facing edges; don't fillet them.
  - Overhangs ≤ 45–60° without supports.
  - Don't grow snap hooks straight up off the bed.
- **Horizontal holes:** they print small; use a teardrop or a measured offset.
- **Elephant foot:** about 0.2 mm, handled by the slicer; don't also chamfer the same edge in CAD.
- **Strength:** more perimeters, not more infill.
- **Materials:**
  - PLA only for static fit checks.
  - PETG for links.
  - ASA/PETG next to servos (they run warm).
- **Part marking:** bold capitals ≥ 4 mm, debossed ≈ 0.6 mm on a top or low-stress face. Too small for text: dots or a bag label.
- **First print on a new printer or material:** print a coupon first.

## SolidCraft MCP server

- **Tools:** `skill_reference {"skill":"solidcraft-modeling"}` first, then `inspect_design`, `batch`, `measure`, `body_topology`, `check_parameters`, `screenshot`.
- **Path sandbox:** MCP `open` and `save` only work inside `/tmp/solidcraft-mcp-<pid>-*`.
  - Build with the CLI in the repo, then copy the `.sc` there to view it in the GUI.
  - To fix this permanently, start the server with `--allow-path /mnt/data/workspaces/cad_models`.
- **Live GUI:** port in `~/.local/share/solidcraft/control/current.port`, token in `<port>.token`. Bridge with `solidcraft-cli mcp --connect 127.0.0.1:<port> --token <t>`.

## Hard limits

- Never modify anything under `lib/`, `exports/_superseded/` or a released (tagged) revision.
- Never call `new_design` over an existing file, and never use `--allow-any-path`.
- Never upload CAD files to external services.
- Never start a print. Uploads to a printer use auto-start off; a human starts every print.
- Tolerances, fits and DFM sign-off are drafts until printed and measured. Mark them **NEEDS PRINT TEST** in the README.
- Before moving or renaming files: make a backup, or make sure the tree is committed. Then rebuild and compare volume and bbox per part.
