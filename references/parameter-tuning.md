# Parameter tuning

Treat these as starting ranges, not universal release criteria. Tune one parameter family at a time and retain the baseline result for comparison.

## Tuning order

1. Correct interfaces, loads, restraints, material orientation, and protected regions.
2. Establish a converged full-density FEA baseline.
3. Tune BESO filter radius and evolutionary rate.
4. Select target volume from structural acceptance, not appearance.
5. Tune reconstruction resolution and physical smoothing radius.
6. Independently remesh and verify the printable surface.
7. Calibrate slicer dimensions and material behavior with coupons.

Do not compensate for a wrong load model by adding material or lowering the volume target.

## BESO

| Parameter | Starting guidance | Increase when | Decrease when |
|---|---|---|---|
| Evolutionary removal rate | 1-2% per iteration; 0.5-1% near convergence | Progress is stable but unnecessarily slow | Load paths disappear, compliance oscillates, or connectivity repeatedly fails |
| Sensitivity filter radius | 1.5-3 element widths | Checkerboards, isolated elements, or nozzle-scale branches appear | Distinct nearby load paths are being merged |
| Target volume fraction | Explore a bounded sweep such as 60%, 50%, 40%, then refine | Displacement or robust FoS misses acceptance | The design passes comfortably and weight remains the priority |
| Convergence window | Compare 10-20 recent iterations | Compliance remains noisy | The history is stable and repeatable |

Require protected elements and connectivity after every keep/remove update. For required symmetry, average mirrored sensitivities and apply one shared density decision to each pair.

## Optimization mesh

- Keep at least 3 elements across the smallest structural member BESO may retain.
- Refine attachment and restraint regions enough to distribute loads without single-node artifacts.
- Repeat with a 20-30% smaller element size before release. As a starting convergence check, require maximum displacement to change less than 5% and the robust FoS metric less than 10%.
- Do not tune from peak stress at an ideal fixed edge alone.

## Reconstruction

| Parameter | Starting guidance | Failure signal |
|---|---|---|
| Field spacing | 0.25-0.5 of the smallest printable feature to preserve | Larger spacing erases holes and thin paths; very small spacing adds cost without useful geometry |
| Physical smoothing radius | Roughly 0.5-1.5 mm for ordinary FDM brackets, converted to voxels using the field spacing | Too high thins joints and moves interfaces; too low preserves voxel roughness |
| Iso-level/volume correction | Recover target material volume within 0.5% | Larger error invalidates weight and FEA comparisons |

Restore exact interfaces after smoothing. Quantitatively audit wall thickness, holes, insert bores, tool access, component count, watertightness, and symmetry.

## Print-aware model and slicing

- Use measured or conservative directional properties for the chosen material and orientation.
- Model the intended wall count and infill rather than a solid isotropic part.
- Add walls before increasing infill when failure is concentrated at the shell or attachment regions; increase infill when broad internal shear or compression controls.
- Calibrate hole and insert dimensions with a coupon. Use slicer polyhole conversion or hole compensation only from measured results.
- Treat support, orientation, layer height, temperature, and line width as structural inputs because they change bonding and effective properties.

## Symptom-driven adjustments

| Symptom | First adjustment |
|---|---|
| Checkerboard or noisy topology | Increase sensitivity filter radius |
| One side differs despite symmetric requirements | Verify mirrored element pairs before reconstruction |
| Thin branches vanish after smoothing | Reduce smoothing radius or raise minimum member size during BESO |
| Excess material with high FoS margin | Lower target volume gradually and rerun independent FEA |
| Displacement fails but FoS passes | Preserve or thicken long load paths rather than only enlarging bosses |
| FoS fails near an attachment | Expand the protected load-transfer region and improve load distribution |
| Final FEA is much worse than optimization FEA | Refine reconstruction, restore interfaces, and compare boundary/load mappings |
| Printed holes undersize | Use a measured coupon adjustment; do not enlarge every CAD interface blindly |
