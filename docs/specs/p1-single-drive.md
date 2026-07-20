# P1 representative single drive — specification

**Status:** provisional candidate for bench validation
**Version:** 0.2
**Date:** 2026-07-20

## 1. Decision

Build and test at most one representative 5:1 servo axis before purchasing the
other two. The provisional motor/drive candidate is the integrated Leadshine
`iSV2-RS6040V48G`, subject to distributor confirmation of the exact revision,
Modbus register access and DC-bus braking requirements.

Primary manufacturer sources:

- product page: <https://www.leadshine.com/product-detail/iSV2-RS6040V48G.html>
- manufacturer datasheet:
  <https://www.leadshine.com/upfiles/downloads/9949e15632cdf92fd2df70eded77ac27_1711076777013.pdf>
- iSV2-RS user manual V2.01 from Leadshine:
  <https://www.leadshine.com/upfiles/downloads/f85ab001e8edd4c7f05e5c32ea6671fd_1766721032370.pdf>

The model is preferred over the earlier NEMA 23 closed-loop stepper because it
publishes continuous and intermittent servo torque, rotor inertia and rated
speed rather than only holding torque. Its low-voltage DC bus also avoids
introducing a 230 VAC servo drive at the moving-system prototype stage.

## 2. Calculated operating requirement

Source: conservative mass case in `artifacts/dynamic_sizing.json`, one-second
25-305-25 trajectory, 5:1 reduction, provisional 90% belt efficiency.

| Requirement at motor | Value |
|---|---:|
| Maximum speed | 34.607 rad/s = 330.48 rpm |
| Maximum acceleration | 464.613 rad/s² |
| External load peak torque | 1.820 Nm |
| External load RMS torque | 0.779 Nm |
| Design factor | 1.30 |
| Required peak after factor, before transmission/rotor inertia | 2.366 Nm |
| Required RMS after factor, before transmission/rotor inertia | 1.013 Nm |

The Leadshine datasheet gives rotor inertia `0.58 kg·cm² = 5.8e-5 kg·m²`.
Adding it and the selected pulley, bushing, belt, coupling and shaft inertias at
every sample, then applying the same 1.30 factor, gives the refined check:

| Final requirement | Worst axis | Candidate rating | Utilization |
|---|---:|---:|---:|
| RMS torque | 1.096 Nm | 1.27 Nm rated | 86.3% |
| Peak torque | 2.576 Nm | 3.81 Nm peak | 67.6% |
| Speed | 330.48 rpm | 3000 rpm rated | 11.0% |

The motor passes this **calculated** external-load-plus-rotor-inertia screen.
Friction, belt compliance/preload loss, hose force and model-form error beyond
the 30% factor remain unverified. Passing does not mean the physical axis has
passed P1. At assumed efficiency 0.85 the refined requirement is 2.725 Nm peak
and 1.159 Nm RMS, which still passes but further reduces thermal margin.

## 3. Candidate hardware contract

Manufacturer values to verify on the delivered part:

| Field | Required / expected |
|---|---|
| Motor/drive | Leadshine `iSV2-RS6040V48G`, integrated 48 VDC, 400 W, with brake |
| Input range | 24–60 VDC; operate nominally at 48 VDC |
| Continuous / peak current | 10 Arms / 28 A from manufacturer datasheet |
| Rated / peak torque | 1.27 / 3.81 Nm |
| Rated / max speed | 3000 / 4000 rpm |
| Rotor inertia | `0.58 kg·cm²` |
| Encoder | 17-bit incremental magnetic, internal closed loop |
| Commands | Pulse+Direction for motion; Modbus RTU for configuration/diagnostics |
| Holding brake | present on `G` variant; control timing documented before use |
| Environmental | integrated drive is IP20; mount away from debris and accidental contact |

The current manual documents command position at `0x0B14/15`, actual position
at `0x0B16/17`, deviation at `0x0B18/19`, DC-bus voltage at `0x0B0A`, driver
temperature at `0x0B0B` and alarm at `0x0B03`. The actual achievable polling
rate and exact revision-specific scaling remain physical integration checks.

## 4. Transmission contract

- nominal reduction: 5.00:1 from Gates 18/90 teeth;
- small pulley `P18-5MGT-15AL` on a separately supported 3/8 inch jackshaft;
- large pulley `P90-5MGT-15` with 1610-20 mm bushing on a 20 mm shaft;
- belt `600-5MGT-15`, nominal centre distance 154.37 mm and at least 25 mm
  carrier adjustment;
- input jackshaft coupled to the 14 mm servo shaft; no belt radial load on the
  servo shaft;
- guards are not production scope, but hands and loose items remain outside the
  moving belt during every powered test.

The reproducible calculation is `artifacts/p1_transmission_selection.json`.
It reports 6.82 teeth in mesh, 68.0 W design belt power against 244.0 W
interpolated capacity, and 376.5 N conservative support load. Real tension,
alignment, fits, runout and compliance remain bench measurements.

## 5. Resolution and lost-motion target

A 17-bit encoder and 5:1 reduction give a theoretical output count of
`131072 × 5 = 655360 counts/rev`, or `0.000549°/count`. This is not an accuracy
claim; belt compliance, hub fit and structural deflection dominate.

The P1 measured bidirectional lost motion target is `<=0.10°` at the output.
Measure with an external indicator/encoder while reversing under a
representative load. Report the actual result rather than compensating it away
in software during the test.

## 6. Bench electrical boundary

The bench supply shall be nominal 48 VDC. The published 10 Arms value is motor
phase current, not a justified DC-supply input rating. The provisional one-axis
BOM therefore uses at least 600 W / 12.5 A continuous, but final peak-current
and regenerative-energy compatibility must be confirmed with Leadshine and the
power-supply vendor. A generic 48 V / 350 W supply is not accepted merely
because average mechanical power is lower.

Provide the workshop minimum already accepted in the HLD: physical drive-power
cutoff, limited commissioning speed and nobody in the moving-axis envelope.
This is not a production safety architecture.

## 7. P1 bench sequence and gate

1. Verify model/revision, wiring, brake control, input voltage range and current
   limit with power off.
2. Confirm Pulse+Direction motion at low current and speed without the large
   pulley.
3. Confirm Modbus diagnostics and attempt to read actual encoder position.
4. Install the final-ratio belt drive and externally measured representative
   output inertia; record belt tension and pulley dimensions.
5. Run slow reversals, then 25%, 50% and 100% of the modelled speed/acceleration.
6. Execute at least 1,000 full reversals without drive alarm or accumulating
   position error.
7. Record motor/drive temperature until stable, bus overvoltage/regeneration
   events, commanded versus actual position and output lost motion.
8. Decide retain / change ratio / choose 750 W / reject. Only a retained result
   allows BOM v1 and two further drive purchases.

P1 passes only if torque/speed are achieved with at least the calculated 30%
load factor, temperatures stay within current manufacturer limits, the bus does
not fault during reversal, and external lost motion is measured and reported.
