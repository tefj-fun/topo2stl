# Topology Print Release

A reusable Codex skill for taking topology-optimized FDM structural parts from design-domain definition through BESO, printable reconstruction, independent FEA, slicing, and release evidence.

## What it enforces

- Real attachment loads and protected interfaces before optimization
- Optional mirrored-element symmetry during BESO
- Controlled smoothing with exact interface restoration
- Watertightness, connectivity, fit, tooling, and symmetry audits
- Independent print-aware FEA of the final printable surface
- Slicer and physical-test gates before declaring a release printable

The skill is workflow guidance. It reuses the CAD, BESO, FEA, and slicer tools already present in each project rather than imposing a particular solver.

## Install

```bash
git clone https://github.com/tefj-fun/topology-print-release-skill.git \
  ~/.codex/skills/topology-print-release
```

Restart Codex if the skill does not appear immediately.

## Use

```text
Use $topology-print-release to build or audit this topology-optimized printable part.
```

Project-specific dimensions, loads, material calibration, printer settings, solver commands, and acceptance limits remain in the project being analyzed.

## Safety boundary

Simulation does not replace fit coupons, supervised first prints, proof loading, or inspection for layer-separation and insert failure. The skill requires explicit authorization before uploading to or starting a physical printer.

## License

MIT
