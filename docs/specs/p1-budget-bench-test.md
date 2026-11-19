# Budget P1 bench load and measurement

This procedure applies to one StepperOnline CL57Y-V20 axis with the supported
20/60 HTD transmission. It supplies evidence for the existing P1 gate. The
0.50 kg / 1.50 s and 0.30 kg / 1.25 s points remain candidates from the proxy
screen. The output-side measurement is independent of the motor encoder.

## Fixture and evidence

Use the Python delta model to supply target signed output load, velocity and
acceleration for the two proposed operating points. Use the largest sampled
external joint inertia across the three axes as the initial target for the
fixture. The fixture arm, hub, mass and fasteners have to be weighed and their
centre of mass and inertia measured or calculated from the delivered geometry.
Report shaft-side inertia in kg·m², gravity and dynamic torque in Nm, angles in
degrees, and speed in rad/s or explicitly converted rpm. The CAD weight is a
layout envelope.

| Target from the 1 ms model traces | 0.50 kg / 1.50 s | 0.30 kg / 1.25 s |
| --- | ---: | ---: |
| Peak external shoulder inertia | 0.07936 kg·m² | 0.06375 kg·m² |
| Signed external shoulder torque, three-axis range | −3.748 to −0.326 Nm | −4.089 to +0.168 Nm |
| Peak absolute output speed | 4.614 rad/s (44.06 rpm) | 5.537 rad/s (52.88 rpm) |
| Peak absolute output acceleration | 41.30 rad/s² | 59.47 rad/s² |
| Illustrative point mass at 280 mm, with a 0.20 kg uniform arm | 0.946 kg | 0.747 kg |

The illustrative point masses use `J = m_arm × L² / 3 + m_tip × r²`.
Real hub and fixture hardware contribute to the measured inertia. The two
examples are starting points for fixture design and a check of available
adjustment. They do not prescribe a weight for a first powered run.

The exporter produces signed position, velocity, acceleration, external
torque and inertia per axis and timestamp. The first and last samples
are included for every axis. External torque excludes the transmission
and rotor, and the model's drive design factor has not been applied to it.
Inconsistent units or absent measurement channels invalidate a comparison.

```bash
uv run python scripts/export_budget_p1_load.py --payload-kg 0.50 --cycle-s 1.50 > p1-load-heavy.csv
uv run python scripts/export_budget_p1_load.py --payload-kg 0.30 --cycle-s 1.25 > p1-load-fast.csv
```

A fixed weight combines gravity and inertia differently from a delta robot.
Use the reference motion to compare signed torque and speed together, including
deceleration, and document the measured coverage of both operating points.
Measure output torque directly with a calibrated sensor, or estimate it from
the independently measured angle and acceleration, verified fixture inertia
and gravity moment, and a measured or bounded friction contribution. Record
uncertainty. Additional runs with changed fixture loading may be needed to
cover the required operating regions. A test with an uncovered required region
can report the measured conditions and leaves the corresponding point open.

## Physical test

1. Record exact belt, drive, supply and coupling revisions. Check the belt
   manufacturer's tension and reversing-duty sizing for the delivered belt.
   Verify the supply setting and response to deceleration before the full
   motion. CL57Y-V20 input is 24–50 V per the device manual. Account for
   measurement uncertainty in comparison to the applicable limits. The
   S-500-48 adjustment range extends beyond the driver's maximum.
2. Set belt tension by the selected manufacturer's method. Fit and secure
   the fixture and use the existing workshop drive-power cutoff and guards.
   With power off, verify travel and free clearance for the actual mass and
   instrument. Establish encoder zero, direction, resolution and calibration.
3. Log synchronized commanded and measured **output** angle, timestamp and
   stage, motor position if available, alarm line, and both surface
   temperatures and ambient. For motion, use at least 200 samples/s for
   position, with a calibrated resolution of 0.02° or better at the output.
   Sample motor and driver temperature at least once per second. Measure
   the supply rail at the driver's terminals with peak capture and bandwidth
   validated for the reversal transients. Record the method, instrument and
   uncertainty for each channel.
4. Work up through unloaded, low speed, 25%, 50% and full requested
   speed and acceleration. Record achieved speed, acceleration, torque
   coverage and rail transients. Stop the run if an alarm, a supply-limit
   excursion or a loss of tracking occurs. Use the applicable motor and
   driver temperature limits and record where and how temperature is sensed.
5. With documented load, count at least 1,000 completed reversals defined by
   the external encoder visiting alternating specified endpoint windows.
   One reversal requires a subsequent visit to the opposite endpoint after
   a change of direction. Exclude the initial move and repeated samples
   within either endpoint window.
   Record repeated endpoint positions by endpoint and approach direction.
   Report repeatability as the peak-to-peak spread in degrees, together with
   first-to-last window drift, lost motion and maximum following error.
   Continue the thermal log until both temperature traces stabilize and
   report their slopes and the observation interval.
6. Retain the time series, calibration, test configuration and a human
   decision against the HLD. A missing channel, undocumented operating limit
   or missing load coverage leaves the corresponding check open. The current
   software evaluator belongs to the simulated reference workflow. Use the
   recorded physical measurements for the budget gate until a budget
   hardware evaluator meets this contract.

[P1 gate](../../poc_plan.md#7-etapy-p0p4-i-kryteria) ·
[Instrumentation reference](p1-test-instrumentation.md) ·
[CL57Y-V20 manual](https://files.omc-stepperonline.com/CL57Y_V2.0_pulse_stepper_driver_manual_V1.0.pdf) ·
[S-500-48 datasheet](https://files.omc-stepperonline.com/S-500-48.pdf)
