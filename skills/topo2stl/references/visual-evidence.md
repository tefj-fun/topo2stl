# Visual evidence

Generate and show visual evidence at each decision gate. Saving images without displaying them to the user does not satisfy the gate. Use actual solver, mesh, slicer, and camera outputs; never substitute a conceptual illustration for analysis evidence.

## Required evidence set

1. **Load map before optimization:** show restrained faces, every load-application region, force arrows, moment axes, center of gravity, coordinate axes, and units. Label each load case.
2. **Unoptimized design:** render the full-density design domain with protected solids and mandatory voids visually distinct.
3. **Optimization progression:** render the initial domain, at least three intermediate checkpoints, the converged BESO result, the smoothed reconstruction, and the interface-restored printable body.
4. **Before/after comparison:** place the full-density design and final printable body side by side at identical scale and view. Report volume and mass change.
5. **Convergence plots:** plot iteration against volume fraction and compliance. Also plot maximum displacement and the robust FoS metric when computed per iteration.
6. **Final FEA:** show undeformed and deformed views plus stress or directional-FoS hotspots for every release load case. Include legend, units, deformation scale, mesh size, and the reported peak and robust metric.
7. **Printable geometry:** show isometric, front, side, and section views that expose bosses, holes, insert bores, ligaments, ribs, contact planes, and tool access.
8. **Slicer evidence:** show build orientation, supports, first supported layers, hole perimeters, wall count, infill, and estimated mass/time from the declared profile.
9. **Physical evidence when printed:** photograph the finished part, interfaces, installed inserts, screw/tool access, mounted load, and any proof-load or failure inspection. Label physical photos separately from renders.

If a stage has not been run, mark its image as unavailable; do not imply that a render, simulation, or physical test exists.

## Optimization checkpoint selection

Prefer material-fraction checkpoints because iteration counts change with tuning. Capture approximately:

- 100% material: full design domain;
- 80% material: early removal;
- 60% material: main load paths emerging;
- 40-50% material: near target, or the nearest passing fraction;
- converged topology: final BESO state;
- reconstructed topology: smoothed surface before interface restoration;
- printable topology: final restored STL.

When the target fraction is higher than a listed checkpoint, choose three evenly spaced states between 100% and the target. Include the iteration number, material fraction, compliance, maximum displacement, and robust FoS in each caption.

## Comparison rules

- Use the same orthographic camera, orientation, crop, scale, resolution, background, and lighting for all geometry checkpoints.
- Keep material color consistent. Use a separate fixed color for protected regions and a consistent legend for density or stress.
- Do not auto-fit each frame independently; changing scale can make material removal look misleading.
- Show at least one section or transparent view when internal voids or disconnected shells could be hidden.
- For symmetric designs, include a front or section view aligned to the symmetry plane and report mirror deviation.
- Do not compare FEA contours with different automatic color ranges without stating the range change.
- Show load arrows on the undeformed model, not only in a separate table.

## Minimum user-facing evidence board

Before calling the STL printable, show these composites in the response:

- load and restraint map;
- fixed-view optimization progression strip;
- full-density versus final printable before/after view;
- final FEA hotspot board for all load cases;
- slicer orientation and support preview.

Link the full-resolution files and keep a compact evidence index containing the image path, stage, iteration, material fraction, load case, solver or slicer configuration, and generating artifact revision.
