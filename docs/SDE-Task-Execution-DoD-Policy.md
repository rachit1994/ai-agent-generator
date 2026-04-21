# SDE Task Execution and Definition of Done Policy

## Purpose
Prevent false completion. A task is complete only when it meets a strict, test-backed, production-ready Definition of Done (DoD) with no open quality gaps.

## What Goes Wrong Without This Policy
- Repo misunderstandings cause edits in the wrong layer and missing integration points.
- Non-atomic plans hide dependencies and produce partial, unverifiable delivery.
- "Looks done" coding without hard negative tests lets fail-open behavior ship.
- Weak contract enforcement creates schema and semantic drift across artifacts.
- Unchecked assumptions about runtime, infra, or flags cause production regressions.
- Loose completion standards pass happy paths while edge failures remain unresolved.

## Mandatory Workflow for Every Task
SDE must execute this workflow in order. Skipping any step is a hard failure.

1. Repo Grounding
- Read repo docs and architecture guidance relevant to scope.
- Identify owner modules, dependencies, contracts, runtime entry points, and tests.
- Record assumptions, constraints, and explicit risks before coding.

2. Create Atomic Spec in `docs/`
- Create or update a task execution spec in this repo's `docs/` folder.
- Break work into atomic steps where each step yields one observable, testable state change.
- For every step include:
  - exact files to change
  - expected behavior change
  - positive and negative tests
  - pass/fail criteria
  - rollback/fail-safe behavior

3. Multi-Pass Atomicity Review (Required)
- Pass 1: split broad steps into independently verifiable units.
- Pass 2: remove ambiguity, hidden coupling, and implied behavior.
- Pass 3: verify each step maps to concrete tests and fails closed when invalid.
- Implementation starts only after all steps are atomic, testable, and unambiguous.

4. Implement to Production Standard
- Use contract-first, deterministic, fail-closed behavior.
- Enforce strict semantics (no truthy coercion for boolean gates).
- Keep error tokens stable and explicit.
- Add or update unit and integration tests for each behavior change.

5. Verify and Gate
- Run scoped tests for touched modules.
- Run integration and regression checks for affected runtime paths.
- Resolve lint and type issues introduced by the change.
- Confirm no DoD item remains open before marking complete.

## Google-Grade Definition of Done (100%)
A task is 100% done only if all conditions below are true.

- Correctness
  - behavior exactly matches the approved atomic spec
  - edge cases and failure modes are covered
  - no unresolved defects remain in touched scope

- Test Evidence
  - all required unit and integration tests pass
  - negative tests prove fail-closed behavior
  - deterministic outputs are validated where relevant

- Contract Integrity
  - schema and semantic invariants are enforced
  - status fields align with gate and check fields
  - malformed inputs are rejected with stable error tokens

- Production Readiness
  - safety checks, rollout constraints, and rollback path are explicit
  - observability and diagnostics remain intact for touched paths
  - no TODO placeholders or silent degradations in core logic

- Documentation
  - execution spec in `docs/` reflects final shipped behavior
  - completion notes record evidence, not intent

If any item fails, task state is **not done**.

## Non-Negotiable Rule
SDE must never report completion unless the full DoD above is satisfied with concrete test evidence.
