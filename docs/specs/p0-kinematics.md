# P0 kinematics — specification

**Status:** accepted for implementation
**Version:** 0.1
**Date:** 2026-07-20

## 1. Problem

Build an authoritative, testable Python model of the position kinematics of a
symmetric three-degree-of-freedom rotary delta robot. Given the moving-platform
center, inverse kinematics (IK) shall calculate the three actuated shoulder
angles. Given those angles, forward kinematics (FK) shall calculate admissible
platform-center position candidates.

The first model exists to validate geometry and produce poses for the Three.js
visualizer. It does not yet plan time-parametrized motion or calculate forces.

## 2. Scope

Included:

- a symmetric 3-RUU rotary delta reduced to three center-line lower links,
- a translating platform whose orientation remains parallel to the base,
- explicit geometry, coordinate and angle conventions,
- IK and FK position solutions,
- joint-limit, unreachable, degenerate and ambiguous-result handling,
- joint and platform attachment points needed by the visualizer,
- independent numerical reference cases,
- property-based and sampled numerical validation.

Excluded:

- velocity, Jacobian, singularity-condition and dynamic calculations,
- compliance, backlash, parallelogram width and collisions between physical rods,
- motor steps, homing, calibration and controller integration,
- ROS2, Gazebo and hardware communication,
- trajectory timing and motor sizing.

These exclusions belong to later P0 slices or P1.

## 3. Mechanism narrative

Three motors are mounted 120 degrees apart in one horizontal base plane. Each
motor rotates one upper arm in a vertical radial plane. A parallelogram pair of
lower rods connects each upper-arm knee to the moving platform. The three
parallelograms constrain the platform to translate without rotating.

For position kinematics, each parallelogram pair is initially represented by one
virtual lower link of constant length. The visualizer may render both rods, but
their shared center-line constraint is the source of truth for P0 mathematics.

## 4. Coordinate system

The base frame `{B}` is right-handed:

```text
Top view (+Z looking toward the origin)

                    +Y
                     ^
                     |
              arm 3  |  arm 2
                  \  |  /
                   \ | /
        -X <---------O---------> +X
                     |
                     |
                   arm 1
                     |
                     v
                    -Y

Side view

                 base plane Z = 0
          ----------------------------
                         |
                         | normal workspace
                         v
                        -Z
```

- Origin: center of the fixed base joint triangle.
- `+X`: right in the top-view diagram.
- `+Y`: away from arm 1 in the top-view diagram.
- `+Z`: upward from the fixed base.
- Normal platform positions have `z < 0`.
- Platform position `(x, y, z)` refers to its geometric center.
- Platform orientation is identical to base orientation.

## 5. Arm numbering and attachment points

Let `r_b` be the base shoulder-joint radius and `r_p` the platform attachment
radius. Both describe the distance from their triangle center to one modeled
joint point.

The radial azimuths are:

| Arm | Azimuth | Unit radial vector `(rx, ry, 0)` |
|---|---:|---|
| 1 | `-90°` | `(0, -1, 0)` |
| 2 | `+30°` | `(sqrt(3)/2, 1/2, 0)` |
| 3 | `+150°` | `(-sqrt(3)/2, 1/2, 0)` |

The base shoulder point for arm `i` is `B_i = r_b * radial_i`. The corresponding
platform attachment point in platform-local coordinates is
`P_i_local = r_p * radial_i`.

This radius-based interface avoids ambiguity between triangle side length,
inradius and circumradius. Adapters from source dimensions must show their
conversion explicitly.

## 6. Joint-angle convention

- Joint order is `(theta_1, theta_2, theta_3)`.
- `theta_i = 0` means the upper arm is horizontal and points radially outward
  from shoulder `B_i`.
- Positive `theta_i` rotates that upper arm toward `-Z`.
- Internal angles are radians.
- Human-facing reports may show degrees, clearly labelled.
- P0's supported physical branch is `knee_out_platform_below`.
- Alternative IK roots must not be selected silently.

## 7. Geometry contract

The kinematic geometry shall contain:

| Field | Unit | Constraint | Meaning |
|---|---|---|---|
| `base_joint_radius_m` | m | `> 0` | Base center to each actuated shoulder axis |
| `platform_joint_radius_m` | m | `> 0` | Platform center to each virtual lower-link attachment |
| `upper_arm_length_m` | m | `> 0` | Shoulder to knee |
| `lower_arm_length_m` | m | `> 0` | Knee to platform attachment, measured on center line |
| `min_joint_angle_rad` | rad | `< max` | Lower accepted shoulder-angle limit |
| `max_joint_angle_rad` | rad | `> min` | Upper accepted shoulder-angle limit |

P0 does not yet freeze the DIY robot's values. Geometry from the independent
reference below is a validation fixture, not the design selected for purchase.

