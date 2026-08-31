# Public repository release

**Status:** local release candidate; awaiting final publication approval

## 1. Problem

The repository is currently local. It should be prepared as a public engineering
portfolio without overstating the robot's validation status or exposing secrets,
private career material, accidental browser traces or unreviewed identity data.
The public README should make the AI-assisted development method understandable
without requiring a reader to infer it from `AGENTS.md` and individual specs.

Creating the remote repository and making it public are separate external actions.
They require an explicit owner approval after the local release candidate and its
audit results have been reviewed.

## 2. Inputs

- the accepted HLD and P0--P4 gates in `poc_plan.md`;
- the delivery workflow in `docs/development-process.md`;
- persistent coding-agent constraints in `AGENTS.md`;
- implemented specs, tests and reproducible artifacts;
- the complete Git history, including author metadata;
- the tracked and untracked file inventory.

## 3. Outputs

- a README section explaining the project-level AI-assisted engineering workflow;
- concise, traceable examples where validation changed or rejected an
  AI-assisted implementation or engineering proposal;
- an explicit distinction between verified digital evidence, assumptions and the
  physical P1 gate that remains open;
- ignore rules for local tooling traces and private career material;
- a recorded pre-publication audit result;
- the owner-approved MIT license before the public remote is created.

## 4. Constraints

- Do not describe this one-person project as an enterprise-wide Agentic SDLC
  rollout or claim measured team-productivity improvements.
- Do not present an agent framework as implemented. Codex assists a controlled
  specification-driven workflow; the repository intentionally has no agent
  framework.
- Do not weaken or silently change the accepted geometry, profiles, BOM, costs or
  P0--P4 gates for portfolio presentation.
- Keep `simulation_only`, `proxy_only`, provisional and physically unverified
  qualifications visible.
- Do not publish secrets, authentication material, private CV files, local browser
  traces or unintended personal data.
- Do not rewrite Git history, create a remote or publish the repository during the
  preparation slice.
- Do not choose a license on the owner's behalf. The owner selected MIT on
  2026-08-31; changing that choice requires another explicit decision.

## 5. Failure behavior

Preparation stops before publication when any of the following remains unresolved:

- a likely secret or private file is present in tracked history;
- commit identity is not accepted by the owner for public display;
- the approved license is missing or does not match the repository declaration;
- the README makes a capability or physical-validation claim unsupported by the
  committed evidence;
- a tracked artifact exceeds the hosting provider's accepted file constraints;
- the local release candidate has not been reviewed by the owner.

Potential findings must be reported with paths or commit identifiers where
possible. Automated secret scans are evidence, not a guarantee that no sensitive
information exists.

## 6. Acceptance tests

The local release candidate is ready for owner review when:

1. The README shows the workflow from HLD through specification, tests,
   AI-assisted implementation, validation, reproducible evidence and a human gate.
2. At least three concrete examples link to committed evidence and distinguish the
   initial plausible result from the validation outcome.
3. The README explicitly states that digital P0 is complete while physical P1 is
   not.
4. `AGENTS.md`, `docs/development-process.md` and representative specs are linked
   as inspectable portfolio evidence.
5. Local browser/tool traces and private career files are ignored.
6. Tracked files, all reachable commits and commit author metadata have been
   audited with the available local tools; limitations are reported.
7. Documentation links resolve and the normal Python and visualizer quality gates
   still pass.
8. The final diff contains only intentional public-release preparation changes.

The repository is ready to be made public only after the owner additionally
accepts the exposed commit identity and license declaration, and explicitly
approves creation of the public remote.

## 7. Out of scope

- changing the engineering design or advancing the project beyond P1;
- claiming organizational adoption, workshop delivery or enterprise governance;
- rewriting existing commits solely to improve their presentation;
- purchasing hardware or publishing generated artifacts elsewhere;
- creating GitHub Actions, issue templates or a project website in this slice.

## 8. Pre-publication audit record

Audit run on 2026-08-31 against the complete reachable local Git history:

- the original commit identity used a personal Gmail address; the owner selected
  GitHub identity `PawelML` and
  `117289196+PawelML@users.noreply.github.com` for the rewritten public history;
  all 48 commits existing at rewrite time were rewritten, the root tree and
  commit count were preserved, and reachable refs plus subsequent commits contain
  only the selected `noreply` identity;
- no sensitive-looking filenames were found in reachable commits;
- `gitleaks` is not installed, so the audit uses a documented high-confidence
  content-pattern fallback and cannot claim equivalent scanner coverage; that
  fallback found no private-key headers, provider-token formats or generic
  credential assignments in reachable commits;
- the largest reachable blob is an 8.0 MiB generated CAD report; no individual
  artifact currently requires large-file migration for ordinary Git hosting;
- the private CV was already ignored and is absent from reachable history;
- `.playwright-mcp/` contained untracked local browser traces and is now ignored;
- the owner selected MIT and the standard license text is present in `LICENSE`;
- no remote is configured, so the preparation changes cannot accidentally alter a
  public repository.

A verified pre-rewrite Git bundle was stored outside the repository before old
objects and reflogs were pruned. Its local path is intentionally omitted from the
public document and is reported directly to the owner.

Release-candidate verification on the same date:

- every local Markdown link added to the README resolves;
- `uv run ruff check .`, `uv run mypy` and all 139 Python tests pass;
- all 8 visualizer tests and the Vite production build pass;
- `git diff --check` remains part of the final diff review.

This record must be updated if later checks change a finding or if the repository
content changes materially before publication.
