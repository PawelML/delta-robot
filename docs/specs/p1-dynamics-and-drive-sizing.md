# P1 simplified dynamics and single-drive sizing — specification

**Status:** accepted for implementation
**Version:** 0.3
**Date:** 2026-07-20

## 1. Problem

P0 gives the actual 1 Hz joint motion but the provisional BOM still proposes a
2.0–2.2 Nm closed-loop stepper and 5:1 belt ratio without a load calculation.
P1 shall calculate load-side peak and RMS torque for the complete exported
25-305-25 trajectory, translate it into gearbox-input requirements and update
the specification for **one** bench-test drive. It shall not authorize buying
three drives or freeze BOM v1.

## 2. Physical story and first model

Each motor must support and accelerate three kinds of moving mass:

1. the payload, platform/tooling and the platform-side share of all lower-arm
   assemblies, which translate with the platform;
2. one upper arm, represented as a uniform rotating link about its shoulder;
3. the knee-side share of that arm's lower parallelogram, represented as a
   point mass at the knee.

The Cartesian translating force is converted to joint torque by virtual work.
If `p_dot = H * theta_dot`, then:

`tau_platform = H^T * m_translating * (p_ddot - gravity_vector)`.

In the accepted base frame `gravity_vector=(0,0,-9.80665) m/s²`. Matrix `H` is
obtained from the accepted differential constraints by solving
`J_x * H = J_theta`; no finite-difference Jacobian or JS formula is introduced.

For arm `i`, with upper length `L` and positive angle downward:

```text
I_upper = m_upper * L² / 3
I_knee  = m_knee_share * L²

tau_rotating_i = (I_upper + I_knee) * theta_ddot_i
               - g * L * cos(theta_i)
                 * (m_upper/2 + m_knee_share)
```

Total load-side torque is `tau_platform + tau_rotating`. Its sign follows the
positive-down shoulder convention. Peak sizing uses absolute torque; RMS is
the square root of the time integral of torque squared divided by cycle time.

## 3. Explicit mass assumptions

All values are configurable SI inputs and carry a measurement plan:

| Parameter | Nominal | Conservative | Reason / next measurement |
|---|---:|---:|---|
| Payload | 0.300 kg | 0.500 kg | HLD nominal and optional maximum test load. |
| Platform + vacuum tooling | 0.250 kg | 0.300 kg | Provisional allowance; weigh assembled P2 platform before final sizing. |
| One upper-arm assembly | 0.200 kg | 0.250 kg | Allowance for 280 mm link, hub and fasteners; weigh the P1 representative arm. |
| All six rods + twelve joints | 0.300 kg | 0.360 kg | About 0.149 kg of 12×10×450 mm carbon tube at assumed 1600 kg/m³ plus an equal allowance for joints/hardware; replace with supplier data and scale measurements. |

Half the complete lower-arm mass is assigned to the translating platform and
half equally to the three knees. This endpoint-lumped approximation preserves
total mass but not the exact rod kinetic energy. It is deliberately conservative
near knee motion in some poses and non-conservative in others; P1 reports this
as model-form uncertainty rather than hiding it in a precision claim.

Standard gravity `9.80665 m/s²` is exact by conventional definition. No other
mass value is presented as measured.

## 4. Included and excluded loads

Included:

- gravity in every 1 ms trajectory sample,
- Cartesian inertia of the translating effective mass,
- rotational inertia and gravity of each upper arm,
- knee-lumped half of lower-arm mass,
- nominal and conservative mass cases,
- peak and trapezoidal RMS torque per axis.

Excluded from the first calculation:

- friction, belt preload loss, bearing drag and vacuum hose forces,
- compliance, vibration, backlash and collision/contact loads,
- motor rotor, small pulley and large pulley inertia,
- gearbox/belt elasticity and controller following error,
- electrical current, voltage, heating and torque-speed droop.

These exclusions prevent a final motor claim. A configurable design factor of
`1.30` is applied to the calculated load torque because the P1 gate requires at
least 30% reserve, but this factor does not magically validate the missing
loads. The bench test and later measured masses remain mandatory.

## 5. Transmission screening

Compare synchronous belt ratios 3:1 and 5:1 using provisional efficiency 0.90.
For reduction `N = motor_speed / joint_speed`:

```text
motor_speed        = N * joint_speed
motor_acceleration = N * joint_acceleration
motor_load_torque  = joint_load_torque / (N * efficiency)
specified_motor_torque = 1.30 * motor_load_torque
```

The result is only the torque needed from the motor to drive the external load.
Motor/pulley rotor inertia must later be added using the actual candidate's
published inertia. The report also gives required output torque before the
reduction so a servo or direct-drive alternative can be evaluated.

Neither ratio is selected solely from nominal holding torque. A candidate drive
must publish or be bench-tested at the required motor speed, voltage and
current. The P1 bench fixture must use the intended ratio and representative
output inertia.

## 6. Outputs

`artifacts/dynamic_sizing.json` uses schema
`delta-robot-p1-dynamic-sizing/v1` and contains:

- selected geometry and trajectory identity,
- exact mass assumptions and model limitations,
- for nominal and conservative cases, per-axis peak torque, RMS torque, peak
  speed, peak acceleration and time/pose of peak torque,
- aggregate worst-axis values,
- 3:1 and 5:1 input speed/acceleration/load-torque requirements with 30% factor,
- deterministic status and warnings.

`docs/specs/p1-single-drive.md` shall then state the minimum continuous/RMS and
intermittent torque at required speed, maximum speed/acceleration, ratio,
voltage class, feedback visibility, backlash target and bench acceptance. A
specific candidate may be named only after comparing its primary-source
torque-speed/inertia data with the report.

