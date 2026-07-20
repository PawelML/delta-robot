# Repository instructions — delta robot

## Source of truth

- Read `poc_plan.md` before planning or implementing project work.
- Treat `poc_plan.md` as the project HLD and `docs/development-process.md` as the delivery process.
- Create or update a focused specification in `docs/specs/` before implementing a new subsystem.
- Record only architecture-changing decisions in `docs/adr/`.
- Do not silently change accepted requirements, coordinate conventions, units, geometry assumptions, P0–P4 gates, or BOM decisions.

## Current scope

- The current implementation target is P0: Python kinematics plus a Three.js visualizer.
- The Python model is authoritative. Three.js visualizes exported model results and must not become a second independent source of kinematic truth.
- The existing `BOM_delta.md` is provisional until the model and the P1 single-drive bench test justify an update.
- Do not introduce ROS2, a motion controller, cloud services, agent frameworks, or production safety architecture into P0 unless the accepted specification explicitly requires them.

## Specification-driven workflow

For each non-trivial slice:

1. State the problem, inputs, outputs, units, constraints, failure behavior, and acceptance tests in a small spec.
2. Add reference examples and tests before or together with the implementation.
3. Implement the smallest complete slice.
4. Run the relevant automated checks.
5. Report what evidence supports correctness and what remains uncertain.
6. Keep changes small enough to understand from one diff.

## Validation instead of expert manual code review

The user is not expected to validate advanced kinematic or dynamic code line by line. Correctness must therefore be demonstrated through evidence:

- independent reference cases with known expected results,
- property-based tests and geometric invariants,
- round-trip tests such as `IK -> FK`, but never round-trip tests alone,
- symmetry, reachability, joint-limit and boundary tests,
- comparison with an independent published derivation or implementation when available,
- numerical error summaries over large sampled datasets,
- visual inspection in the Three.js model,
- later comparison with physical measurements.

Do not claim a model is correct merely because tests using the same derivation pass. State explicitly when an independent oracle is missing.

## Mathematical and code conventions

- Define the coordinate system, motor-angle convention and units before implementing FK or IK.
- Use SI units internally unless an accepted spec states otherwise; document conversions at boundaries.
- Reject unreachable or ambiguous states explicitly. Do not hide them with clipping or arbitrary defaults.
- Keep numerical tolerances named and justified.
- Prefer typed, testable pure functions for geometry and kinematics.
- Avoid duplicating formulas across Python, JavaScript and tests.
- Every important number must have a stated source, derivation or measurement plan.

## Quality gates

Once configured, run the repository's formatter/linter, type checker and tests before declaring a slice complete. The intended Python baseline is:

```text
ruff check
mypy
pytest
```

Add Hypothesis tests where continuous geometric input spaces make example-only testing weak. Do not weaken a test or tolerance only to make generated code pass without documenting the reason.

## AI-assisted development record

Codex usage itself does not require a running diary. Add a short note only when something has lasting engineering value, for example:

- generated code contained a non-obvious mathematical or API error,
- validation rejected an apparently plausible approach,
- a substantial design decision changed because of measured evidence,
- the task required an unusual context or cost trade-off worth mentioning in the final case study.

Use the relevant spec or ADR for the note. Do not store full chats, routine prompts, token counts, or a log entry for every change.

## Communication

- Explain advanced mathematics in plain language and connect it to visible robot behavior.
- Separate verified facts, model assumptions and unverified hypotheses.
- When blocked by missing physical parameters, make a clearly labelled provisional assumption if it does not force an expensive purchase.
- Stop before purchases or architecture changes that are not justified by the current gate.
