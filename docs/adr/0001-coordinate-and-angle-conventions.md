# ADR 0001 — Coordinate and angle conventions

**Status:** accepted
**Date:** 2026-07-20

## Context

Rotary-delta formulas are sensitive to axis direction, arm numbering, angle sign
and assembly branch. Two internally consistent implementations can produce
different results if those conventions are implicit. The visualizer and future
hardware must also share the same frame.

## Decision

- Use a right-handed base frame with its origin at the center of the fixed base.
- Put the fixed base in `Z = 0` and the normal workspace below it in `Z < 0`.
- Place arm 1 on the `-Y` radial axis; arms 2 and 3 follow at `+120°` and `-120°`.
- Number joint vectors as `(arm 1, arm 2, arm 3)`.
- Define zero shoulder angle as a horizontal upper arm extending radially outward.
- Define positive shoulder rotation as motion from horizontal toward `-Z`.
- Use metres and radians inside the Python model; convert only at interfaces.
- Make the physical assembly mode explicit. P0 supports knee-out with the
  platform below the base.
- Treat the Python model as authoritative and export data to Three.js.

## Rationale

This convention is compatible with the revolute-input examples in Robert L.
Williams II, *The Delta Parallel Robot: Kinematics Solutions* (Ohio University,
2016), allowing its published numerical examples to act as an independent
validation oracle.

## Consequences

- Reference values copied from sources using other conventions require a
  documented adapter.
- The visualizer must not flip the Z axis silently; any Three.js display mapping
  belongs at the rendering boundary.
- IK and FK APIs must reject or explicitly represent unsupported branches rather
  than choosing one invisibly.
