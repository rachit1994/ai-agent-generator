# Error Reduction Metrics

## Context
- [x] Confirmed scope and baseline (`18%`) from `docs/master-architecture-feature-completion.md`.
- [x] Audited error-reduction evaluation utilities in `evaluation_framework/offline_evaluation/sde_eval/eval.py`.
- [x] Identified fail-closed gap: `verdict_for` and `strict_gate_decision` assumed well-formed metric dicts and could crash on missing/malformed fields.

## Assumptions and Constraints
- [x] Scope is repo-local error-reduction evaluation robustness for malformed metric inputs.
- [x] Decision helpers should degrade safely to conservative outcomes (`rejected` / `stop`) instead of throwing.
- [x] Existing function names/return shapes must remain compatible with current imports and call sites.

## Phase 0 — Preconditions
- [x] Verified aggregate/error-distribution functions already had basic malformed-row handling coverage.
- [x] Verified no direct tests for malformed metric dict inputs to `verdict_for` and `strict_gate_decision`.
- [x] Verified `_to_int`/`_to_float` accepted bool values via Python coercion (`True -> 1`), which is undesirable for fail-closed scoring.

## Phase 1 — Contracts and Interfaces
- [x] Hardened scalar coercion contract:
  - [x] bool is treated as invalid numeric input
  - [x] missing/malformed scalar metric fields are coerced to safe defaults
- [x] Hardened decision helper contract:
  - [x] `verdict_for` now uses safe, typed extraction from metric dicts
  - [x] `strict_gate_decision` now uses safe, typed extraction from metric dicts
- [x] Preserved output schemas for both functions.

## Phase 2 — Core Implementation
- [x] Updated `_to_int` and `_to_float` to reject bool.
- [x] Refactored `verdict_for` to use `_to_float`/`_to_int` + `.get(...)` across required metrics.
- [x] Refactored `strict_gate_decision` to use safe extracted baseline/guarded metrics before computing deltas.

## Phase 3 — Safety and Failure Handling
- [x] Added negative test that malformed/missing metrics return conservative `rejected` verdict.
- [x] Added negative test that malformed/missing metrics return conservative `stop` gate decision.
- [x] Confirmed no crashes for malformed input dictionaries.

## Phase 4 — Verification and Observability
- [x] Expanded `test_eval.py` with malformed metric-input coverage.
- [x] Ran focused suites:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_eval.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_public_export_surface.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_replay.py`
  - [x] Result: `221 passed`.

## Definition of Done
- [x] Error-reduction decision helpers are fail-closed for malformed metric dicts.
- [x] Bool leakage into numeric metrics is blocked at coercion helpers.
- [x] Focused eval + regression suites are green and lint-clean.

## Test Cases
### Unit
- [x] `test_verdict_for_fails_closed_on_missing_or_malformed_metrics`.
- [x] `test_strict_gate_decision_fails_closed_on_malformed_or_missing_fields`.
- [x] Existing eval unit tests remain green.

### Integration
- [x] `test_replay.py` remains green with updated metric helper semantics.
- [x] `test_public_export_surface.py` remains green with unchanged exported symbols.

### Negative
- [x] Missing keys and malformed values no longer crash `verdict_for` and `strict_gate_decision`.

### Regression
- [x] Existing pass/fail threshold behavior remains intact for well-formed metrics.
- [x] Evaluation utilities remain import-compatible across migration surface tests.

## Out of Scope
- [x] Production KPI collection pipelines and organization-wide SLO governance.
- [x] External dashboarding/reporting systems for longitudinal error-reduction tracking.
