# Benchmark orchestration jsonl

## Context
- [x] Verified feature scope and baseline (`60%`) in `docs/master-architecture-feature-completion.md`.
- [x] Verified canonical contracts in `orchestration_benchmark_jsonl_contract.py`.
- [x] Verified producer call-sites in `run_benchmark.py` for `benchmark_resume` and `benchmark_error` lines.

## Assumptions and Constraints
- [x] Scope is local line-level contract strictness for benchmark orchestration JSONL rows.
- [x] Contracts should fail closed on bool-as-int ambiguity, unknown keys, and blank error messages.
- [x] Producer payload shapes should remain unchanged and contract-compliant.

## Phase 0 — Preconditions
- [x] Confirmed existing tests covered happy path and some negative branches.
- [x] Confirmed resume pending count accepted bool values.
- [x] Confirmed error message allowed empty string and unknown keys were accepted for both line types.

## Phase 1 — Contracts and Interfaces
- [x] Added allowed-key enforcement for `benchmark_resume` and `benchmark_error` lines.
- [x] Hardened `pending_task_count` to reject bool values.
- [x] Hardened `error_message` to require non-empty string.
- [x] Preserved contract IDs and existing required fields (`run_id`, `type`, `pending_task_count` / `error_type`, `error_message`).

## Phase 2 — Core Implementation
- [x] Updated `validate_orchestration_benchmark_resume_dict` with bool + unknown-key fail-closed checks.
- [x] Updated `validate_orchestration_benchmark_error_dict` with non-empty message + unknown-key fail-closed checks.
- [x] Kept benchmark producer (`run_benchmark.py`) payload shape stable and valid under stricter validation.

## Phase 3 — Safety and Failure Handling
- [x] Added negative test for bool pending count.
- [x] Added negative test for unknown key on `benchmark_resume`.
- [x] Converted empty error-message expectation to rejection.
- [x] Added negative test for unknown key on `benchmark_error`.

## Phase 4 — Verification and Observability
- [x] Expanded benchmark orchestration contract tests in `test_orchestration_benchmark_jsonl_contract.py`.
- [x] Re-ran validate-run API integration checks in `test_validate_run_api.py`.
- [x] Re-ran CLI coverage in `test_cli.py`.
- [x] Executed focused verification:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_orchestration_benchmark_jsonl_contract.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_validate_run_api.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_cli.py`
  - [x] Result: `33 passed`.

## Definition of Done
- [x] `benchmark_resume` and `benchmark_error` line contracts reject unknown keys.
- [x] Resume pending counts reject bool values.
- [x] Error message requires non-empty string.
- [x] Unit and integration suites pass with stricter fail-closed behavior.
- [x] Feature checklist is complete for repo-local scope.

## Test Cases
### Unit
- [x] `test_validate_benchmark_resume_ok`.
- [x] `test_validate_benchmark_resume_rejects_bool_pending`.
- [x] `test_validate_benchmark_resume_rejects_unknown_keys`.
- [x] `test_validate_benchmark_error_ok`.
- [x] `test_validate_benchmark_error_empty_message_rejected`.
- [x] `test_validate_benchmark_error_rejects_unknown_keys`.

### Integration
- [x] `test_validate_run_api.py` remains green.
- [x] `test_cli.py` remains green.

### Negative
- [x] Existing wrong-type and bad-pending tests remain green.
- [x] Existing blank-error-type test remains green.

### Regression
- [x] Contract IDs remain stable (`sde.orchestration_benchmark_resume.v1`, `sde.orchestration_benchmark_error.v1`).
- [x] Existing producer line writes in benchmark flow remain valid.

## Out of Scope
- [x] Cross-repository orchestration event buses and centralized event governance.
- [x] Production control-plane event ingestion beyond local line contract enforcement.
