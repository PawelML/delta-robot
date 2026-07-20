# P0 kinematics — specification

**Status:** accepted for implementation
**Version:** 0.4
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

#### 8.1 One-arm inverse geometry and complete IK slice

For arm `i`, let `r_i = (r_x, r_y, 0)` be its outward radial unit vector
from section 5 and let `t_i = (-r_y, r_x, 0)` be the in-plane tangent. The
shoulder and platform-attachment points are:

- `B_i = r_b * r_i`,
- `Q_i = (x, y, z) + r_p * r_i`.

Relative to the shoulder, the target attachment has components:

- `d_r = x*r_x + y*r_y + r_p - r_b`,
- `d_t = -x*r_y + y*r_x`,
- `d_z = z`.

The upper-arm knee is constrained to the radial motor plane:

`A_i = B_i + L*cos(theta_i)*r_i + (0, 0, -L*sin(theta_i))`.

Enforcing `|Q_i - A_i| = l` gives one scalar equation per arm:

```text
E*cos(theta_i) + F*sin(theta_i) + G = 0

E = -2*L*d_r
F =  2*L*z
G = d_r^2 + d_t^2 + z^2 + L^2 - l^2
```

The solver shall obtain both mathematical roots using the phase form of this
equation. For `knee_out_platform_below`, exactly one root must satisfy
`L*cos(theta_i) > 0`, meaning the knee lies radially outward from its shoulder.
Zero or multiple outward roots are reported as an ambiguous/degenerate branch;
the solver does not select a root by array order.

The public `inverse_kinematics` result shall contain the three angles plus, for
each arm, the shoulder, knee and platform-attachment points in the base frame.
The one-arm function remains independently testable and pure.

This slice fixes the initial IK error model:

| Error | Meaning |
|---|---|
| `InvalidPositionError` | An XYZ input is NaN or infinite |
| `UnreachablePositionError` | At least one arm's circle and sphere do not intersect |
| `DegeneratePositionError` | The phase equation or its roots collapse at a numerical/geometric boundary |
| `AmbiguousAssemblyError` | The requested knee-out rule does not identify exactly one root |
| `AssemblyConstraintError` | The platform is not below the base as required by the selected mode |
| `JointLimitError` | The selected geometric solution lies outside an inclusive joint limit |
| `UnsupportedAssemblyModeError` | A mode other than the implemented branch is requested at runtime |

Feasibility is decided from the discriminant `E^2 + F^2 - G^2`. A relative
comparison tolerance of `64 * sys.float_info.epsilon` is used only to classify
a value indistinguishable from zero as a degenerate boundary. It is not used to
clip a negative discriminant or move an angle inside a joint limit.

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

#### 8.2 Three-sphere intersection and complete FK slice

For known shoulder angles, the three knee points `A_i` follow directly from
the upper-arm geometry in section 8.1. Because the moving platform remains
parallel to the base, subtracting each platform-local attachment offset creates
three virtual sphere centers:

`C_i = A_i - r_p * r_i`.

The unknown platform center must lie exactly `l` metres from every `C_i`.
Complete FK is therefore the intersection of three equal-radius spheres.

The implementation shall use coordinate-free trilateration:

1. Build an orthonormal basis from `C_1`, `C_2` and `C_3`.
2. Solve the in-plane coordinates by subtracting the sphere equations.
3. Solve the remaining perpendicular coordinate from the first sphere.
4. Return both mathematical candidates when two intersections exist.
5. For `knee_out_platform_below`, accept exactly one candidate with `z < 0`.

This algorithm deliberately handles equal and unequal knee heights through one
path. It avoids the division-by-zero problem of the general component-wise
algorithm described in Williams Appendix A when all three centers share a
height; it is mathematically equivalent to sphere intersection, not a second
delta-specific kinematic formula.

The public `forward_kinematics` result shall contain:

- the selected platform-center position,
- all mathematical sphere-intersection candidates,
- the input joint angles,
- each arm's shoulder, knee, virtual sphere center and selected platform
  attachment point.

Inputs must be finite, inside inclusive joint limits and consistent with the
requested knee-out branch (`L*cos(theta_i) > 0`). Expected failures are:

