# P0 and P1 engineering audit — 19 November 2026

Reviewed baseline `51dcf7d` against the [HLD](../poc_plan.md) and
[development process](development-process.md). The numerical evidence supports
keeping P0 and continuing with the budget 20/60 design as the candidate for a
single axis. Fix the bench mounting pattern and define the representative load
and hardware evidence before releasing the bench for fabrication or using it to
decide P1. The physical P1 gate remains open.

## Findings in priority order

1. **High | The report generator can pass a run without evidence of physical
   P1.** The evaluator counts changes in commanded direction across all stages.
   It derives “output” following error from the motor encoder and ideal gear
   ratio. It accepts full speed as a Boolean, checks the peak driver
   temperature, and takes one supplied lost-motion value. It cannot establish
   completed output reversals, repeatability, accumulated drift, or thermal
   stabilization of both motor and driver. A synthetic `hardware` run with
   1,002 half-second samples labelled `idle`, alternating command and motor
   readback between 0 and 1 rad with zero reported velocity, returned
   `passed`. The budget hardware path needs validated stage timing, calibrated
   output feedback, completed endpoint visits and endpoint spread/drift,
   thermal trends, and profile-specific thresholds. Keep the simulation report
   useful for exercising the software. [Evaluator](../delta_model/p1_bench/evaluation.py#L58)
   · [Existing instrumentation specification](specs/p1-test-instrumentation.md)

2. **High | The budget base plate has three compromised mounting features.**
   Two Ø9 mm output-support holes are centred at X = 238 mm, 2 mm from
   the plate edge. Each opens through the edge by 2.5 mm. The inboard front
   Ø9 mm hole at (206, −120) mm merges with the Ø13 mm anchoring hole at
   (210, −115) mm. Their centres are 6.40 mm apart for a combined radius of
   11 mm. The XY section at Z = 5 mm shows both edge breakouts and the
   merged hole. Revise the footprint with usable hole ligaments and bearing
   surfaces for the fasteners. Recheck arm travel and installation clearance.
   [Budget base plate source](../cad/2026/07/22/p1-budget-single-axis-bench/main.forge.js#L120)

3. **High | The budget bench has no demonstrated load equivalence.** For
   0.50 kg / 1.50 s, the robot model reaches 0.0794 kg·m² of external joint
   inertia on axes 2 and 3. Using the budget mass envelope's 304 mm mass
   centre, its declared 0.50 kg mass, and the assumed 0.20 kg uniform arm,
   the fixture has about 0.0516 kg·m², roughly 35% lower. Under the same
   joint motion the fixture calculation peaks at 3.29 Nm versus the model's
   3.75 Nm on those axes, before transmission terms. These are model-to-model
   comparisons. The CAD identifies the mass as an envelope. Specify the
   actual fixture by measured mass, centre of mass and inertia, then check
   that the loaded test covers the relevant torque and speed of each proposed
   operating point. A fixed tip mass can approximate the load over selected
   conditions. The robot's effective inertia and gravity load vary along the
   path. [Budget mass geometry](../cad/2026/07/22/p1-budget-single-axis-bench/main.forge.js#L315)
   · [Budget fabrication package](p1-budget-bench-fabrication-package.md)

4. **High | The budget driver has only 2 V of nominal supply headroom.**
   The CL57Y-V20 manual limits its input to 50 V, and the S-500-48
   datasheet lists a 48 V nominal output with adjustment up to 52.1 V.
   The exact installed supply setting, ripple and reversal transients matter.
   The existing evaluator's 60 V ceiling comes from the reference bench
   and would accept a 55 V reading on the budget profile. The model predicts
   roughly 15 W peak returning mechanically to one motor at 0.50 kg / 1.50 s.
   Electrical energy on the bus depends on driver losses and supply behaviour.
   Confirm the power arrangement and measure the rail before full-speed
   reversals. [Driver manual, chapters 2–4](https://files.omc-stepperonline.com/CL57Y_V2.0_pulse_stepper_driver_manual_V1.0.pdf)
   · [Power supply datasheet](https://files.omc-stepperonline.com/S-500-48.pdf)

5. **Medium | The mechanical screen covers the heavier point and misses the
   governing faster point.** The 0.30 kg / 1.25 s point has the highest belt
   force, motor peak torque and motor speed of every non-rejected point for the
   selected 20/60 candidate. With the existing preload and safety-factor
   assumptions, the simple shaft and coupling checks still meet their
   provisional thresholds for that point. The result needs actual belt
   tension, belt tooth capacity for reversing duty, final fits and retention,
   and a fatigue check consistent with the finished shaft. The BOM specifies
   Optibelt. The screen uses a Gates minimum preload as a proxy. Obtain the
   exact belt series and use its own manufacturer's sizing and tension method.
   [Mechanical screen](../delta_model/budget_mechanics.py#L190)
   · [Belt listing](https://www.ebmia.pl/pasy-zebate-htd-5m/1350-pas-zebaty-450-5m-15-z90.html)
   · [Optibelt manual, pp. 38 and 44](https://www.optibelt.com/fileadmin/extranet/power_transmission/technische_Unterlagen/OPTIBELT-TM-Rubber-Timing-Belt-Drives.pdf)

   | Same screening assumptions | 0.50 kg / 1.50 s | 0.30 kg / 1.25 s |
   | --- | ---: | ---: |
   | Peak pitch-line force difference before 1.30 factor | 92.81 N | 101.40 N |
   | Factored pulley radial load | 234.42 N | 245.49 N |
   | Provisional shaft yield factor | 2.98 | 2.81 |
   | Provisional coupling torque factor | 1.55 | 1.41 |

6. **Medium | The nominal budget speed is sensitive to mass, and P4
   throughput is still open.** The published 23HS40-5004D-E1000 curve uses
   CL57T-V41 at 36 V. Its plotted low-speed values support the transcribed
   proxy. At 0.30 kg / 1.25 s, utilization increases from 93.4% to 100.8%
   when each modeled upper arm goes from 0.20 to 0.25 kg, lower assemblies from
   0.30 to 0.36 kg total, and the platform/tooling stays at 0.25 kg. On the
   current trajectory, 1.25 s is 0.8 picks/s, and 0.30 kg / 1.00 s
   requires 137.0% of proxy torque after the design factor. The accepted P4
   target stays at 1.0 pick/s. The actual kit, measured masses and any later
   trajectory changes will determine the attainable throughput. The
   75 N motor radial-load limit at 20 mm from the face supports keeping the
   separately supported jackshaft. [Proxy curve](https://www.stepperonline.ca/image/catalog/torque-curves/23HS40-5004D-E1000_Torque_Curve.svg)
   · [Motor datasheet](https://files.omc-stepperonline.com/23HS40-5004D-E1000_Full_Datasheet.pdf)
   · [Performance sweep](../artifacts/budget_performance_envelope.json)

7. **Medium | The industrial reference has an intermediate angle collision.**
   At +42.5° the representative mass overlaps the base plate by 237.7 mm³.
   The roughly 10,566 mm³ overlap between the mass and arm throughout the
   sweep is the documented clamp envelope. The extra base contact is separate
   and was missed by checks at −45°, 0° and +80°. Correct or document this
   travel restriction before any future use of the reference fixture.
   [Reference CAD mass and clamp](../cad/2026/07/20/p1-single-axis-bench/main.forge.js#L270)

8. **Medium | The cost total is reproducible and remains a planning estimate.**
   The 5,220.09 PLN base contains 3,519.66 PLN in capped allowances and
   1,700.43 PLN in dated catalogue prices. Adding the 650 PLN reserve leaves
   129.91 PLN below 6,000 PLN. The Polish vendor listing confirms the drive
   SKU, and the parts listing confirms the belt dimensions and brand. A
   delivered quote for the exact kit and machining quotes for the corrected
   bench are open. Keep the pilot's fixture and measurement costs visible
   against the HLD's cost inclusions and exclusions.
   [Active BOM](../BOM_budget_delta.md)
   · [Polish kit listing](https://www.stepperonline.pl/zestaw-cnc-z-silnikiem-krokowym-z-zamknieta-petla-ys-series-3-osie-v2-0-3-00nm-424-83oz-in-silnik-nema-23-z-przewodami-2-0m-i-zasilaczem-3-clys30-v20)

9. **Low | A valid custom cycle duration fails at the final sample.**
   `generate_trajectory(cycle_time_scale=1.4)` accepts the divisibility
   check and later rejects its final timestamp, `1.4000000000000001`,
   against the summed segment duration of `1.4`. The published grid
   regenerates. Set the final sample to the canonical trajectory duration
   and cover the 1.4 s case when extending the sweep.
   [Trajectory sampling](../delta_model/trajectory.py#L321)

## What held up

- **Kinematics and workspace.** A separate audit calculation bisected the raw
  rod-length equations for IK and used Newton iteration on the three geometric
  constraints for FK. It covered 25,000 seeded points sampled uniformly in
  the accepted cylinder and 22,320 points on its outer surface at 31 Z levels.
  Repository IK differed by at most 1.34 × 10⁻¹⁵ rad. Maximum repository
  IK→FK closure error was 3.56 × 10⁻¹⁶ m. The independent minimum serial and
  parallel singularity margins were 0.572 and 0.605, above the 0.20 threshold.
  Sampled shoulder angles ranged from −32.94° to +68.04°. The included
  Williams cases supply a published reference with a different geometry. The
  conveyor corner radius is 182.36 mm, within the 200 mm cylinder radius. This supports the
  sampled kinematics and leaves physical joint articulation, collisions and
  calibration for the corresponding hardware checks.
  [Williams reference](https://sites.ohio.edu/williams/html/PDF/DeltaKin.pdf)
  · [Conveyor report](../artifacts/conveyor_coverage.json)
- **Trajectory and dynamics.** Finite differences of independent IK gave
  maximum joint-rate and acceleration differences of 8.36 × 10⁻⁶ rad/s and
  2.56 × 10⁻⁴ rad/s² on the 1 s trajectory away from segment joins.
  For a separate torque calculation, numerical FK supplied virtual
  displacements and accelerations for all lumped masses. Two quadrature
  points reproduced the upper-arm mass moments. The worst-axis conservative
  peak was 8.190263 Nm versus 8.190267 Nm in the repository, with a
  maximum per-sample error of 1.72 × 10⁻⁵ Nm. The comparison verifies the
  simplified model's arithmetic and signs. The physical effect of mass
  distribution, friction, hose forces and transmission compliance still needs
  measurement.
- **Transmission arithmetic and references.** The 20/60 pitch circles and
  450 mm open belt give a 120.806 mm nominal centre distance, 149.45°
  small-pulley wrap and 8.30 teeth in mesh. The retained 5:1 assessment
  regenerates at 2.576 Nm peak, 1.096 Nm RMS and 330.48 rpm. The exact
  Leadshine data sheet confirms its 1.27 Nm rated and 3.81 Nm peak values.
  The Modbus field addresses and high-word/low-word position ordering agree
  with the manual. Scaling and time alignment still need revision-specific
  confirmation for physical telemetry.
  [Leadshine datasheet](https://www.leadshine.com/upfiles/downloads/9949e15632cdf92fd2df70eded77ac27_1711076777013.pdf)
  · [Leadshine manual](https://www.leadshine.com/upfiles/downloads/f85ab001e8edd4c7f05e5c32ea6671fd_1766721032370.pdf)
- **Builds and reproducibility.** Ruff and strict Mypy passed, along with
  139 Python and eight JavaScript tests. All 11 README Python generators
  reproduced the tracked JSON and CSV byte for byte in a detached worktree.
  Vite built successfully. Chromium rendered the robot and workspace,
  advanced the trajectory, and passed pause and restart checks. The browser
  reported a missing favicon and a Three.js shadow-map deprecation. The
  build includes the entire public artifacts directory, around 26 MB on
  disk, while the scene consumes three JSON files. npm audit reported four
  development dependency entries, three high and one moderate, which are
  separate maintenance work.

## CAD verification

ForgeCAD 0.10.3 ran both sources. The STEP imports had 18 budget and 29
industrial bodies, with the same assembly bounds as their source runs at
0.1 mm reporting precision. I inspected iso, front, right and top renders,
the budget plate section, and interference images including the industrial
collision pose. The scores apply to the candidate bench layouts.
The budget mechanical-integrity check also passed at −45°, 0° and +80°
with the carrier set to each adjustment endpoint (−15 and +3 mm).

| Criterion | Budget layout | Industrial reference |
| --- | --- | --- |
| Motor, supported input, belt and output shown | Pass | Pass |
| Nominal pose and 11 samples across −45° to +80° | No positive-volume interpart collision | Documented clamp overlap and an unexpected base/mass collision |
| Usable mounting and measured load fixture | Hole pattern fails section inspection, fixture load remains open | Fits and retention remain provisional, mass travel fails at an intermediate angle |
| ForgeCAD grader score | **6/10** | **5/10** |

The budget score reflects the unusable hole pattern despite the clean sweep.
The reference score reflects the collision in the required travel. Fits,
fastener access, belt behaviour and the final weight and inertia of both
fixtures remain open.

The inspection commands below reproduce the sweep and section. Substitute the
industrial source path for the reference sweep. Add `--chrome-path` if
ForgeCAD cannot locate Chromium.

```bash
bench=cad/2026/07/22/p1-budget-single-axis-bench/main.forge.js
forgecad run "$bench"
forgecad render 3d "$bench" --camera iso --camera front --camera right --camera top
forgecad inspect fit interference "$bench" --joint-sweep 'output_angle=-45..80:11'
forgecad inspect section "$bench" --plane xy --offset 5 \
  --ray 'outer-front:225,-120:250,-120' --ray 'outer-rear:225,-50:250,-50'
```

## Order of work for P1

1. Correct the budget plate hole pattern and specify the loads and instruments
   the single-axis bench must reproduce or measure.
2. Screen the planned operating points against the exact belt, shaft, coupling
   and driver limits. Confirm supply headroom and obtain delivered parts and
   machining quotes within the existing cost gate.
3. Measure delivered parts, release the fits and machining drawings, then run
   the instrumented single-axis P1. Decide the drive and the remaining axes
   from the physical result.
