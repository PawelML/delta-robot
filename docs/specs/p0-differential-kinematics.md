# P0 differential kinematics and singularity margin — specification

**Status:** accepted for implementation
**Version:** 0.1
**Date:** 2026-07-20

## 1. Problem

Position kinematics says whether the platform can occupy one XYZ point, but it
does not say how rapidly the three motors must move there or whether the robot
is close to losing controllability. This slice shall differentiate the three
constant-lower-link constraints, expose both velocity mappings and attach a
dimensionless singularity margin to every geometrically solved workspace point.

The existing public workspace classes remain exactly `reachable`,
`joint_limited` and `unreachable`. Singularity quality is an additional field,
not a fourth reachability class.

## 2. Mechanism narrative

At every solved pose each virtual lower link is a rigid vector from a knee to a
platform attachment. A tiny platform motion changes all three vectors. Each
motor must rotate its upper arm just enough that the component of this change
along its lower link remains zero; otherwise the rigid link would have to grow
or shrink.

Normally the three link constraints determine one motor-speed vector for one
platform velocity and vice versa. Near a singularity this conversion becomes
poorly conditioned:

- a **parallel singularity** occurs when the three lower-link directions stop
  constraining three independent Cartesian directions;
- a **serial singularity** occurs when one upper arm moves locally at right
  angles to the constraint direction, so that motor cannot efficiently change
  its lower-link constraint.

The UI shall make these weak but still geometrically reachable areas visible.

## 3. Inputs, outputs and units

Inputs:

- validated `DeltaGeometry` in metres and radians,
- one platform-center `CartesianPosition` in metres,
- the supported `knee_out_platform_below` assembly mode,
- optionally a Cartesian velocity in m/s or joint velocity in rad/s.

Outputs:

- the solved IK pose and its three lower-link vectors,
- Cartesian constraint matrix `J_x` with dimensionless rows,
- joint constraint diagonal `J_theta` in metres,
- `joint_rates_for_cartesian_velocity` in rad/s,
- `cartesian_velocity_for_joint_rates` in m/s,
- dimensionless parallel, serial and combined singularity margins.

All matrices use row/column order `(arm 1, arm 2, arm 3)` and Cartesian column
order `(x, y, z)`.

## 4. Differential constraint

For arm `i`, let:

- `Q_i` be its platform attachment,
- `A_i(theta_i)` be its knee,
- `u_i = Q_i - A_i` be its lower-link vector of length `l`,
- `r_i` be the arm's horizontal radial unit vector,
- `L` be the upper-arm length.

The position constraint is `u_i · u_i = l²`. Its time derivative gives:

```text
u_i · (p_dot - A'_i(theta_i) * theta_dot_i) = 0

A'_i(theta_i) = -L*sin(theta_i)*r_i + (0, 0, -L*cos(theta_i))
```

After dividing each row by `l`:

```text
J_x * p_dot = J_theta * theta_dot

row_i(J_x) = u_i / l
diag_i(J_theta) = (u_i · A'_i) / l
```

This is the coordinate-free equivalent of the revolute-input velocity equation
`A X_dot = B Theta_dot` in Williams (2016), page 15. The source's geometry and
axis labels differ, so validation shall compare differentiated constraints and
finite-difference IK rather than copying its component expressions.

## 5. Singularity metrics

The following metrics are dimensionless and range from zero to one apart from
floating-point round-off:

### 5.1 Parallel margin

Normalize every lower-link vector to form `J_x`. Let its singular values be
`sigma_max >= sigma_mid >= sigma_min >= 0`:

`parallel_margin = sigma_min / sigma_max`.

It is zero at rank loss and one for an ideally conditioned isotropic matrix.
The ratio is preferred over a determinant because it has a direct condition
number interpretation and is comparable between geometries.

### 5.2 Serial margin

For each arm:

`serial_margin_i = abs(u_i · A'_i) / (l * L)`.

The aggregate `serial_margin` is the minimum of the three values. It is zero at
a serial singularity and one at the best possible alignment of the two vectors.

### 5.3 Combined margin and provisional useful threshold

`singularity_margin = min(parallel_margin, serial_margin)`.

For P0 visualization and geometry screening only:

