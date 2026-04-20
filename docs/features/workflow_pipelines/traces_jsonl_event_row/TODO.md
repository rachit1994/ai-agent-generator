# Traces jsonl event row

## Context
- [x] Verified feature scope and baseline (`64%`) in `docs/master-architecture-feature-completion.md`.
- [x] Verified canonical traces row contract in `traces_jsonl_event_contract.py`.
- [x] Verified producer/consumer validation integration in `run_benchmark.py` and `persist_traces.py`.

## Assumptions and Constraints
- [x] Scope is local event-row contract strictness and fail-closed validation behavior.
- [x] Numeric fields must reject bool values to avoid Python `bool` as `int` edge-case acceptance.
- [x] Changes must preserve compatibility with `TraceEvent.to_dict()` payloads.

## Phase 0 — Preconditions
- [x] Confirmed existing tests covered happy path, unknown keys, and basic negative branches.
- [x] Confirmed numeric validation allowed bool values for latency/tokens/cost/retry/score metrics.
- [x] Confirmed benchmark + traces persist paths already enforce this contract.

## Phase 1 — Contracts and Interfaces
- [x] Hardened `latency_ms`, `token_input`, `token_output` to reject bools.
- [x] Hardened `estimated_cost_usd` to reject bools.
- [x] Hardened `retry_count` to reject bools.
- [x] Hardened score metric numeric checks (`reliability`, `validity`) to reject bools.
- [x] Preserved contract ID and all existing required fields.

## Phase 2 — Core Implementation
- [x] Updated validation internals in `validate_traces_jsonl_event_dict` helper branches.
- [x] Kept producer paths unchanged (`run_benchmark`/`persist_traces`) and compatible.
- [x] Preserved current mode and schema semantics while tightening numeric validation.

## Phase 3 — Safety and Failure Handling
- [x] Added unit negative test that exercises bool misuse across all numeric fields.
- [x] Confirmed invalid rows still raise fail-closed errors through `persist_traces`.
- [x] Confirmed orchestration-stage event suite still green after stricter traces validation.

## Phase 4 — Verification and Observability
- [x] Expanded traces row contract tests in `test_traces_jsonl_event_contract.py`.
- [x] Re-ran benchmark integration checks in `test_benchmark_harvest.py`.
- [x] Re-ran orchestration stage contract checks in `test_orchestration_stage_event_contract.py`.
- [x] Executed focused verification:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_traces_jsonl_event_contract.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_benchmark_harvest.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_orchestration_stage_event_contract.py`
  - [x] Result: `18 passed`.

## Definition of Done
- [x] Traces event row contract rejects bool-valued numeric fields across timing, tokens, cost, retries, and score metrics.
- [x] Contract consumers in benchmark/persist flows remain green.
- [x] Unit and integration suites cover newly hardened fail-closed branches.
- [x] Feature checklist is complete for repo-local scope.

## Test Cases
### Unit
- [x] `test_validate_traces_jsonl_event_ok_from_trace_event`.
- [x] `test_validate_traces_jsonl_event_rejects_bool_numeric_fields`.
- [x] Existing unknown-key/mode/errors-item negatives remain green.

### Integration
- [x] `test_persist_traces_raises_on_invalid_event`.
- [x] `test_persist_traces_writes_valid_line`.
- [x] `test_benchmark_harvest.py` remains green with strict traces validation.

### Negative
- [x] Bool misuse in numeric fields is rejected with stable tokens.
- [x] Existing fail-closed path for malformed events remains enforced.

### Regression
- [x] Contract ID remains stable (`sde.traces_jsonl_event.v1`).
- [x] Existing `TraceEvent.to_dict()` happy path remains valid.

## Out of Scope
- [x] Cross-repository telemetry standards and external log pipeline ingestion.
- [x] Control-plane rollout policies beyond local traces contract enforcement.
