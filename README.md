# Topo2STL

A reusable Codex skill for taking topology-optimized FDM structural parts from design-domain definition through BESO, printable reconstruction, independent FEA, slicing, and release evidence.

## What it enforces

- Real attachment loads and protected interfaces before optimization
- Explicit user confirmation of payload, center of gravity, restraints, forces, moments, and dynamic load cases
- Optional mirrored-element symmetry during BESO
- Controlled smoothing with exact interface restoration
- Watertightness, connectivity, fit, tooling, and symmetry audits
- Independent print-aware FEA of the final printable surface
- Slicer and physical-test gates before declaring a release printable
- Starting ranges and failure-driven tuning rules for BESO, meshing, reconstruction, interfaces, FEA, and slicing
- Before/after renders, optimization-progress images, convergence plots, FEA hotspots, and slicer evidence

The skill is workflow guidance. It reuses the CAD, BESO, FEA, and slicer tools already present in each project rather than imposing a particular solver.

## Install

```bash
git clone https://github.com/tefj-fun/topo2stl.git \
  ~/.codex/skills/topo2stl
```

Restart Codex if the skill does not appear immediately.

## Use

```text
Use $topo2stl to build or audit this topology-optimized printable part.
```

Project-specific dimensions, loads, material calibration, printer settings, solver commands, and acceptance limits remain in the project being analyzed.

## Safety boundary

Simulation does not replace fit coupons, supervised first prints, proof loading, or inspection for layer-separation and insert failure. The skill requires explicit authorization before uploading to or starting a physical printer.

## License

MIT
