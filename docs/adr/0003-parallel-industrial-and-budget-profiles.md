# ADR 0003: Keep industrial reference and budget demonstrator profiles

**Status:** accepted
**Date:** 2026-07-22

## Context

The current Leadshine/Gates axis and measurement plan are useful engineering
work, but their total cost is incompatible with the accepted 5--6 kPLN budget
for the complete workshop demonstrator. Replacing constants in place would
erase a validated comparison point; copying the model would create two sources
of kinematics and dynamics.

## Decision

Keep one authoritative Python model and introduce two explicit configurations:
`industrial_reference` and `budget_demonstrator`. Generated evidence is tagged
by profile; existing industrial artifacts remain regression references. The
budget profile may have incomplete hardware fields and must fail explicitly
when a calculation requires a component that has not yet been selected.

The top-level project direction is the budget demonstrator. The industrial
profile is retained for comparison and a possible later upgrade, not as the
active purchase plan.

## Consequences

- Common geometry, kinematics, trajectories and dynamics are not duplicated.
- Profile-specific motor and transmission data cannot leak through hidden
  defaults.
- Industrial calculations remain executable and testable.
- The budget route may honestly report `not_selected` or `proxy_only` until
  sufficient manufacturer or bench evidence exists.
- Scripts and artifacts need stable profile identifiers; later budget CAD and
  BOM work consumes the selected budget configuration.