## 8. API behavior

### Inverse kinematics

Input:

- validated geometry,
- platform-center `CartesianPosition`,
- explicit assembly mode.

Output:

- one `JointAngles` value for the requested supported branch,
- joint and knee points sufficient for diagnostic export.

IK must distinguish:

- position unreachable by link lengths,
- solution outside a joint limit,
- degenerate geometry,
- unsupported or ambiguous assembly branch.

### Forward kinematics

Input:

- validated geometry,
- `JointAngles`,
- explicit assembly mode.

Output:

- platform-center candidate consistent with the requested branch,
- attachment and knee points sufficient for diagnostic export.

The mathematical sphere intersection can yield more than one position. P0 may
return all candidates before assembly-mode filtering, but it must not silently
discard ambiguity. For the supported branch, the accepted platform is below the
base (`z < 0`).

### Error model

Expected geometric failures shall use domain-specific exceptions or typed
results, not `None`, NaN values, clipping or unlabelled `ValueError` exceptions.
Exact class names will be fixed with the first implementation slice.

## 9. Numerical policy

- Calculations use Python double-precision floats.
- SI units are used internally: metres and radians.
- Numerical tolerances are named constants with a stated purpose.
- A value within a tolerance of a boundary is reported as such; it is not moved
  inside the valid region by clipping.
- P0 gate for sampled `IK -> FK` position error is `< 1e-5 m` (0.01 mm) for at
  least 10,000 valid sampled positions.
- Reports must include maximum and 99th-percentile error, not only the mean.

## 10. Independent reference oracle

Primary external reference for P0:

Robert L. Williams II, *The Delta Parallel Robot: Kinematics Solutions*, Ohio
University, 2016: <https://sites.ohio.edu/williams/html/PDF/DeltaKin.pdf>

The paper defines a revolute-input delta and publishes cross-checked IK and FK
examples. Its fixture uses:

| Source parameter | Value |
|---|---:|
| Base triangle side `s_B` | 0.567 m |
| Platform triangle side `s_P` | 0.076 m |
| Upper arm `L` | 0.524 m |
| Lower arm `l` | 1.244 m |

For the paper's joint geometry:

- `base_joint_radius_m = s_B / (2 * sqrt(3))`,
- `platform_joint_radius_m = s_P / sqrt(3)`.

The following rounded examples shall become tests using tolerances reflecting
the source's displayed precision:

| Direction | Input | Expected output |
|---|---|---|
| IK | `(0, 0, -0.900) m` | `(-20.5°, -20.5°, -20.5°)` |
| IK | `(0.300, 0.500, -1.100) m` | `(47.5°, -11.6°, 21.4°)` |
| FK | `(0°, 0°, 0°)` | `(0, 0, -1.065) m` |
| FK | `(10°, 20°, 30°)` | `(0.108, -0.180, -1.244) m` |

Before implementing formulas, the first test slice must document whether any
adapter is required between the paper's triangle notation and this radius-based
contract. The adapter itself must be independently tested.

## 11. Additional test properties

The future implementation must cover:

1. Equal angles produce a centered platform (`x ≈ 0`, `y ≈ 0`).
2. A centered reachable platform produces three equal angles.
3. Rotating a valid position by 120 degrees cyclically permutes the arm angles.
4. Returned knee-to-platform distances equal `lower_arm_length_m` within the
   named closure tolerance.
5. Returned shoulder-to-knee distances equal `upper_arm_length_m`.
6. Positions outside link reach are rejected explicitly.
7. Solutions outside joint limits are distinguished from geometric
   unreachability.
8. Sampled valid positions meet the HLD round-trip error gate.
9. The equal-knee-height FK case is handled without division by zero.
10. Inputs do not produce silent NaN or infinite outputs.

## 12. Visualizer contract

The Python export used later by Three.js shall include:

- schema version,
- geometry parameters and units,
- platform center,
- three shoulder points,
- three knee points,
- three platform attachment center-lines,
- three joint angles,
- reachability/limit state,
- assembly mode.

Rendering may map axes to Three.js display conventions, but the JSON values stay
in the base frame defined here.

## 13. Acceptance criteria for this specification slice

This specification slice is complete when:

- coordinate, arm and angle conventions are unambiguous,
- the external Williams examples are recorded as an independent oracle,
- the Python project exposes typed SI position, angle and assembly-mode values,
- Ruff, Mypy, Pytest and at least one Hypothesis test run successfully,
- no FK or IK implementation is claimed yet.

## 14. Known uncertainty

The reference dimensions were scaled by the paper's author from an ABB figure,
and its displayed results are rounded. They are suitable for convention and
formula validation at the stated precision, not for high-precision metrology.
Later validation should add a second independent implementation or derivation
before P0 is declared fully complete.
