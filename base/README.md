# base: general CAD files, reused across projects

Building blocks that more than one project needs: vendor models of bought parts (servos, boards, sensors) and, later, our own reusable parts (standard horns, mounting plates, …).

| Folder | PN | What | Notes |
|---|---|---|---|
| [feetech_sts3215](feetech_sts3215/SOURCE.md) | LIB-0009 | Feetech STS3215 serial-bus servo: **all 6 joints of the SO-101** leader and follower (C001 / C044 / C046 / C018 / C047 share one case); 45.2 × 24.7 × 35 mm | SO-ARM100 model (Apache-2.0) **incl. Ø20 horn**; interfaces measured vs Feetech drawing; per-joint variant table; placement matrix |
| [feetech_scs0009](feetech_scs0009/SOURCE.md) | LIB-0010 | Feetech SCS0009 micro serial-bus servo (6 V, 2.3 kg·cm, 23.3 × 12.1 × 25.25 mm) | vendor STEP (MIT via step.parts), interfaces measured, Z-up placement matrix |

**Rules:**
- **Vendor files:** one folder per item, `base/<maker>_<model>/`, holding `<LIB-NNNN>_<name>.step` plus `SOURCE.md`. SOURCE.md records the source URL, licence, sha256, the interfaces measured on the model (`model.faces`, never from a picture), a cross-check against the datasheet, and a placement matrix.
- **Read-only, like `lib/`:** never edit a vendor file. A better model gets a new file and SOURCE.md entry.
- **Derived meshes:** STL and 3MF sit next to the STEP, exported in the same coordinates. Use them for visualisation only.
- **In assemblies:** insert the STEP with `file.insert_step`, set `component.metadata.set … bom_type: "purchased"`, and place it with the matrix from SOURCE.md.
- **Our own reusable parts:** these get a `cad/` script and `exports/`, like a product, and a PN from their project code.

The older vendor parts stay in `lib/` (SO-101 arm parts, STS3215, RPLIDAR C1), because existing generators reference those paths. The STS3215 is also in `base/`, as a byte-identical copy (LFS stores it once); new designs use the `base/` one.
