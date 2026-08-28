# Camera-mount evidence example

This example is an actual saved 90-degree camera-mount development run used to shape Topo2STL's evidence requirements.

## Declared load case shown

- Payload: 2.0 kg
- Center of gravity: `(0, 0, -51.15)` mm
- Fore-aft acceleration: 4g
- Applied force: `Fy = -78.5 N`
- Applied moment: `Mx = -4.01 N*m`
- Restraint: distributed contact at the camera insert face

![Load map and final FEA hotspot](../../assets/readme/05-final-fea-hotspot.png)

## Saved development checkpoints

| Baseline | Clean load-path concept |
|---|---|
| ![Ribbed baseline](../../assets/readme/01-baseline-ribbed.png) | ![Clean topology concept](../../assets/readme/02-clean-topology.png) |

| Raw reconstructed BESO surface | Smoothed and interface-restored printable body |
|---|---|
| ![Raw reconstructed BESO surface](../../assets/readme/03-raw-beso-reconstruction.png) | ![Final printable body](../../assets/readme/04-final-printable.png) |

The historical run did not retain exact 80%, 60%, and 40% iteration renders, so these are labeled as development checkpoints rather than falsely presented as material-fraction snapshots. New Topo2STL runs require fraction or evenly spaced iteration checkpoints before release.

## Final evidence

- Maximum displacement: 0.70 mm
- p99 directional factor of safety: 8.95
- Peak hotspot: 192.1 MPa at the idealized fixed boundary; retained for inspection rather than used as the robust release metric
- Supported slice: 0.20 mm profile, two walls, 15% crosshatch infill, build-plate-only normal supports, 38.27 g and approximately 2 h 13 min

![Actual sliced G-code toolpath](../../assets/readme/06-slicer-preview.png)

These results apply only to this geometry, load model, material assumptions, mesh, and slicer profile. They are an evidence-format example, not a reusable strength claim.
