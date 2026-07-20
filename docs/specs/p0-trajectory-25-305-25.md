# P0 25-305-25 trajectory and export — specification

**Status:** accepted for implementation
**Version:** 0.1
**Date:** 2026-07-20

## 1. Problem

The selected geometry proves a static useful cylinder but drive sizing needs a
time-parametrized pick-and-place motion. P0 shall generate one reproducible
25-305-25 round trip containing Cartesian position, velocity and acceleration,
plus all three motor angles, rates and accelerations. Three.js shall animate
only exported joint points from this authoritative Python trajectory.

## 2. Cycle narrative

The tool starts 25 mm below transfer height over the source. It waits briefly,
lifts 25 mm, travels horizontally 305 mm, lowers 25 mm over the destination and
waits. It then lifts, returns and lowers to the source. The complete round trip
takes 1.000 s, representing the HLD baseline of one completed pick-and-place
cycle per second.

No gripper actuation is modelled yet. The two 50 ms dwells reserve time for a
future vacuum confirmation/release experiment; their adequacy is unverified.

```text
source                         destination
(-152.5 mm)                    (+152.5 mm)
     │ 25 mm up                    │ 25 mm down
     └──────── 305 mm ─────────────┘
                Z transfer = -372 mm
                Z low      = -397 mm
```

Both endpoints are centred in the selected Ø400×150 mm cylinder. `Y=0`. The low
plane is 25 mm below the selected cylinder centre (`-347 mm`) plus another
25 mm chosen to keep the complete cycle well inside the `-422..-272 mm`
screened Z bounds. This placement leaves room for later approach-height tests.

## 3. Segment schedule

| Segment | Duration | Start → end | Rationale |
|---|---:|---|---|
| source dwell | 0.050 s | source low → same | provisional future grip confirmation budget |
| lift | 0.100 s | source low → source transfer | separates the part before lateral motion |
| outbound transfer | 0.250 s | source transfer → destination transfer | longest move receives half of the moving time |
| lower | 0.100 s | destination transfer → destination low | symmetric with lift |
| destination dwell | 0.050 s | destination low → same | provisional future release budget |
| lift | 0.100 s | destination low → destination transfer | starts return |
| return transfer | 0.250 s | destination transfer → source transfer | symmetric return |
| lower | 0.100 s | source transfer → source low | closes the cycle |

Total is exactly 1.000 s. This schedule is a baseline load case, not yet an
optimized industrial cycle.

## 4. Cartesian motion law

Every moving segment uses the normalized minimum-jerk quintic:

```text
s(tau)   = 10*tau^3 - 15*tau^4 + 6*tau^5
s'(tau)  = 30*tau^2 - 60*tau^3 + 30*tau^4
s''(tau) = 60*tau - 180*tau^2 + 120*tau^3
tau = local_time / segment_duration
```

Position interpolates `start + s*(end-start)`. Velocity and acceleration use
the exact first and second derivatives divided by segment duration and its
square. Position, velocity and acceleration are continuous at segment joins;
jerk is finite but discontinuous. Dwell samples are constant zeros.

The export samples `t=0..1.000 s` inclusively every 1 ms: 1,001 samples. This is
fine enough for the first load estimate but does not prove unsampled peaks;
P1 shall compare it with a finer convergence run.

## 5. Joint velocity and acceleration

Joint rates use the accepted differential equation:

`J_x * p_dot = J_theta * theta_dot`.

Joint accelerations come from differentiating each rigid-link velocity
constraint. Let `w_i = p_dot - A'_i*theta_dot_i = u_dot_i` and:

`A''_i = -L*cos(theta_i)*r_i + (0, 0, L*sin(theta_i))`.

Then:

```text
(u_i · A'_i) * theta_ddot_i =
    (u_i · p_ddot)
  + (w_i · w_i)
  - (u_i · A''_i) * theta_dot_i^2
```

This uses the same serial-singularity rejection as joint-rate conversion. The
implementation exports rad/s and rad/s²; it does not numerically differentiate
the exported angle array.

## 6. JSON contract

`artifacts/trajectory_25_305_25.json` uses schema
`delta-robot-p0-trajectory/v1` and contains:

- geometry, assembly mode, SI units and source label,
- cycle definition and segment schedule,
- sample period, count and complete duration,
- for every sample: time, segment, XYZ, XYZ velocity, XYZ acceleration, three
  angles, three joint rates, three joint accelerations, singularity metrics,
- shoulder, knee and platform-attachment points for all three arms,
- summary extrema for Cartesian and joint speed/acceleration and minimum
  singularity margin.

The Three.js data adapter validates this schema and geometry against workspace
v2. JavaScript interpolates adjacent exported point coordinates for display; it
must not derive knees or solve IK from angles.

## 7. Failure behavior

- Any unreachable, joint-limited or below-0.20 trajectory sample aborts export.
- Non-finite results abort export; JSON never contains NaN or infinity.
- A sample inside 5° of either joint limit aborts export because it contradicts
  the selected useful-cylinder evidence.
- Singular velocity or acceleration conversion raises the existing dedicated
  differential error; it is not clipped.
- Exact segment-boundary samples may be assigned to either adjacent segment,
  but their numerical state must be identical and continuous.

## 8. Walk-through

1. At `t=0`, the platform is stationary at source low.
2. It remains stationary for 50 ms, then follows a smooth vertical lift.
3. At transfer height all Cartesian derivatives return to zero before the
   305 mm horizontal motion starts.
4. The same process lowers and dwells at the destination.
5. The reverse four segments return to the exact starting state at 1.000 s.
6. At every millisecond Python solves IK, Jacobian and joint acceleration, then
   exports all visible points.
7. Three.js advances through those samples, interpolates displayed points and
   updates the shown XYZ/angles; no kinematic formula exists in JS.

## 9. Acceptance evidence

- Exact source/destination horizontal separation is 0.305 m and lift/lower
  displacement is 0.025 m to `<1e-15 m`.
- The trajectory has 1,001 monotonically ordered samples from 0 to 1 s.
- Start and end position, velocity, acceleration, angles and joint rates match
  to `<1e-12`; all segment joins are C2 to `<1e-12`.
- Every sample passes IK, 5° joint reserve and singularity margin 0.20.
- Analytical joint rates agree with central-difference IK at interior moving
  samples to `<1e-5 rad/s`.
- Analytical joint accelerations agree with central differences of analytical
  joint rates at interior samples away from joins to `<1e-3 rad/s²`.
- Substitution into the differentiated acceleration constraint leaves maximum
  residual `<1e-9 m/s²`.
- JSON regeneration is byte-identical and its summary exactly matches extrema
  recomputed from samples.
- The visualizer's automated contract tests pass and a browser smoke test shows
  a connected robot throughout one complete loop.

## 10. Remaining uncertainty

The timing is an imposed 1 Hz load case, not a controller-feasible guarantee.
It ignores jerk limits, path blending, vacuum behavior, compliance, backlash,
collision clearance and motor torque-speed limits. P1 dynamics and the
single-drive bench test decide whether the one-second schedule is retained,
slowed or reshaped.