| Error | Meaning |
|---|---|
| `InvalidAnglesError` | At least one input angle is NaN or infinite |
| `UnreachableAnglesError` | The three lower-link spheres have no common point |
| `DegenerateSphereGeometryError` | Sphere centers are coincident/collinear or meet tangentially within numerical resolution |
| `AmbiguousForwardSolutionError` | The below-base rule identifies zero or multiple admissible candidates |

Shared `JointLimitError`, `AssemblyConstraintError` and
`UnsupportedAssemblyModeError` retain the meanings fixed for IK. Relative
geometric comparisons use `64 * sys.float_info.epsilon` scaled by the relevant
length or squared-length magnitude. Values classified as a boundary are
reported, never clipped into a valid sphere intersection or assembly branch.

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

### 10.1 Williams adapter and reference-fixture slice

The paper describes both triangles by side length, while the authoritative P0
geometry describes the modeled joint locations by center-to-joint radius. A
small boundary adapter is therefore required. It shall:

- accept `s_B`, `s_P`, `L`, `l` in metres and explicit joint limits in radians,
- return the radius-based geometry contract from section 7,
- calculate `r_b = s_B / (2 * sqrt(3))` and `r_p = s_P / sqrt(3)`,
- copy `L` and `l` without scaling,
- reject non-finite or non-positive lengths and invalid joint-limit ordering,
- contain no IK or FK formula.

The four published examples shall be stored as typed, immutable SI fixtures.
Their displayed precision and the precision of the published input dimensions
define the solver-test tolerances:

- angles displayed to `0.1 deg`: absolute tolerance
  `0.05 deg + 1e-12 rad`,
- positions displayed to `0.001 m`: absolute tolerance `0.001649554077 m`.
  This is the zero-angle fixture's worst-case `0.001149554076 m` displacement
  over all corners formed by varying each of `s_B`, `s_P`, `L` and `l` by
  `+/-0.0005 m`, plus the output's `0.0005 m` half-resolution and `1e-12 m`
  floating-point boundary slack.

The `1e-12` additions cover only floating-point boundary representation. The
larger FK tolerance accounts for uncertainty already present in the rounded
source dimensions; it is not a numerical allowance for the solver. The
Williams paper does not publish
joint limits, so its shared validation fixture uses explicit non-restrictive
test limits `[-pi, +pi]`. These limits are not a DIY robot design decision.

In this slice, tests verify the adapter independently against precomputed radii
and verify exact transcription, units and tolerances of all four fixtures. The
fixtures become executable IK/FK oracle tests as soon as the corresponding
solver is added. Until then, passing fixture tests is not evidence that any
kinematic formula is correct.

### AI-assisted implementation note

- The initial `0.0005 m` FK tolerance, based only on displayed output precision,
  rejected the zero-angle oracle by `0.000048344 m` beyond that interval.
- Exhaustively evaluating all 16 corners of the four published `1 mm` dimension
  intervals showed up to `0.001149554076 m` movement in the expected zero-angle
  result.
- The reference tolerance now includes that source-data uncertainty. The model
  formula and solver tolerances were not altered to make the test pass.

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
- the Williams side-length adapter is tested against independently precomputed
  radius values,
- all four published examples are available as typed SI fixtures with
  source-precision tolerances,
- the Python project exposes typed SI position, angle and assembly-mode values,
- both Williams IK cases pass as executable solver tests within their published
  `0.1 deg` precision,
- returned diagnostic points close both upper- and lower-link lengths,
- centered-position equality, 120-degree cyclic symmetry, unreachable input,
  non-finite input and joint-limit rejection are tested,
- both Williams FK cases pass as executable solver tests within the
  source-uncertainty tolerance derived in section 10.1, including the
  equal-knee-height case,
- a deterministic sample of 10,000 valid Williams-fixture positions in
  `x,y in [-0.1, 0.1] m`, `z in [-1.15, -0.85] m` passes `IK -> FK` below
  `1e-5 m`, reporting maximum and 99th-percentile position error; this validates
  the numerical pipeline but does not freeze the DIY robot geometry,
- Ruff, Mypy, Pytest and at least one Hypothesis test run successfully,
- IK and FK position solutions are implemented; Jacobian, workspace boundary
  generation and singularity metrics remain later P0 slices.

## 14. Known uncertainty

The reference dimensions were scaled by the paper's author from an ABB figure,
and its displayed results are rounded. They are suitable for convention and
formula validation at the stated precision, not for high-precision metrology.
Later validation should add a second independent implementation or derivation
before P0 is declared fully complete.
