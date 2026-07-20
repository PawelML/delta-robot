# Development process

## Purpose

This project uses specification-driven, AI-assisted development, but the robot and its measured behavior remain the product. The process exists to make generated code verifiable without requiring the owner to review advanced mathematics line by line.

The process intentionally stays lightweight. It does not introduce an agent framework, a prompt archive or mandatory token accounting.

## Documents and responsibilities

| Artifact | Purpose | Update frequency |
|---|---|---|
| `poc_plan.md` | High-level design, scope and P0–P4 gates | Only when project direction or acceptance criteria change |
| `docs/specs/*.md` | Contract and acceptance tests for one subsystem or implementation slice | Before that subsystem is implemented |
| `docs/adr/*.md` | Important architecture or hardware decisions and their consequences | Only for decisions with lasting cost |
| Tests | Executable evidence that implementation meets the spec | With each implemented behavior |
| Generated reports/JSON | Numerical evidence and visualizer inputs | Reproducibly generated from code |
| Git commits | Small history of implemented decisions | Per coherent change once Git is initialized |

## Workflow for a feature

```text
HLD requirement
      │
      v
Focused spec + acceptance criteria
      │
      v
Reference cases and tests
      │
      v
Small Codex-assisted implementation
      │
      v
Automated validation + numerical report
      │
      v
Three.js visual check where applicable
      │
      v
Commit and optional ADR
```

### 1. Focused specification

A spec should answer:

- What problem is being solved?
- What are the inputs and outputs?
- Which coordinate system and units apply?
- What constitutes a valid, unreachable or ambiguous result?
- What tolerances are acceptable and why?
- Which examples and properties must pass?
- What is explicitly outside this slice?

The first planned specification is `docs/specs/p0-kinematics.md`.

### 2. Tests before confidence

Tests should be designed before or together with implementation. Green tests are evidence only when they can detect a plausible wrong implementation.

For kinematics, the evidence set should contain:

- independently calculated reference poses,
- center and symmetry cases,
- joint-limit and unreachable cases,
- property-based sampling of the valid workspace,
- `IK -> FK` and, where unambiguous, `FK -> IK` checks,
- numerical error distribution, including maximum and high-percentile error,
- comparison with a separate derivation or trusted reference.

Round-trip consistency alone is insufficient because FK and IK can share the same incorrect convention.

### 3. Implementation

Implementation should proceed in small vertical slices. For example:

1. geometry types and coordinate convention,
2. one-arm inverse geometry,
3. complete IK with reachability errors,
4. FK,
5. sampled workspace export,
6. visualizer ingestion and rendering.

Each slice should leave the repository runnable and should avoid unrelated refactoring.

### 4. Automated checks

The planned baseline is:

```bash
ruff check
mypy
pytest
```

Hypothesis will be used for continuous geometry spaces when it adds stronger coverage than hand-written examples. CI can be added after the initial project scaffold and test commands exist.

### 5. Human-facing validation

The owner should not need to inspect every formula. Each completed mathematical slice must instead provide a short explanation containing:

- what was implemented,
- what independent evidence was used,
- numerical accuracy obtained,
- a visible example in the visualizer when relevant,
- known limitations and remaining uncertainty.

The owner can then evaluate behavior and evidence rather than advanced implementation details.

## Lightweight record of AI-assisted work

Routine Codex use is not logged. A short note is added to a spec or ADR only when one of these events occurs:

- a plausible generated solution fails an independent test,
- a hidden assumption changes the design,
- validation changes a hardware or architecture decision,
- a reusable lesson is worth including in the final English case study.

A note should normally be three to six lines:

```markdown
### AI-assisted implementation note

- Proposed approach: ...
- Evidence that rejected or confirmed it: ...
- Human/project decision: ...
- Lasting consequence: ...
```

There is no requirement to save prompts, full conversations, routine corrections or token usage.

## Definition of done for a P0 slice

A P0 slice is complete when:

- its behavior and boundaries are described in a focused spec,
- acceptance tests pass,
- at least one validation method is independent of the implementation under test,
- formatting, linting and type checks pass once configured,
- generated artifacts are reproducible,
- assumptions and remaining uncertainties are visible,
- `poc_plan.md` remains accurate.

If an independent oracle does not yet exist, the slice may be marked experimental, but it must not be presented as validated.
