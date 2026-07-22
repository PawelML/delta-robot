# P1 industrial reference and budget demonstrator profiles

**Status:** accepted for implementation
**Version:** 0.2
**Date:** 2026-07-22

## 1. Problem

The calculated Leadshine/Gates P1 axis is technically useful but its complete
instrumented implementation no longer fits the project's total purchase
envelope. The project needs a budget route without deleting, weakening or
silently replacing the existing industrial calculation.

One mathematical implementation shall therefore support two named profiles:

- `industrial_reference` preserves the current Leadshine/Gates calculation and
  its generated evidence;
- `budget_demonstrator` introduces a lower-cost closed-loop stepper candidate,
  but does not claim a payload, cycle time or transmission until those values
  pass a torque-speed-aware parameter search.

This slice originally separated configuration from calculation without a
budget transmission. Follow-on evidence now records the provisional
`catalogue_20_60_450` selection and 0.50 kg / 1.50 s screen, while the base
profile deliberately keeps `transmission=None` until physical P1 freezes
measured hardware. The generated budget-sizing report is the authoritative
complete transmission object in the meantime. No document authorizes purchase.

## 2. Shared and profile-specific inputs

Both profiles share the accepted 180/65/280/450 mm delta geometry, coordinate
conventions, IK, FK, differential kinematics, workspace classification,
trajectory machinery and dynamic equations. Geometric coverage remains
independent of the selected drive.

Profile-specific data are:

| Input | `industrial_reference` | `budget_demonstrator` |
|---|---|---|
| Drive | Leadshine `iSV2-RS6040V48G` | StepperOnline kit `3-CLYS30-V20` |
| Motor | integrated servo | `23HS40-5004D-E1000` |
| Driver | integrated | `CL57Y-V20` |
| Supply | provisional external 48 V bench supply | kit `S-500-48`, 48 V / 500 W |
| Transmission | Gates 5MGT 18/90, 5:1, fully modelled | provisional HTD 5M 20/60, 15 mm, 450 mm, supported input shaft |
| Dynamic target | current 0.50 kg / 1 Hz conservative reference | provisional 0.50 kg / 1.50 s; 0.30 kg / 1.25 s also not rejected |
| Evidence state | calculated reference, physical P1 pending | proxy curve plus digital mechanics; physical P1 pending |

No code path may silently substitute the budget candidate for the industrial
profile or vice versa. An unknown profile identifier and an attempt to run a
complete drive assessment without a selected transmission must fail explicitly.

## 3. Industrial regression contract

Refactoring the industrial constants into a profile shall preserve the numeric
and serialized results currently committed as:

- `artifacts/dynamic_sizing.json`;
- `artifacts/p1_refined_drive_trace.csv`;
- `artifacts/p1_transmission_selection.json`.

The first two files are owned by the drive-profile refactor. Their SHA-256
digests before implementation are respectively:

- `a00b77ddbbdbb734eef89c7aef630dd8e77152dc703f475ecc4dccbd4cfb27bd`;
- `2d794818ad5e41245fa0635c1f5dc1e7b8369e3c55a8adc8d9a785b7541b39e7`.

The transmission-selection artifact remains unchanged with digest
`d0ff2fe687040169506e75b9e9ae8e63a980c0bcfae674206cdb4ccd4c60ed39`.
These hashes are regression evidence, not a permanent ban on intentional,
specified schema changes in later slices.

## 4. Budget motor and kit evidence

The exact candidate kit is StepperOnline `3-CLYS30-V20`. The manufacturer's
product page lists:

- three `23HS40-5004D-E1000` motors;
- three `CL57Y-V20` drivers, 24--50 VDC and 0--7.0 A;
- one `S-500-48` supply, 48 V / 500 W / 10.5 A;
- three motor/encoder extension cables and one configuration cable.

Motor data from the current manufacturer drawing and product page are:

| Quantity | Value |
|---|---:|
| Holding torque | 3.00 Nm |
| Rated phase current | 5.0 A |
| Phase resistance | 0.6 ohm +/-10% |
| Phase inductance | 2.3 mH +/-20% at 1 kHz |
| Rotor inertia | 660 g*cm^2 = 6.60e-5 kg*m^2 |
| Motor mass | 1.65 kg |
| Step angle | 1.8 deg |
| Encoder | differential optical, 1000 PPR / 4000 CPR |
| Shaft | 8 mm diameter, 22 mm long |

Primary manufacturer sources:

- kit: <https://www.stepperonline.com.tr/ys-serisi-3-eksenli-kapali-dongu-adimlayici-cnc-kiti-v2-0-3-00-nm-424-83-oz-in-nema-23-motor-2-0-m-kablolar-ve-guc-kaynagi-ile-3-clys30-v20>
- motor: <https://www.stepperonline.ca/s-series-nema-23-closed-loop-stepper-motor-3-00nm-424-83oz-in-encoder-1000ppr-4000cpr-23hs40-5004d-e1000.html>
- published curve asset:
  <https://www.stepperonline.ca/image/catalog/torque-curves/23HS40-5004D-E1000_Torque_Curve.svg>

## 5. Torque-speed curve and its limitation

The manufacturer publishes a pull-out-torque graph for the exact motor, but
the graph header states `CL57T-V41 36V, RMS5.0A, 2000 Microstep`. This is not
the exact `CL57Y-V20 + 48 V` combination sold in the candidate kit.

The digitized marker values are therefore stored with evidence status
`proxy_only`. Linear interpolation is permitted only from 100 to 1500 rpm.
The model shall reject extrapolation below or above that interval; it shall not
connect the 3.00 Nm holding-torque value to the first running-torque point.
Digitization uncertainty is recorded as +/-0.03 Nm.

This curve may reject an obviously infeasible operating point. It may not prove
that the budget kit passes. Before a final budget drive selection, obtain a
matching manufacturer curve or measure torque/following-error/temperature on
the one-axis bench at the chosen voltage, current, microstep and control mode.

## 6. Outputs and failure behaviour

The implementation provides:

- immutable typed profile objects retrievable by stable identifiers;
- a transmission configuration containing ratio, efficiency, pitch radius and
  component inertia instead of hidden 18-tooth/5:1 constants;
- a validated torque-speed curve with bounded linear interpolation;
- a deterministic `artifacts/design_profiles.json` evidence file describing
  both profiles and all current evidence limitations.

Invalid numeric inputs, duplicate or non-increasing curve speeds, non-positive
torques, unknown profile identifiers and curve extrapolation raise
`ValueError`. The base budget profile exposes no frozen complete transmission.
The sizing and mechanical-closure modules supply the provisional transmission
explicitly, preventing code that assumes physically validated hardware from
proceeding.

## 7. Acceptance tests

- The industrial dynamic JSON and CSV remain byte-for-byte identical after the
  refactor, including their pre-refactor SHA-256 digests.
- The industrial profile contains ratio 5.0, efficiency 0.90 and the current
  Gates 18-tooth pitch radius.
- The budget profile names the exact kit, motor, driver and supply and carries
  `proxy_only` curve evidence.
- Rotor inertia converts to `6.60e-5 kg*m^2`.
- Interpolation reproduces every digitized marker and the midpoint between two
  markers to floating-point tolerance.
- Requests below 100 rpm or above 1500 rpm fail instead of extrapolating.
- The profile artifact is generated from code and matches the committed file.

## 8. Outside this slice

- physically validating the selected pulley, belt, shaft and bearing arrangement;
- proving the proxy-screened payload and cycle rate on the exact kit;
- freezing the provisional 5--6 kPLN cost envelope after quotations;
- releasing delivered-part fits and machining drawings;
- claiming that the StepperOnline kit passes P1.
