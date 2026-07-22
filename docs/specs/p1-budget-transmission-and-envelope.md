# P1 budget transmission and performance-envelope search

**Status:** implemented; proxy-only recommendation mechanically screened
**Version:** 1.1
**Date:** 2026-07-22

## 1. Problem

The active `budget_demonstrator` has an exact closed-loop stepper-kit candidate
and a proxy torque-speed curve, but no transmission, payload or cycle time. A
holding-torque comparison is insufficient. This slice shall compare physically
plausible low-cost HTD 5M transmissions and find which combinations of ratio,
payload and cycle duration are not rejected by the available curve.

The result is a screening envelope, not a drive approval. `proxy_only` evidence
cannot produce a `passes` status.

## 2. Fixed shared inputs

- accepted delta geometry: 180/65/280/450 mm;
- path: the same 25-305-25 round trip and Cartesian points as P0;
- trajectory law: the accepted minimum-jerk quintic, with every segment time
  multiplied by one common positive scale;
- mechanical mass baseline: 0.250 kg platform/tooling, 0.200 kg per upper-arm
  assembly and 0.300 kg for all lower assemblies;
- payload sweep: 0.10, 0.15, 0.20, 0.25, 0.30 and 0.50 kg;
- complete cycle durations: 1.00, 1.25, 1.50, 2.00, 2.50 and 3.00 s;
- design factor: 1.30;
- provisional budget transmission efficiency: 0.85.

The mechanical masses are the existing nominal unmeasured assumptions, not a
promise that the budget structure will have those masses. The later CAD/BOM
must weigh representative parts and rerun this search.

Scaling time must not change positions, IK, workspace margins or segment order.
For scale `s`, velocities shall change by `1/s` and accelerations by `1/s^2` at
equal normalized segment positions. The default scale `1.0` must reproduce the
committed P0 trajectory byte-for-byte.

## 3. Transmission candidates

All candidates use a 5 mm HTD pitch and 15 mm belt width with a 20-tooth small
pulley bored for the motor's 8 mm shaft.

| ID | Teeth | Ratio | Belt | Large pulley | Evidence state |
|---|---:|---:|---:|---|---|
| `catalogue_20_60_450` | 20/60 | 3.0 | 450-5M-15 | catalogue aluminium 60T, finish-machined hub required | locally catalogue-backed |
| `printed_20_80_500` | 20/80 | 4.0 | 500-5M-15 | PETG/PA prototype with bolted aluminium hub | geometric estimate only |
| `printed_20_100_600` | 20/100 | 5.0 | 600-5M-15 | PETG/PA prototype with bolted aluminium hub | geometric estimate only |

Current Polish catalogue evidence:

- HTD 5M pulleys and the 20T/60T dimensions:
  <https://www.akcesoria.cnc.info.pl/330-mechanika/pasy-zebate-kola-zebate/kola-zebate/kola-zebate-do-pasow-htd/kola-htd-5m>
- 450, 500 and 600 mm, 15 mm-wide belts:
  <https://www.akcesoria.cnc.info.pl/285-mechanika/pasy-zebate-kola-zebate/pasy-zebate/pasy-zebate-metryczne/pasy-zebate-htd/pasy-zebate-htd-5m>
- an exact 20T, 15 mm belt, 8 mm bore listing:
  <https://www.ebmia.pl/outlet/269804-kolo-zebate-htd-20-5m-15-2f-do-pasa-szerokosci-15mm-otwor-przelotowy-8mm-rowek-wpustowy-3mm.html>

Availability and price are not frozen by this calculation and must be rechecked
for the later BOM. A printed pulley is not assigned a catalogue power rating.

## 4. Inertia estimates

Each candidate shall store its physical assumptions and derive SI inertia from
simple cylinders/annuli:

- 20T small pulley: steel tooth body, 36 mm outside diameter, 8 mm bore,
  20.5 mm face plus a 23 mm hub over the remaining 5.5 mm;
- catalogue 60T: aluminium 94.35 mm tooth body, 12 mm final bore, 20.5 mm face
  plus a 50 mm hub over the remaining 9.5 mm;
- printed 80T/100T: polymer tooth rim and 6 mm web plus an 80 g aluminium hub;
- output shaft: steel, 12 mm diameter and 150 mm long;
- belt mass: scaled linearly from the existing 0.01715 kg estimate for 600 mm.

