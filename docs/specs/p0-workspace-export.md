# P0 workspace sampling and visualizer export — specification

**Status:** accepted for implementation  
**Version:** 0.1  
**Date:** 2026-07-20

## 1. Problem

The validated position-kinematics model can solve one requested pose, but it
cannot yet show where the robot can move or provide a stable data contract to a
Three.js visualizer. This slice shall sample a finite Cartesian grid, classify
every point without hiding solver failures, and export both the sampled map and
one complete robot pose as deterministic JSON.

This map is a **geometric and joint-limit workspace**, not yet the useful
workspace promised by the HLD. The latter also needs Jacobian/singularity,
collision and later dynamic margins.

## 2. Inputs and outputs

Inputs:

- one validated `DeltaGeometry`,
- the explicit `knee_out_platform_below` assembly mode,
- inclusive Cartesian bounds in metres,
- a positive integer sample count for each X, Y and Z axis,
- for a pose export, one platform-center position in metres.

Outputs:

- an immutable, deterministically ordered workspace sample,
- one classification and one reason for every sampled point,
- counts for all classifications,
- a versioned workspace JSON document,
- a versioned pose JSON document containing geometry and all visible joints.

All model values remain in the base frame and SI units fixed by
`p0-kinematics.md`.

## 3. Workspace classification

The public classification is deliberately small enough to color directly in a
visualizer:

| Classification | Meaning |
|---|---|
| `reachable` | IK closes all three arms on the supported branch and all angles are inside the configured inclusive limits. |
| `joint_limited` | The point is reachable on the supported geometric branch, but at least one solved angle is outside the configured limits. |
| `unreachable` | The point has no accepted geometric solution on the supported branch. |

Each point also carries one of these diagnostic reasons:

| Reason | Classification | Source |
|---|---|---|
| `reachable` | `reachable` | IK succeeded. |
| `joint_limit` | `joint_limited` | Limited IK failed, then the same point succeeded with non-restrictive validation limits. |
| `geometric_unreachable` | `unreachable` | Link geometry cannot close. |
| `degenerate_boundary` | `unreachable` | The point is on a collapsed or tangent numerical/geometric boundary. |
| `assembly_constraint` | `unreachable` | The point violates the requested platform-below assembly branch. |
| `ambiguous_assembly` | `unreachable` | The branch rule cannot select exactly one IK root. |

Classification shall not depend on which arm happens to be evaluated first. If
normal IK reports `JointLimitError`, the classifier shall retry the same point
with a copy of the geometry whose validation limits are `[-pi, +pi]`. The
supported knee-out root necessarily lies strictly inside `(-pi/2, +pi/2)`, so
these retry limits remove the configured actuator restriction without changing
link geometry or branch selection. Only a successful retry is
`joint_limited`; a geometric failure during retry is `unreachable` with its
actual reason.

Invalid non-finite positions, invalid grid definitions and unsupported assembly
modes are caller/configuration errors and shall be raised rather than converted
to colored workspace points.

## 4. Grid contract and deterministic order

Each axis has an inclusive minimum, inclusive maximum and sample count:

- bounds must be finite and `minimum <= maximum`,
- counts must be integers (not booleans) and at least one,
- count `1` samples the midpoint of the interval,
- count greater than one samples both endpoints at uniform spacing,
- a zero-width interval may only have count `1`.

Points are emitted in nested `Z -> Y -> X` traversal with X changing fastest.
This order is stable but does not imply a physical scan trajectory. The summary
counts must add exactly to `x_count * y_count * z_count`.

## 5. JSON boundary

JSON serialization is a boundary adapter only; it shall contain no kinematic
formula. Documents use sorted keys, a trailing newline, finite JSON numbers and
these schema identifiers:

- `delta-robot-p0-workspace/v1`,
- `delta-robot-p0-pose/v1`.

Both documents contain:

- schema identifier,
- explicit `{length: "m", angle: "rad"}` units,
- assembly mode,
- all six geometry fields with unit-bearing names,
- a source label supplied by the generator so a reference fixture cannot be
  mistaken for frozen DIY geometry.

The workspace document additionally contains:

- grid bounds and shape,
- classification counts,
- ordered points as `{position_m: [x, y, z], classification, reason}`.

The pose document additionally contains:

- platform center,
- three joint angles,
- for each arm: arm index, shoulder, knee and platform attachment point.

An unreachable pose request raises the existing typed IK error and does not
write a partial pose document. Three.js may remap axes for display, but must not
recompute joints or solve kinematics.

## 6. Reference artifacts

Until DIY dimensions are selected, the reproducible demo uses the clearly
labelled Williams validation fixture, not a hardware proposal:

- workspace bounds: `x,y = [-0.45, +0.45] m`, `z = [-1.45, -0.55] m`,
- workspace shape: `21 x 21 x 21 = 9,261` points,
- pose: platform center `(0, 0, -0.900) m`,
- source label: `williams_validation_fixture_not_diy_geometry`.

The equal axis counts make the first artifact easy to inspect and give a coarse
46.8 million cubic-millimetre voxel scale (`45 mm` per axis). It is a visual
map, not a boundary-accuracy claim. Finer or adaptive boundary sampling belongs
to a later slice if it materially helps select the DIY geometry.

## 7. Walk-through

1. The generator constructs the published Williams geometry and the grid.
2. Python visits each finite point in deterministic order.
3. Normal IK either returns angles, reports a configured joint limit, or gives
   a geometric/branch failure.
4. A joint-limit result is retried without the configured actuator restriction
   to separate limited from truly unreachable space.
5. Counts are checked against the exact grid cardinality.
6. Python writes the versioned workspace map.
7. Python solves the selected centered pose and writes the complete visible
   arm geometry.
8. Three.js can color the map and draw that pose directly from JSON without
   implementing a second kinematic model.

## 8. Acceptance tests

This slice is complete when:

1. A known Williams point is classified `reachable` and contains finite angles.
2. The same geometric point under deliberately narrow limits is classified
   `joint_limited` rather than unreachable.
3. A point outside link reach and a point above the base are `unreachable` with
   distinct reasons.
4. Invalid bounds, invalid counts and non-finite point input are rejected.
5. A small grid proves inclusive endpoints, midpoint behavior, X-fastest order,
   exact cardinality and exact summary counts.
6. Workspace and pose dictionaries match their versioned schemas and serialize
   with strict finite JSON numbers.
7. The exported pose preserves the IK result and both upper- and lower-link
   closure within the kinematic numerical policy.
8. Running the reference generator twice produces byte-identical files.
9. The committed reference artifacts regenerate without a diff.
10. Ruff, strict Mypy and Pytest pass.

## 9. Known uncertainty

- No Jacobian or singularity-distance metric exists yet, so `reachable` must
  not be presented as safe, fast or useful throughout the cell.
- The reduced center-line lower-link model does not detect rod, platform or
  frame collisions.
- Uniform sampling can miss a thin boundary feature between points.
- The Williams fixture validates software behavior but says nothing about the
  final DIY dimensions or motor choice.
