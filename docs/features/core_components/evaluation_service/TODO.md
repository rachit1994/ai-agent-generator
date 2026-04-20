# Evaluation Service

## Context
- [x] Confirmed scope and baseline (`61%`) from `docs/master-architecture-feature-completion.md`.
- [x] Audited offline evaluation logic in `evaluation_framework/offline_evaluation/sde_eval/eval.py`.
- [x] Identified fail-open gap: `root_cause_distribution` coerced non-string `failure_reason` values into arbitrary string buckets (`"True"`, `"404"`) instead of failing closed to `unknown_failure`.

## Assumptions and Constraints
- [x] Root-cause analytics should only accept meaningful non-empty string reason codes.
- [x] Malformed metadata should aggregate under canonical `unknown_failure`.
- [x] Existing valid reason strings should be preserved unchanged.

## Phase 0 — Preconditions
- [x] Verified non-string `failure_reason` values were stringified and counted as distinct reasons.
- [x] Verified this could pollute failure taxonomy and downstream gating insights.
- [x] Verified no unit test covered non-string reason rejection.

## Phase 1 — Contracts and Interfaces
- [x] Tightened reason extraction contract in `root_cause_distribution`:
  - [x] accept only non-empty strings (trimmed)
  - [x] reject non-strings/blank strings into `unknown_failure`
- [x] Preserved finalize-stage filtering behavior.

## Phase 2 — Core Implementation
- [x] Replaced permissive `str(reason)` coercion with strict typed branch.
- [x] Added normalization via `.strip()` for accepted reason strings.
- [x] Added explicit fallback counter path for malformed reasons.

## Phase 3 — Safety and Failure Handling
- [x] Added negative unit test for bool/int/blank reason values.
- [x] Confirmed malformed reasons collapse to single canonical bucket.
- [x] Confirmed valid reason extraction remains stable.

## Phase 4 — Verification and Observability
- [x] Added test: `test_root_cause_distribution_rejects_non_string_failure_reason`.
- [x] Ran focused suites:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_eval.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_public_export_surface.py`
  - [x] Result: `217 passed`.

## Definition of Done
- [x] Root-cause distribution now fail-closes malformed `failure_reason` values.
- [x] Unit coverage protects against taxonomy pollution regressions.
- [x] Evaluation + public export focused suites are green.

## Test Cases
### Unit
- [x] Valid string failure reasons are counted by normalized label.
- [x] Non-string/blank reasons map to `unknown_failure`.
- [x] Non-finalize events remain excluded.

### Integration
- [x] Evaluation module integration tests remain green.
- [x] Public API surface exports remain stable.

### Negative
- [x] Bool/int reasons no longer create spurious buckets.
- [x] Blank-string reasons no longer create empty-label buckets.

### Regression
- [x] Existing root-cause distribution tests remain green.
- [x] Existing eval decision tests remain green.

## Out of Scope
- [x] Introduction of a centralized failure-reason taxonomy service.
- [x] Migration/backfill of historical artifacts with malformed failure reasons.
