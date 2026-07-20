# P1 single-axis bench software — specification

**Status:** accepted for implementation
**Version:** 0.1
**Date:** 2026-07-20

## 1. Problem

Provide a hardware-independent command, telemetry and gate-evaluation layer for
the P1 axis. It shall support deterministic development without a drive, and
later accept real Leadshine telemetry without changing the gate calculation.
Simulation may prove the software path but can never pass the physical P1 gate.

## 2. Interfaces and units

Python is authoritative. Public values use SI units: seconds, radians, rad/s,
newton-metres, volts and degrees Celsius. CSV column names include units.

A drive abstraction provides:

- enable and disable;
- accept a time-stamped motor-position command;
- advance or sample at an explicit time;
- return commanded/actual position, speed, torque, driver temperature, DC-bus
  voltage, overload rate and active alarm codes.

The no-hardware simulator implements the same abstraction with deterministic
tracking lag, configurable lost motion, thermal response, regenerated bus-voltage
rise and alarm injection. It is a test double, not a motor-physics oracle.

## 3. Commands

The generator consumes a committed Python trajectory result and a selected axis.
It maps output angle to motor angle with the accepted reduction and emits
monotonic time-stamped commands. It rejects non-monotonic time, non-finite data,
invalid ratios and out-of-range axis indices.

The P1 staged command plan covers low-speed dry motion and 25%, 50% and 100% of
the accepted trajectory. A reversal-count generator supports the required 1,000
full reversals without embedding controller-specific Pulse/Direction timing in
the model layer.

## 4. Leadshine diagnostic adapter

The first hardware adapter accepts an injected Modbus register client so tests
need no serial hardware or third-party package. It decodes the current iSV2-RS
manual's status registers, including alarm `0x0B03`, speed `0x0B09`, torque
`0x0B07`, current `0x0B08`, DC-bus voltage `0x0B0A`, driver temperature
`0x0B0B`, overload `0x0B0F`, command position `0x0B14/15`, actual position
`0x0B16/17` and deviation `0x0B18/19`.

Thirty-two-bit fields use high word at the even address followed by low word;
signed conversion is explicit. The default electronic gear is documented as
10,000 command units per motor revolution and is configurable. Register reads
that are absent, short or invalid fail explicitly.

Pulse+Direction output and real-time scheduling are intentionally outside this
slice: the command stream is transport-neutral and later hardware integration
must document its controller and measured timing.

## 5. Logs and reports

CSV contains one telemetry sample per row. JSON contains metadata, thresholds,
aggregate maxima, RMS position error, reversal count, alarm set, per-check
result and overall disposition. Artifact generation is deterministic.

P1 checks:

- data source must be `hardware` for a physical pass;
- at least 1,000 completed reversals;
- no drive alarm;
- output bidirectional lost motion at most 0.10 degrees;
- maximum driver temperature below 60 degrees Celsius during this bench test;
- maximum brake-resistor load below 80 percent when that field is available;
- no bus-overvoltage event and no missing/non-finite required sample;
- full requested speed and acceleration stage was executed.

Manufacturer absolute limits are not replaced by these conservative test limits.
The current manual's suggested iSV2-RS6040 regenerative-resistor test value is
10 ohm / 100 W, minimum 5 ohm; the physical build must confirm settings and safe
resistor temperature before repeated reversal.

## 6. Failure behaviour

Empty data, non-monotonic timestamps, inconsistent metadata, missing required
telemetry and non-finite values produce a failed report with explicit reasons or
a typed input error. The evaluator never silently drops bad rows. A simulator
run whose numerical checks pass returns `simulation_only`, never `passed`.

## 7. Acceptance evidence

- tests exercise enable/disable, tracking, alarm injection and thermal/bus data;
- command generation retains every source sample and exact endpoint time;
- fake Modbus registers verify signed 16-bit and signed 32-bit decoding;
- CSV round-trips all required fields;
- the same evaluator marks an otherwise identical simulator record
  `simulation_only` and hardware record `passed`;
- any threshold violation names the failed check;
- committed JSON/CSV simulator artifacts are reproducible.

## 8. Physical unknowns

The actual Modbus polling rate, command transport, encoder-field semantics,
temperature rise, regeneration and external output lost motion require the real
drive and instrumented bench. They remain explicitly unverified after this
software slice.