- `singularity_margin >= 0.15` is provisionally **usable**;
- `singularity_margin < 0.15` is **weak / practically unusable**.

The value `0.15` means neither normalized mechanism has less than 15% of its
best directional leverage, and the normalized parallel condition number is no
worse than about `1 / 0.15 = 6.67`. It is a conservative engineering screening
rule, not a safety limit or a published industry standard. P1/P2 measurements
may change it; the raw metrics must therefore always be exported.

Metrics are calculated for both `reachable` and `joint_limited` points when IK
has a geometric solution. `unreachable` points carry JSON `null` margins.

## 6. Failure behavior

- Existing position, branch and joint-limit errors retain their meaning.
- Non-finite velocity inputs are rejected explicitly.
- Velocity conversion raises a dedicated singularity error when its required
  matrix is rank-deficient at numerical resolution; it does not clip a margin
  or return infinities.
- A very small but nonzero margin is reported honestly. The visualization
  threshold does not make the mathematical solver fail.
- SVD and linear solves use IEEE-754 double precision through NumPy. The
  singular solve threshold is `64 * machine epsilon * sigma_max` for `J_x` and
  the corresponding scale for the diagonal `J_theta`.

## 7. Workspace JSON v2

The workspace schema advances to `delta-robot-p0-workspace/v2`; pose v1 remains
unchanged in this slice. Every workspace point gains:

```json
{
  "parallel_margin": 0.0,
  "serial_margin": 0.0,
  "singularity_margin": 0.0,
  "practically_usable": false
}
```

All four values are `null` for `unreachable` points. `practically_usable` is
false for `joint_limited` points even if their singularity margin passes,
because the configured actuator limits still exclude them. The summary gains
`practically_usable` and `weak_reachable` counts. The old three class counts and
their meanings do not change.

## 8. Walk-through

1. At a central pose, IK supplies three symmetric lower-link vectors. `J_x` is
   full rank, all three joint-diagonal terms are nonzero, and both velocity
   conversions succeed.
2. A requested small +X velocity produces three joint speeds. Advancing XYZ by
   a small time step and rerunning IK yields the same speeds to finite-difference
   accuracy.
3. Moving toward a parallel singularity makes two or more normalized constraint
   directions dependent. `parallel_margin` tends toward zero and Cartesian
   velocity from joint rates becomes ill-conditioned.
4. Moving toward one arm's serial singularity makes `u_i · A'_i` tend toward
   zero. `serial_margin` tends toward zero and that motor's required velocity
   for Cartesian motion grows.
5. Workspace sampling retains `reachable`, but v2 marks a reachable point below
   0.15 as `practically_usable: false`. Three.js can therefore display it as a
   warning shell without independently evaluating a formula.

## 9. Acceptance evidence

- The analytical joint-rate mapping agrees with central finite-difference IK
  over at least 10,000 valid, non-weak random poses and velocity directions:
  maximum absolute error `< 1e-5 rad/s` and 99th percentile `< 1e-6 rad/s` for
  velocities up to `0.25 m/s`.
- Substitution of either velocity mapping into `J_x*p_dot -
  J_theta*theta_dot` leaves maximum absolute residual `< 1e-10 m/s`.
- At symmetric center poses, cyclic arm symmetry is preserved to `< 1e-12`.
- Scaling every robot length and Cartesian coordinate by the same positive
  factor leaves all three singularity margins unchanged to `< 1e-12`.
- Property-based tests cover finite inputs, symmetry and metric ranges.
- Workspace v2 contract tests prove that all old classes/counts remain and that
  only solved points contain finite metrics.
- The visualizer uses exported booleans/margins and contains no Jacobian or
  singularity formula.

## 10. Source and uncertainty

Primary derivation cross-check: Robert L. Williams II, *The Delta Parallel
Robot: Kinematics Solutions*, Ohio University, 2016, especially the revolute
input constraint and velocity sections:
<https://sites.ohio.edu/williams/html/PDF/DeltaKin.pdf>.

The differential equation is independently supported by that publication and
finite-difference IK. The `0.15` useful threshold is not independently
validated. It remains a labelled P0 design assumption until dynamics and
physical measurements quantify tracking error, vibration and drive reserve.

