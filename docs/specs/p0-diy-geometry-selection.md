# P0 DIY geometry screening — specification

**Status:** accepted for implementation
**Version:** 0.1
**Date:** 2026-07-20

## 1. Problem

The Williams dimensions validate mathematics but describe a much larger
commercial robot. P0 needs one buildable DIY geometry whose **entire useful
cylindrical workspace**, not merely selected points, covers the HLD target of
diameter 350–400 mm and height 150 mm with explicit joint-limit and singularity
reserve. The selection must precede trajectory timing, dynamics and purchases.

## 2. Candidate story

All candidates are symmetric rotary deltas intended for a private workshop.
Dimensions are joint-centre to joint-centre and remain provisional until a CAD
assembly checks real bearings, rod-pair spacing and collisions.

| Candidate | Base radius | Platform radius | Upper arm | Lower arm | Reason for inclusion |
|---|---:|---:|---:|---:|---|
| `compact_400` | 180 mm | 55 mm | 200 mm | 400 mm | Smallest envelope and lowest expected upper-arm inertia; uses the low end of the provisional 400–450 mm rod range. |
| `balanced_430` | 210 mm | 60 mm | 240 mm | 430 mm | Moderate increase in all dimensions; tests whether a conventional proportional scale reaches the target. |
| `reach_optimized_450` | 180 mm | 65 mm | 280 mm | 450 mm | Bounded parameter search found this combination can cover Ø400 mm while retaining the current maximum proposed lower-rod length. Its longer upper arm is an explicit dynamic cost to test in P1. |

All candidates use provisional inclusive shoulder limits `-45°..+80°`. This
125° range is mechanically plausible for an exposed workshop demonstrator and
contains the complete planned cycle, but it is not yet a purchased motor or
hard-stop specification. P0 additionally requires every useful point to remain
at least 5° from both limits so small calibration and construction errors do not
immediately invalidate the workspace.

## 3. Required cylinder

Candidate diameters are evaluated in descending preference:

1. 400 mm (top of HLD range),
2. 375 mm (mid-range fallback),
3. 350 mm (minimum HLD pass).

Height is always 150 mm. The cylinder is centred on model X=Y=0. Its vertical
centre is not assumed: the selector searches `z=-250..-550 mm` in 1 mm steps
and chooses the placement with the largest worst-case normalized reserve.

This range covers the plausible working depth of all candidates without
approaching the base plane. If no placement passes, that diameter fails.

## 4. Sampling and reserve

For each candidate, diameter and Z placement, sample a deterministic solid
cylinder using:

- 16 Z planes including both ends (10 mm spacing across 150 mm),
- 9 radial levels including centre and boundary,
- one centre sample and 72 azimuths on every nonzero radius (5° spacing).

This gives `16 × (1 + 8 × 72) = 9,232` evaluated poses per cylinder. Sampling is
evidence, not a mathematical proof of the continuous volume; the exact grid and
minimum location must be exported so CAD and later physical tests can target
the weakest pose.

A sampled pose passes only when:

- IK succeeds inside the configured limits,
- distance to the nearest joint limit is at least 5° on every arm,
- `singularity_margin >= 0.20`.

The 0.20 design threshold is deliberately stricter than the 0.15 visualization
warning threshold. It caps the normalized parallel condition number at 5 and
leaves 5 percentage points for interpolation between the coarse screening
samples. It is still a provisional project choice, not a safety standard.

For a complete passing cylinder define:

```text
joint_reserve_ratio = minimum_joint_limit_margin / 5°
singularity_reserve_ratio = minimum_singularity_margin / 0.20
overall_reserve_ratio = min(joint_reserve_ratio, singularity_reserve_ratio)
```

For each diameter the selector chooses the Z centre with maximum
`overall_reserve_ratio`. The project selects the smallest candidate that passes
the largest diameter. If candidates pass the same largest diameter, prefer:

1. larger overall reserve,
2. shorter upper arm (lower expected moving inertia),
3. shorter lower arm (smaller frame envelope).

## 5. Outputs

`artifacts/geometry_comparison.json` shall contain:

- schema `delta-robot-p0-geometry-comparison/v1`,
- all exact candidate dimensions and limits,
- sampling definition and thresholds,
- best placement and minimum margins for each candidate/diameter,
- pass/fail plus a diagnostic reason,
- selected candidate and explicit selection rationale,
- the weakest sampled position for the selected cylinder.

The selected `DeltaGeometry`, source label, useful cylinder and nominal pose
shall live in a typed Python module. Workspace and subsequent trajectory
artifacts must import that configuration rather than repeat dimensions.

## 6. Walk-through

1. Start at the top centre of the cylinder and solve IK/margins.
2. Move radially through all sampled rings; at each ring rotate through 360°.
3. Repeat down through all 16 planes. One failure rejects that placement.
4. Shift the full cylinder 1 mm in Z and repeat until all placements are tested.
5. Retain the placement whose weakest point has the best combined reserve.
6. Repeat for Ø400, Ø375 and Ø350 and for all candidates.
7. Select by the deterministic rule above; export its weakest pose so a reviewer
   can inspect the exact limiting configuration.
8. Generate the dense visualizer workspace around the selected geometry. Green,
   purple, orange and red points remain results from Python, not JS formulas.

## 7. Acceptance

- Every reported passing cylinder contains exactly 9,232 passing samples.
- Re-evaluating the exported weakest point reproduces both reported minima to
  `<1e-12`.
- Rotating each sampled XY point by 120° and cyclically permuting arms preserves
  pass/fail and singularity margin to `<1e-12` for targeted property tests.
- The selected candidate passes at least Ø350×150 mm with
  `singularity_margin >= 0.20` and 5° joint reserve everywhere sampled.
- The selector is deterministic and regenerates byte-identical JSON.
- The report states that collision clearance, stiffness, bearing angles and
  dynamic adequacy remain unverified; selection does not authorize purchases.

## 8. Explicit uncertainties

- The virtual-link model does not check collision between paired rods, upper
  arms, platform, base plate or tooling.
- Actual universal/spherical joint articulation may be smaller than the
  kinematic range.
- Carbon-tube bending and upper-arm torsional stiffness are not yet modelled.
- The 1 mm / 5° / 10 mm sampling lattice cannot prove behavior between points.
- `reach_optimized_450` may win kinematically but lose dynamically because its
  280 mm upper arms carry more inertia. P1 must quantify this before BOM freeze.

