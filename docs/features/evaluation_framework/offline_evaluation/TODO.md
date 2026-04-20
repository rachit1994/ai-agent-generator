# Offline evaluation

## Context
- [x] Verified feature scope and baseline (`62%`) in `docs/master-architecture-feature-completion.md`.
- [x] Verified offline metrics implementation in `src/evaluation_framework/offline_evaluation/sde_eval/eval.py`.
- [x] Verified benchmark summary integration in `src/workflow_pipelines/production_pipeline_plan_artifact/production_pipeline_task_to_promote/benchmark/summary_payload.py`.

## Assumptions and Constraints
- [x] Scope is repo-local offline evaluation correctness, fail-closed behavior, and benchmark summary semantics.
- [x] Malformed events must not crash metrics aggregation and must not inflate results.
- [x] Cross-mode deltas (`baseline` vs `guarded`) are meaningful only when both finalize events exist.

## Phase 0 — Preconditions
- [x] Confirmed existing tests covered only limited happy paths for `aggregate_metrics`, `verdict_for`, and `strict_gate_decision`.
- [x] Confirmed missing robustness coverage for malformed/non-dict events and malformed numeric fields.
- [x] Confirmed `summary_payload` lacked direct unit tests for single-mode delta semantics.

## Phase 1 — Contracts and Interfaces
- [x] Added fail-closed input normalization helpers in `eval.py` (`_as_dict`, `_to_int`, `_to_float`).
- [x] Formalized event parsing semantics: non-dict events and malformed fields coerce to safe defaults.
- [x] Formalized per-task delta semantics in `summary_payload.py`: deltas are `None` unless both modes have finalize rows.

## Phase 2 — Core Implementation
- [x] Hardened `aggregate_metrics` against malformed `events`, `score`, and numeric fields.
- [x] Hardened `root_cause_distribution` against malformed `metadata`.
- [x] Hardened `stage_latency_breakdown` against malformed event rows and non-numeric latency values.
- [x] Updated `build_summary` to avoid synthetic cross-mode deltas in single-mode runs.

## Phase 3 — Safety and Failure Handling
- [x] Added negative-path unit coverage for malformed event rows in metrics aggregation.
- [x] Added negative-path unit coverage for malformed metadata in root-cause distribution.
- [x] Added negative-path unit coverage for malformed latency rows in stage latency breakdown.
- [x] Added summary-level guard test for baseline-only runs to prevent fabricated deltas.

## Phase 4 — Verification and Observability
- [x] Added focused benchmark summary tests in `test_offline_summary_payload.py`.
- [x] Expanded eval robustness tests in `test_eval.py`.
- [x] Executed targeted verification:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_eval.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_offline_summary_payload.py`
  - [x] Result: `10 passed`.

## Definition of Done
- [x] Offline eval metric functions are fail-closed for malformed event data.
- [x] Benchmark per-task deltas no longer report fabricated comparisons in single-mode runs.
- [x] New unit tests cover malformed-input safety and per-task summary semantics.
- [x] Focused offline-eval test suite is green.

## Test Cases
### Unit
- [x] `test_aggregate_metrics_fail_closed_on_malformed_events`.
- [x] `test_root_cause_distribution_uses_unknown_failure_for_malformed_metadata`.
- [x] `test_stage_latency_breakdown_ignores_malformed_rows`.

### Integration
- [x] `test_build_summary_single_mode_has_no_cross_mode_deltas`.
- [x] `test_build_summary_both_mode_has_deltas_when_both_finalize_exist`.

### Negative
- [x] Non-dict events do not crash aggregate metrics.
- [x] Malformed score/latency/cost/retry fields fail closed to safe defaults.
- [x] Malformed metadata falls back to `unknown_failure` rather than raising.

### Regression
- [x] Existing aggregate/verdict/strict-gate tests remain green.
- [x] New summary-payload tests validate both baseline-only and both-mode semantics.
- [x] Targeted suite remains green (`10 passed`).

## Out of Scope
- [x] Hosted/distributed offline evaluation service runtime.
- [x] Organization-wide governance and control-plane orchestration beyond repo-local execution.
