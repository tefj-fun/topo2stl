---
name: topology-print-release
description: Run or review topology-optimized FDM structural parts from design envelope and BESO through symmetry control, printable reconstruction, independent FEA, slicing, and release. Use for structural 3D-print topology workflows; do not invoke for ordinary CAD edits or slicer-only tuning.
---

# Topology Print Release

Produce a versioned printable artifact with evidence that survives smoothing and slicing. Reuse project-local CAD, BESO, FEA, and slicer scripts before adding new tooling.

## Start from declared inputs

Resolve these before optimization:

- authoritative interface dimensions and screw/insert access;
- design domain, protected solids, and mandatory voids;
- restraint, load positions, load cases, mass, and center of gravity;
- actual printer orientation, material, walls, infill, layer height, and line width;
- configurable displacement, strength, volume, and fit acceptance limits.

Do not infer missing physical interfaces from an optimized mesh. Stop for user direction when a missing choice would change the mechanism or load path.

## Confirm the loading

Before running BESO or FEA, obtain the following from project evidence or ask the user to confirm it:

- payload mass and center of gravity relative to the mount;
- exact restrained interfaces and load-application regions;
- force direction, torque arm, and whether gravity acts in more than one orientation;
- static, acceleration, braking, vibration, shock, cable-pull, and handling load cases that apply;
- load multipliers or required safety factor and the failure condition being protected against.

Show the resulting load table to the user before solving. Do not substitute an assumed point load at a convenient node. If a required value is unknown, label a proposed conservative assumption and wait for confirmation rather than treating it as measured input.

## Required gates

1. Build and audit the full-density design domain.
2. Apply loads to the real attachment regions, not convenient nearby faces.
3. Run BESO with protected interfaces and connectivity checks.
4. When mirror symmetry is required, pair mirrored elements during sensitivity filtering and keep/remove updates. A mirrored reconstruction is a safeguard, not a substitute; report which level was used.
5. Reconstruct and smooth at controlled resolution while holding the material target.
6. Restore exact bosses, holes, insert bores, tool channels, and contact planes.
7. Require one connected watertight body, correct interfaces, clear tooling paths, and a quantitative symmetry audit when applicable.
8. Independently remesh the final printable surface and rerun print-aware FEA. Do not reuse optimization stresses as release evidence.
9. Slice using the declared printer configuration and inspect supports, holes, time, material, and build orientation.
10. Keep physical printing and printer motion separate from artifact generation. Upload or start only when the user explicitly asks, after checking live printer state.

Do not call an STL printable when any required gate fails. Preserve earlier verified releases and write a new version instead of overwriting them.

For the detailed flow and evidence checklist, read [references/pipeline.md](references/pipeline.md). When selecting or changing optimization, reconstruction, mesh, or print parameters, also read [references/parameter-tuning.md](references/parameter-tuning.md).
