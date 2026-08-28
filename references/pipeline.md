# Topology-to-print pipeline

## Flow

```text
Requirements and interfaces
  -> design envelope
  -> protected solids and mandatory voids
  -> print-aware material and load model
  -> symmetric FEA mesh and mirrored element pairing
  -> iterative BESO removal
  -> controlled signed-distance reconstruction
  -> exact interface restoration
  -> topology, fit, and symmetry audits
  -> independent final-surface FEA
  -> slicer validation
  -> physical coupon, proof load, and release
```

## Pre-BESO evidence

- Interface source and revision
- Coordinate system and print orientation
- User-confirmed load table covering payload mass, center of gravity, forces, moments, directions, application regions, restraints, dynamic/shock cases, and load multipliers
- Protected attachment regions
- Mandatory holes, counterbores, insert bores, and assembly clearances
- Load and restraint node counts
- Material model tied to the intended print configuration
- Full-density baseline FEA
- Mirrored element-pair coverage when symmetry is required

## BESO loop

For each iteration:

1. Solve all load cases.
2. Calculate and filter element sensitivities.
3. Average each mirrored pair when symmetry is enabled.
4. Force protected elements to remain solid.
5. Remove the least useful eligible elements at the configured evolutionary rate.
6. Reject disconnected paths between any attachment and the restrained interface.
7. Record volume, compliance, failure indicators, and convergence.

Stop on convergence and target volume, not merely an arbitrary iteration count.

## Reconstruction and release evidence

- Field spacing, smoothing strength, iso-level, and target-volume error
- Whether symmetry was enforced in BESO, reconstruction, or both
- Component and open/non-manifold edge counts
- Mirror-surface deviation
- Interface diameters, locations, and tool-channel obstruction
- Independent mesh node/tetrahedron counts
- Per-case displacement and directional factor of safety
- Slicer printer/nozzle/material, walls, infill, support, layer height, estimated mass, and time
- Visual evidence listed in `visual-evidence.md`, displayed to the user rather than only written to disk

Peak stress at an ideal fixed boundary may be a mesh singularity. Use the declared robust release metric, but retain the peak for inspection.

## Project integration

For each project, locate and map its existing tools to these stages before adding code:

- design-domain and protected-region construction;
- BESO solve and sensitivity update;
- printable reconstruction and interface restoration;
- independent final-surface FEA;
- slicer export and physical validation.

Keep dimensions, loads, printer settings, acceptance thresholds, and tool commands in the project repository rather than this reusable skill. Report whether symmetry is enforced during optimization, reconstruction, or both; never imply optimizer-level symmetry from a mirrored final mesh alone.