Version 1.0 provisionally placed the 20T pulley directly on the stepper shaft
to expose the cheapest layout. The follow-on mechanical closure rejected that
layout because the modelled 92.8 N effective tension difference alone exceeds
the motor drawing's 75 N dynamic radial-load limit before installation tension.
The current inertia model therefore includes the separately supported 8 mm
input shaft and R+W BKL/3/8/8 coupling specified in
`p1-budget-mechanical-and-cost-closure.md`.

## 5. Torque-speed screening

For every trajectory sample, calculate motor torque using the common equation:

```text
tau_motor = (tau_external + J_output * alpha_joint)
            / (ratio * efficiency)
            + (J_input + J_rotor) * alpha_motor
```

Compare `1.30 * abs(tau_motor)` with the lower digitization bound of the proxy
curve: `interpolated_torque - 0.03 Nm`.

The curve begins at 100 rpm. For samples from 0 to 100 rpm, use the first
running point minus uncertainty as a deliberately conservative flat screening
cap; do not use the 3.00 Nm holding torque. Above 1500 rpm the sample is
rejected. This low-speed cap is an assessment policy and does not alter the
curve object's refusal to extrapolate.

Status vocabulary:

- `rejected_by_proxy`: at least one sample exceeds speed or torque evidence;
- `not_rejected_by_proxy`: all samples fit under the proxy lower bound;
- never `passes`, because the driver, voltage and thermal duty do not match the
  published curve conditions.

The report shall also expose RMS required motor torque, but shall not compare it
with an invented continuous stepper rating. Temperature and following error
remain mandatory P1 measurements.

## 6. Selection rule

The recommended provisional candidate is the lowest-complexity catalogue-backed
transmission that is `not_rejected_by_proxy` for the largest payload and fastest
cycle among the stated sweep. A printed candidate may be recommended only if no
catalogue-backed candidate reaches the same selected operating target and its
mechanical evidence gap is stated prominently.

No combination may be promoted into HLD performance gates automatically. The
report presents an achievable-envelope candidate for user review.

## 7. Outputs

`artifacts/budget_performance_envelope.json` shall contain:

- schema and `proxy_only` status;
- exact motor/curve identity and low-speed policy;
- all transmission geometry and inertia assumptions;
- every payload/cycle/ratio result;
- worst utilization, speed, required peak and RMS torque;
- fastest non-rejected duration for each payload and transmission;
- one provisional recommendation and explicit blockers.

`scripts/generate_budget_performance_envelope.py` owns the artifact.

## 8. Acceptance evidence

- Default trajectory scaling reproduces all current trajectory samples.
- At equal normalized positions, a 2x duration gives 0.5x velocity and 0.25x
  acceleration within `1e-10` relative/absolute tolerance.
- All three belt geometries reconstruct their selected pitch length within
  `1e-9 m` and retain at least six small-pulley teeth in mesh.
- Zero added transmission inertia reproduces the existing rotor/load equation.
- Increasing a positive component inertia changes torque in the acceleration
  direction at a nonzero-acceleration sample.
- Curve utilization is calculated sample by sample; a constructed one-sample
  over-torque and over-speed case is rejected.
- The generated report is finite JSON, deterministic and exactly matches the
  committed artifact.
- Existing industrial JSON/CSV hashes and the P0 trajectory artifact remain
  unchanged.

## 9. Outside this slice

- final pulley material, tooth strength, fatigue and printed-layer validation;
- physical belt-tension setting and delivered-part fit approval;
- final shaft/bearing/hub fabrication details;
- price freeze or purchase authorization;
- changing P3/P4 gates;
- physical proof of torque, temperature or following error.

## 10. Implemented result

The deterministic sweep recommends `catalogue_20_60_450` (HTD 5M, 20/60,
15 mm, 450 mm belt) as the lowest-complexity candidate for the next mechanical
and cost-closure slice. With the stated mass assumptions it is:

- `not_rejected_by_proxy` for 0.50 kg at a 1.50 s cycle, with worst curve
  utilization 0.853 after the 1.30 design factor, including the supported
  input-shaft and coupling inertia;
- `rejected_by_proxy` for 0.50 kg at 1.25 s (utilization 1.144) and 1.00 s
  (utilization 1.681);
- `not_rejected_by_proxy` for 0.30 kg at 1.25 s, but rejected at 1.00 s.

The printed 4:1 and 5:1 candidates reach faster proxy-only points, but are not
recommended because this slice has no tooth-strength, hub-retention or fatigue
evidence for them. The 3:1 result is not validated hardware: actual masses,
delivered-part fits, price and exact-kit torque behaviour remain open. Detailed
radial-load evidence is in `artifacts/budget_mechanical_closure.json`.
