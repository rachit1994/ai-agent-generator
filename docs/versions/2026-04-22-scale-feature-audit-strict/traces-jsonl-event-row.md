# Traces JSONL event row (one-feature execution packet)

## Map
- Feature: `Traces JSONL event row`
- Baseline: 34%
- Target: 100% with executable runtime evidence, fail-closed contracts, and deterministic tests.

## Gap
- Runtime status/check logic existed but execution-level ingestion telemetry was missing.
- No explicit accounting for malformed/invalid trace rows and run-id mismatch counts.
- Contracts did not require execution payload validation.

## Red
- Added failing assertions for execution payload presence in output artifacts.
- Added runtime regression for run-id mismatch counting.

## Green
- Implemented `execute_traces_jsonl_runtime` in:
  - `src/workflow_pipelines/traces_jsonl/runtime.py`
- Runtime now emits:
  - `rows_processed`
  - `malformed_rows`
  - `invalid_row_indices`
  - `run_id_mismatch_rows`
- Wired execution output into `build_traces_jsonl_event_row_runtime`.
- Extended contract validation in:
  - `src/workflow_pipelines/traces_jsonl/contracts.py`
  - requires typed execution fields and fail-closed invariants.
- Exported runtime function in:
  - `src/workflow_pipelines/traces_jsonl/__init__.py`

## Harden
- Expanded deterministic tests in:
  - `src/workflow_pipelines/traces_jsonl/tests/test_runtime.py`
- Preserved existing status/check/count semantics while adding execution-level assertions.

## Evidence
- Test command:
  - `uv run pytest src/workflow_pipelines/traces_jsonl/tests/test_runtime.py`
- Result:
  - `7 passed`

## Score
- Updated `docs/master-architecture-feature-completion.md`:
  - `Traces JSONL event row` moved from `34` to `100`.

## Review
- Feature now includes executable runtime ingestion telemetry, schema-enforced execution payloads, and deterministic regression coverage.
- Backend indexing/query/retention controls remain out of scope and do not block local completion criteria.
