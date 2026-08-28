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
| Target volume fraction | Start at 50-60%; test 5-10 percentage-point reductions, then refine in 2-3 point steps around the lightest passing result | Displacement, robust FoS, connectivity, or minimum-member checks fail | Every load case passes with margin and mass remains the priority |
| Convergence window | Compare 10-20 recent iterations; a useful starting stop rule is less than 1-2% relative compliance change with stable connectivity and volume | Compliance remains noisy or members toggle | Compliance, topology, and volume are stable and repeatable |

Require protected elements and connectivity after every keep/remove update. For required symmetry, average mirrored sensitivities and apply one shared density decision to each pair.

## Optimization mesh

- Keep at least 3 elements across the smallest structural member BESO may retain.
- Refine attachment and restraint regions enough to distribute loads without single-node artifacts.
- Start with an element size no larger than one third of the minimum allowed member thickness. Reduce it by 20-30% for each refinement.
- Run at least two final-surface meshes. As a starting convergence check, require maximum displacement to change less than 5%, the robust FoS metric less than 10%, and reaction-force imbalance less than 1% of applied load.
- Compare p95 or p99 directional stress/FoS away from ideal fixed-edge singularities; retain peak stress only as a hotspot diagnostic.
- Do not tune from peak stress at an ideal fixed edge alone.

## Interfaces and minimum printable members

Express minimums in extrusion widths so the guidance scales with nozzle and line width. For a 0.4 mm nozzle with about 0.45 mm line width, use these conservative starting values:

| Feature | Starting minimum | Decision rule |
|---|---|---|
| Free structural rib or wall | 3-4 line widths, about 1.35-1.8 mm | Use 4 widths for primary load paths or unfavorable layer orientation; never retain a one- or two-line topology branch as structural material |
| Hole-edge ligament | 3-4 line widths from finished hole to free edge | Increase when bearing or tear-out controls |
| Boss radial wall outside an insert | 3-4 line widths beyond the insert OD | Increase to 5-6 widths when installation heat, high clamp load, or layer splitting is credible |
| Boss-to-body transition | Fillet radius at least 2 line widths, with a gradual rib or gusset | Increase when FEA shows a sharp stress gradient at the boss root |
| Protected interface depth | Full insert engagement plus 1-2 layer heights of closed material, without blocking the screw | Increase only when pull-out or bottom-skin failure controls |

Preserve the exact hole, insert, contact-plane, and tool-access geometry during optimization and restore it after smoothing. Validate insert dimensions and installation temperature with a coupon; generic boss ratios do not prove pull-out strength.

## Reconstruction

| Parameter | Starting guidance | Failure signal |
|---|---|---|
| Field spacing | 0.25-0.5 of the smallest printable feature to preserve | Larger spacing erases holes and thin paths; very small spacing adds cost without useful geometry |
| Gaussian smoothing sigma | Start at 1.0 voxel; sweep 0.5, 1.0, 1.5, and at most 2.0 voxels while monitoring minimum thickness and volume | Too high thins joints and moves interfaces; too low preserves voxel roughness |
| Physical smoothing radius | Keep the effective radius near 0.5-1.5 mm for ordinary FDM brackets and report both millimetres and voxels | A voxel-only value changes physical behavior when field spacing changes |
| Iso-level/volume correction | Recover target material volume within 0.5% | Larger error invalidates weight and FEA comparisons |

Restore exact interfaces after smoothing. Quantitatively audit wall thickness, holes, insert bores, tool access, component count, watertightness, and symmetry.

## Print-aware model and slicing

- Use measured or conservative directional properties for the chosen material and orientation.
- Model the intended wall count and infill rather than a solid isotropic part.
- For a 0.4 mm nozzle, begin structural trials at 3-4 walls, 20-35% infill, 0.16-0.24 mm layers, and 0.42-0.48 mm line width. Treat these as experiment bounds, not certified defaults.
- Add walls before increasing infill when failure is concentrated at the shell, boss, hole, or attachment region. Increase infill in 5-10 percentage-point steps when broad internal shear or compression controls.
- Choose orientation to keep primary tensile load paths within layers. If Z tension cannot be avoided, use measured interlayer properties and increase section area instead of assuming isotropic PLA.
- Use support only where unsupported angles, bridges, or interface quality require it. Begin support-angle trials near 50-55 degrees, keep support away from precision bores when possible, and inspect the sliced load path for unsupported starts.
- Calibrate hole and insert dimensions with a coupon. Sweep diametral compensation in 0.05 mm steps around zero; use slicer polyhole conversion or hole compensation only from measured results.
- Treat support, orientation, layer height, temperature, and line width as structural inputs because they change bonding and effective properties.

## What to tune first

| Failure | Tune first | Then, if still needed | Do not start with |
|---|---|---|---|
| Strength or FoS fails | Verify loads/restraints and print orientation; enlarge the controlling load path or protected transfer region | Add one wall, then raise infill only if internal shear/compression controls | Global smoothing or arbitrary solid infill |
| Displacement fails but FoS passes | Deepen or straighten long load paths and increase section moment of inertia | Raise target volume locally or preserve another rib | Thickening only the bolt bosses |
| Weight is too high | Lower BESO target volume by 2-5 percentage points and rerun all cases | Reduce non-load-bearing wall count or infill after slice inspection | Removing protected interfaces or minimum ligaments |
| Surface is too rough | Reduce mesh size or reconstruction field spacing, then tune sigma in 0.5-voxel steps | Apply controlled surface fairing with volume recovery | Large cosmetic smoothing after FEA |
| Thin members disappear | Lower sigma or enforce a larger minimum member during BESO | Increase local protected material | Raising iso-level without checking total volume |
| Supports are excessive | Change print orientation or enforce self-supporting topology constraints | Adjust support angle and local support painting | Deleting structural members after optimization |
| Holes print poorly | Print a hole/insert coupon and apply measured diametral compensation | Use polyhole conversion and change orientation | Editing all nominal CAD diameters by guesswork |

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
