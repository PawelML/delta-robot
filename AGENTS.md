# Repository instructions — delta robot

## Source of truth

- Read `poc_plan.md` before planning or implementing project work.
- Treat `poc_plan.md` as the project HLD and `docs/development-process.md` as the delivery process.
- Create or update a focused specification in `docs/specs/` before implementing a new subsystem.
- Record only architecture-changing decisions in `docs/adr/`.
- Do not silently change accepted requirements, coordinate conventions, units, geometry assumptions, P0–P4 gates, or BOM decisions.

## Current scope

- Digital P0 and the digital mechanical/cost closure of the budget axis are complete. The current gate is P1: confirm suppliers and delivered dimensions, then build and physically validate one representative budget axis.
- The project has two explicit profiles from `docs/specs/p1-design-profiles.md`: active `budget_demonstrator` and retained `industrial_reference`. They share one Python model; do not duplicate formulas between profiles.
- Industrial P1 calculations, the ForgeCAD bench, simulated drive and automated report pipeline are implemented, but they are reference evidence and have not passed a physical gate. The budget HTD 5M 20/60 radial-load closure, bench CAD and provisional BOM are implemented; physical proof and delivered-part fits are still missing.
- The Python model is authoritative for kinematics, differential kinematics, trajectories, dynamics and transmission calculations. Three.js and ForgeCAD visualize or package exported/modelled results and must not become independent mathematical sources of truth.
- `BOM_delta.md` preserves the inactive industrial-reference purchase specification. `BOM_budget_delta.md` is the active provisional 5,870.09 PLN cost envelope, not a purchase authorization. Buy/fabricate at most one axis of transmission hardware before physical P1; the three-axis drive kit is one indivisible candidate SKU.
- Do not purchase or specify three production axes, start P2 construction, or introduce ROS2, a motion controller, cloud services, agent frameworks or production safety architecture unless an accepted specification explicitly advances the project beyond P1.

## Accepted engineering baseline

- The selected provisional delta geometry is: 180 mm base-joint radius, 65 mm platform-joint radius, 280 mm upper arms, 450 mm lower rods and shoulder limits from -45 deg to +80 deg.
- The accepted useful workspace remains a sampled cylinder `diameter 400 mm x Z height 150 mm`, centred at `Z = -347 mm`. Diameter is an XY dimension; do not confuse conveyor width with vertical Z travel.
- A centred `305 mm x 200 mm` horizontal conveyor footprint fits inside the 400 mm useful diameter: its corner radius is about 182.4 mm. The stated 200 mm conveyor width therefore does not change the accepted 150 mm Z height.
- In `industrial_reference`, the selected transmission is Gates 5MGT, 18/90 teeth, 15 mm width and a 600 mm belt, using the separately supported input jackshaft from `docs/adr/0002-supported-input-jackshaft.md`. The calculated drive is Leadshine iSV2-RS6040V48G, 48 V / 400 W. Preserve these values and artifacts as a comparison point; do not present them as the active purchase plan or validated hardware.
- In `budget_demonstrator`, the first exact drive candidate is StepperOnline `3-CLYS30-V20` with `23HS40-5004D-E1000` motors and `CL57Y-V20` drivers. The provisional transmission is catalogue HTD 5M 20/60, 15 mm, 450 mm with an 8 mm jackshaft supported by two 608 bearings and an R+W BKL/3/8/8 coupling. Direct 20T mounting on the motor is rejected because 92.8 N effective belt-tension difference exceeds the 75 N motor-shaft limit before installation tension. The proxy-only sweep does not reject 0.50 kg / 1.50 s or 0.30 kg / 1.25 s. The published motor curve uses CL57T-V41 at 36 V; these points are not validated capability or purchase authorization.
- The total purchased demonstrator target is 5,000--6,000 PLN gross delivered to Poland under the inclusions and exclusions in `poc_plan.md`.
- Exploratory parameter checks may be run without changing accepted requirements. Do not promote them into defaults, artifacts, the BOM or claims of capability until the relevant spec and evidence are updated.

## Specification-driven workflow

For each non-trivial slice:

1. State the problem, inputs, outputs, units, constraints, failure behavior, and acceptance tests in a small spec.
2. Add reference examples and tests before or together with the implementation.
3. Implement the smallest complete slice.
4. Run the relevant automated checks.
5. Report what evidence supports correctness and what remains uncertain.
6. Keep changes small enough to understand from one diff.

Generated files in `artifacts/` are evidence, not hand-authored configuration. Regenerate them with the owning script and commit the input/code change together with the resulting artifact. A report marked `simulation_only` can validate software plumbing but can never satisfy a physical P1 acceptance criterion.

## Validation instead of expert manual code review

The user is not expected to validate advanced kinematic or dynamic code line by line. Correctness must therefore be demonstrated through evidence:

- independent reference cases with known expected results,
- property-based tests and geometric invariants,
- round-trip tests such as `IK -> FK`, but never round-trip tests alone,
- symmetry, reachability, joint-limit and boundary tests,
- comparison with an independent published derivation or implementation when available,
- numerical error summaries over large sampled datasets,
- visual inspection in the Three.js model,
- analytical capacity and stress checks with stated service factors for the transmission,
- CAD checks at the minimum, nominal and maximum accepted joint positions,
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

Run the checks relevant to every changed surface before declaring a slice complete. The Python baseline is:

```bash
uv run ruff check .
uv run mypy
uv run pytest
```

Add Hypothesis tests where continuous geometric input spaces make example-only testing weak. Do not weaken a test or tolerance only to make generated code pass without documenting the reason.

For changes to exported P0/P1 evidence, rerun the owning scripts listed in `README.md` and confirm that only intentional artifact changes remain. For visualizer changes also run:

```bash
cd visualizer
npm test
npm run build
```

For ForgeCAD changes, run `forgecad run` and the relevant inspection command. A moving bench must be checked at least at the accepted minimum, nominal and maximum output angles; intentional fit/contact overlaps must be distinguished from unexpected collisions.

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
