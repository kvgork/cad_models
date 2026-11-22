# storage_drawers

Stackable, 3D-printed storage (user request 2026-11-18): shelves whose top is the lid of the drawer below it, drawers with a Gridfinity 5 × 4 floor (customise them with bins; the shelf never changes), a spacer frame that goes under a shelf to make room for a taller drawer. Everything prints on the Bambu X2D. Stage 1: the core parts and one test bin; bins for the fastener sets (M2–M5 bolts/nuts/washers, M3 standoffs) and the Bambu finishing kit come later.

| Version | What | Status |
|---|---|---|
| [v1_gridfinity](v1_gridfinity/README.md) | Shelf STOR-0001, drawer STOR-0002, spacer STOR-0003, test bin STOR-0004 | printed: drawer stuck, handle weak |
| [v2_loose-fit](v2_loose-fit/README.md) | New drawer STOR-0005: more slide clearance (body to pad 1.0, flange 0.7, rail 0.4, lid 0.8), hook handle; same shelf, spacer, bin | X1, CAD-checked (19/19), not printed yet |

**Interfaces (fixed by the shelf):** stack pitch 53 mm; shelf 236 × 189 outside; drawer flanges rest on rails whose top is 46.0 above the shelf's wall bottom, inner edge 113.2 from the centre line; detent pocket in a pad on each wall (pad face 112.0, pocket 0.8 deep at y 16); drawer front panel stops on the shelf front.

Generator and checks for all versions: `tools/gen_storage.py [assy|check] --ver v1|v2`, `tools/verify_storage.py --ver v1|v2`, `tools/build_guide_storage.py --ver v1|v2`.
