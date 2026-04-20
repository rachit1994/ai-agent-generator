# Stability Metrics

## Context
- [x] Confirmed scope and baseline (`28%`) from `docs/master-architecture-feature-completion.md`.
- [x] Audited stability metric computation in `risk_budgets/metrics_helpers.py`.
- [x] Identified fail-closed gap: malformed numeric fields could raise exceptions during metric aggregation.

## Assumptions and Constraints
- [x] Scope is repo-local stability score robustness from finalize trace events.
- [x] Metrics computation should fail closed (coerce malformed numerics to safe zeros) instead of crashing.
- [x] Existing export surface and gate interfaces (`metrics_from_events`, `reliability_gate`) must remain unchanged.

## Phase 0 — Preconditions
- [x] Verified no dedicated behavior tests for `metrics_from_events` malformed input handling.
- [x] Verified current implementation directly casted values via `int(...)`/`float(...)`, allowing runtime `ValueError`.
- [x] Verified public export contract includes `metrics_from_events` and `reliability_gate`.

## Phase 1 — Contracts and Interfaces
- [x] Added stable coercion semantics:
  - [x] bool is rejected for numeric fields and treated as zero
  - [x] malformed strings become zero
  - [x] empty strings become zero
  - [x] valid numeric strings still parse
- [x] Preserved returned metrics shape and key names.

## Phase 2 — Core Implementation
- [x] Added `_to_int_or_zero` helper.
- [x] Added `_to_float_or_zero` helper.
- [x] Updated `metrics_from_events` to use safe numeric coercion for reliability, latency, cost, validity, and retries.
- [x] Preserved `reliability_gate` behavior.

## Phase 3 — Safety and Failure Handling
- [x] Added negative/robustness coverage for malformed numerics (`"n/a"`, `"bad"`, bools).
- [x] Added coverage for empty finalize slice returning zero-profile metrics.
- [x] Confirmed function now computes deterministically without exceptions on malformed event payloads.

## Phase 4 — Verification and Observability
- [x] Added `test_metrics_helpers.py` unit suite.
- [x] Ran focused suites:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_metrics_helpers.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_public_export_surface.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_project_status.py`
  - [x] Result: `240 passed`.

## Definition of Done
- [x] Stability metrics aggregation is fail-closed for malformed numeric trace fields.
- [x] Reliability gating remains compatible with existing call sites.
- [x] Focused metrics + regression suites are green and lint-clean.

## Test Cases
### Unit
- [x] `test_metrics_from_events_fails_closed_for_malformed_numeric_fields`.
- [x] `test_metrics_from_events_empty_finalize_slice_returns_zero_profile`.

### Integration
- [x] `test_project_status.py` remains green.
- [x] `test_public_export_surface.py` remains green with unchanged exported names.

### Negative
- [x] Malformed latency/cost/retry/reliability/validity fields no longer crash computation.

### Regression
- [x] Metric output keys and gate functions are still publicly importable.

## Out of Scope
- [x] Production KPI dashboarding, alerting, and historical trend warehousing.
- [x] Full SLO control-plane with automated budget enforcement.