`BOM_delta.md` remains provisional but shall replace unsupported declarations
with the calculated requirements, one-drive-first rule and links to the sizing
evidence. Prices and availability must be rechecked before purchase.

## 7. Walk-through

1. Load the exact 1,001-sample selected-geometry trajectory.
2. At each sample calculate `H`, Cartesian inertial/gravity force and its three
   generalized torques.
3. Add each upper-arm/knee inertia and gravity torque.
4. Record signed torque, absolute peak and squared torque for RMS integration.
5. Repeat without changing motion for nominal and conservative masses.
6. Convert the worst load case through 3:1 and 5:1, retaining speed as well as
   torque.
7. Compare the resulting operating point with primary manufacturer data.
8. Update the one-drive spec and provisional BOM; stop before buying three.

## 8. Acceptance evidence

- With zero mass every torque is zero to `<1e-12 Nm`.
- At a stationary symmetric centre pose all three torques match to `<1e-12 Nm`.
- Cartesian virtual-work identity `tau_platform·theta_dot = force·p_dot` holds
  to `<1e-10 W` over targeted nonsingular samples.
- Doubling every configured mass doubles total torque to `<1e-12` relative
  error for the same motion.
- Peak torque is not lower than RMS torque on any axis.
- Recomputed trapezoidal RMS and maxima match the JSON summary to `<1e-12`.
- Nominal and conservative reports cover all 1,001 samples without non-finite
  values or singularities.
- A finer 0.5 ms trajectory changes every reported peak and RMS value by less
  than 1%; otherwise P1 adopts the finer sampling.
- The drive spec separates verified calculation, provisional mass/efficiency
  assumptions and unavailable manufacturer data.

## 9. Decision boundary

Completing this software slice may justify ordering **one** representative
motor/driver/transmission set for P1. It does not freeze the exact arm material,
permit buying three sets, or claim the 1 Hz cycle is physically achieved. Those
decisions wait for measured component masses, candidate torque-speed evidence
and 1,000 bench reversals with temperature and position-error reporting.

## 10. Implemented result

The reproducible report `artifacts/dynamic_sizing.json` passes the 0.5 ms
convergence check with a maximum relative peak/RMS change of
`4.99e-6`. For the conservative mass case it reports:

| Quantity | Worst axis result |
|---|---:|
| Output peak load torque | 8.190 Nm |
| Output RMS load torque | 3.507 Nm |
| Output speed | 6.921 rad/s = 66.10 rpm |
| Output acceleration | 92.923 rad/s² |
| 5:1 motor speed | 330.48 rpm |
| 5:1 external-load peak, with 30% factor | 2.366 Nm |
| 5:1 external-load RMS, with 30% factor | 1.013 Nm |

The earlier BOM proposal of a 2.0–2.2 Nm closed-loop stepper is rejected for
P1: its quoted value is holding torque, while the calculated required peak at
330 rpm already exceeds it before rotor inertia, pulley inertia and friction.

### AI-assisted implementation note

- The original 5:1 stepper proposal appeared plausible from static payload and
  holding torque alone.
- The time-domain model found 8.190 Nm output peak and 3.507 Nm output RMS for
  the conservative 1 Hz cycle, invalidating that selection basis.
- P1 changes to a 400 W servo candidate and retains the one-drive bench gate;
  the full three-axis purchase remains blocked.

## 11. Refined P1 transmission model

Version 0.3 adds the selected transmission from
`artifacts/p1_transmission_selection.json`. The earlier simplified result remains
visible for traceability, but the candidate decision uses sample-by-sample
motor torque:

```text
tau_motor = (tau_external + J_output_transmission * alpha_joint)
            / (ratio * efficiency)
            + J_input_transmission * alpha_motor
            + J_rotor * alpha_motor
```

`J_input_transmission` includes the small pulley, supported input shaft,
coupling and translating belt inertia referred to the small pulley.
`J_output_transmission` includes the large pulley, 1610 bushing and output
shaft. Pulley inertia comes from published Gates `WR²`. Shaft, coupling and
bushing inertia are explicit geometric estimates with density and dimensions
stored in the artifact; every one is replaced by measured mass/inertia or
supplier data before a final three-axis purchase.

The report evaluates upper-arm assembly masses of 0.15, 0.20, 0.25 and 0.30 kg
while retaining the conservative payload, platform and lower-arm assumptions.
It also reports an efficiency sensitivity at 0.85, 0.90 and 0.95. The accepted
screen continues to use 0.90; the other values expose selection sensitivity and
do not silently alter the HLD.

For each sample the report also calculates small-pulley pitch-line tension
difference from the absolute torque transmitted through the belt. Installation
preload remains separate: dynamic tension difference is not added to the load
model as an invented friction torque.

The P1 CAD representative mass is derived to match the maximum conservative
external-load joint inertia with a 280 mm bench arm. This is an equivalent
inertia fixture, not a claim that one point mass reproduces delta-robot gravity,
Jacobian coupling or every operating pose. The generated bench trajectory
therefore tests the drive/transmission envelope and controller path; the full
Python delta model remains authoritative for robot loads.

Version 0.3 output changes `artifacts/dynamic_sizing.json` to schema
`delta-robot-p1-dynamic-sizing/v2`. It adds component inertia assumptions,
refined per-axis torque time histories/summaries, arm-mass variants, efficiency
sensitivity, peak belt-force difference and the equivalent bench load. Tests
must prove that zero added inertia reproduces the original motor calculation,
that increasing any positive inertia cannot reduce acceleration torque at a
sample with fixed acceleration sign, and that committed results are exactly
reproducible.
