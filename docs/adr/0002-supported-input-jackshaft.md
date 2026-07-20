# ADR 0002 — Separately supported belt input shaft

**Status:** accepted
**Date:** 2026-07-20

## Context

The first P1 concept placed the small synchronous-belt pulley directly on the
Leadshine servo shaft. Belt preload and transmitted force would then create a
continuous radial shaft load. The current Leadshine installation guidance says
to use a flexible coupling, avoid impact during pulley installation, and older
iSV2 mechanical guidance states that the motor shaft should not bear radial or
axial load. No acceptable published radial-load rating was found for the
provisional motor.

## Decision

The P1 bench uses a separately supported input jackshaft. The servo connects to
it with a flexible zero-backlash coupling. The 18-tooth pulley is positioned
between two jackshaft bearings. Belt adjustment moves the supported jackshaft
housing, not an overhung pulley on the motor shaft.

The output pulley is likewise positioned between two output-shaft bearings so
that the arm-side overhang does not add to belt-induced bending at one bearing.

## Consequences

- Motor-shaft belt load is removed from the design calculation.
- The coupling, jackshaft, two bearings and an adjustable housing are added to
  the CAD and P1 BOM.
- Their inertia, alignment error and compliance are added to the dynamic model.
- Coupling alignment and its speed/torque ratings become P1 inspection items.
- The bench is larger and costs more than a direct-on-motor pulley arrangement.
- A future motor with a documented acceptable radial-load rating may justify a
  new ADR, but shall not silently revert this decision.
