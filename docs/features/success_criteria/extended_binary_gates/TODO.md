# Extended Binary Gates

## Context
- [x] Confirmed scope and baseline (`14%`) from `docs/master-architecture-feature-completion.md`.
- [x] Audited extended binary decision surface in `evaluation_framework/offline_evaluation/sde_eval/eval.py` (`strict_gate_decision`).
- [x] Identified fail-closed gap: NaN/inf threshold and ROI inputs were accepted and could poison gate checks.

## Assumptions and Constraints
- [x] Scope is repo-local binary gate determinism under malformed numeric threshold input.
- [x] Threshold and ROI fields must sanitize to safe defaults when non-finite.
- [x] Existing decision/check/threshold output schema must stay stable.

## Phase 0 — Preconditions
- [x] Verified no dedicated tests for non-finite (`NaN`) binary-gate threshold arguments.
- [x] Verified `_to_float` did not previously reject non-finite values.
- [x] Verified exported evaluation function surface is used in regression suites.

## Phase 1 — Contracts and Interfaces
- [x] Hardened numeric coercion contract:
  - [x] reject non-finite floats (NaN/inf) to default fallback
  - [x] continue rejecting bool for numeric coercion
- [x] Hardened binary-gate threshold ingestion:
  - [x] sanitize `pass_threshold_points`
  - [x] sanitize `reliability_threshold_points`
  - [x] sanitize `max_latency_overhead_percent`
  - [x] sanitize `roi_base_case`

## Phase 2 — Core Implementation
- [x] Added `math.isfinite` guard in `_to_float`.
- [x] Updated `strict_gate_decision` to always use sanitized threshold and ROI scalars.
- [x] Preserved return shape for `checks`, `metrics`, and `thresholds`.

## Phase 3 — Safety and Failure Handling
- [x] Added test proving NaN thresholds/ROI are coerced to defaults.
- [x] Confirmed malformed non-finite input yields conservative ROI check (`False`).
- [x] Confirmed gate still produces deterministic decision output without exceptions.

## Phase 4 — Verification and Observability
- [x] Expanded `test_eval.py` with non-finite threshold coverage.
- [x] Ran focused suites:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_eval.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_public_export_surface.py`
  - [x] Result: `216 passed`.

## Definition of Done
- [x] Extended binary gate thresholds are fail-closed for non-finite values.
- [x] ROI gating no longer accepts non-finite inputs.
- [x] Focused eval/export suites are green and lint-clean.

## Test Cases
### Unit
- [x] `test_strict_gate_decision_fails_closed_on_malformed_threshold_arguments`.
- [x] Existing `strict_gate_decision` and `verdict_for` coverage remains green.

### Integration
- [x] `test_public_export_surface.py` remains green with unchanged evaluation exports.

### Negative
- [x] NaN threshold/ROI inputs are coerced to safe defaults and no longer poison gating logic.

### Regression
- [x] Existing binary gate decision behavior remains intact for well-formed inputs.

## Out of Scope
- [x] Production rollout policy orchestration and external release approval systems.
- [x] Enterprise KPI governance and alerting workflows outside repo-local evaluator logic.
