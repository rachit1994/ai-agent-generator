# Learning Lineage

## Context
- [x] Confirmed scope and baseline (`30%`) from `docs/master-architecture-feature-completion.md`.
- [x] Audited evolution lineage hard-stops in `hard_stops_evolution.py` (HS25–HS28).
- [x] Identified lineage gap: HS27 only validated `task_spec.gap_detection_ref` and ignored `evaluation_result` contract shape.

## Assumptions and Constraints
- [x] Scope is repo-local lineage completeness through hard-stop validation and artifact contracts.
- [x] Practice/evaluation linkage should fail closed when evaluation evidence is malformed or lacks a boolean pass/fail outcome.
- [x] Existing HS25/HS26/HS28 contract checks should remain unchanged.

## Phase 0 — Preconditions
- [x] Verified HS27 required both files to exist but did not parse/validate `evaluation_result`.
- [x] Verified existing tests covered HS25/HS26/HS28 but had no HS27 negative cases for malformed eval payload.
- [x] Verified evolution harness emits `evaluation_result.json` with `passed` boolean on happy path.

## Phase 1 — Contracts and Interfaces
- [x] Hardened HS27 contract semantics:
  - [x] parse both `task_spec.json` and `evaluation_result.json`
  - [x] require both JSON payloads to be objects
  - [x] require non-empty string `gap_detection_ref`
  - [x] require `evaluation_result.passed` to be boolean
- [x] Preserved HS27 artifact paths and hard-stop ID wiring.

## Phase 2 — Core Implementation
- [x] Updated `_hs27_practice_gap` to validate evaluation-result object shape and boolean `passed`.
- [x] Kept file-existence gate behavior unchanged.
- [x] Left HS25/HS26/HS28 logic untouched.

## Phase 3 — Safety and Failure Handling
- [x] Added negative case where `evaluation_result.json` is non-object (`[]`).
- [x] Added negative case where `evaluation_result.passed` is not boolean (`"yes"`).
- [x] Confirmed HS27 now fails closed on malformed lineage evaluation evidence.

## Phase 4 — Verification and Observability
- [x] Added HS27 negative tests in `test_evolution_organization_hard_stops.py`.
- [x] Re-ran focused suites:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_evolution_organization_hard_stops.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_hard_stop_schedule.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_public_export_surface.py`
  - [x] Result: `224 passed`.

## Definition of Done
- [x] HS27 validates both practice specification and evaluation-result evidence with typed fields.
- [x] Malformed lineage evaluation evidence fails closed deterministically.
- [x] Focused evolution/schedule/export suites remain green and lint-clean.

## Test Cases
### Unit
- [x] `test_hs27_fails_when_evaluation_result_not_object`.
- [x] `test_hs27_fails_when_evaluation_result_missing_passed_bool`.
- [x] Existing HS25/HS26/HS28 tests remain green.

### Integration
- [x] `test_hard_stop_schedule.py` remains green with tightened HS27 behavior.

### Negative
- [x] Non-object `evaluation_result.json` fails HS27.
- [x] Non-boolean `evaluation_result.passed` fails HS27.

### Regression
- [x] Organization hard-stop tests remain green after evolution hard-stop tightening.
- [x] Public export/import migration surface remains green.

## Out of Scope
- [x] Distributed learning lineage graph services and cross-repo lineage federation.
- [x] Production control-plane evaluation governance beyond local artifact contracts.
