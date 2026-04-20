# Orchestration run error line

## Context
- [x] Verified feature scope and baseline (`62%`) in `docs/master-architecture-feature-completion.md`.
- [x] Verified canonical run-error contract in `orchestration_run_error_contract.py`.
- [x] Verified producer call-sites in `single_task.py` for immediate-failure and parse-failure paths.

## Assumptions and Constraints
- [x] Scope is local `orchestration.jsonl` `run_error` line contract strictness.
- [x] Contract should fail closed on blank `error_message` and emit deterministic unknown-key tokens.
- [x] Producer behavior and payload fields should remain unchanged and contract-compliant.

## Phase 0 — Preconditions
- [x] Confirmed existing tests covered happy path, unknown key, bad mode, and blank detail branches.
- [x] Confirmed empty `error_message` was previously accepted.
- [x] Confirmed unknown-key reporting was generic (`unknown_keys`) rather than per-key deterministic tokens.

## Phase 1 — Contracts and Interfaces
- [x] Tightened unknown-key reporting to key-specific token format.
- [x] Tightened `error_message` validation to require non-empty string.
- [x] Preserved run id/type/mode/error type/detail requirements and allowed keys set.

## Phase 2 — Core Implementation
- [x] Updated `validate_orchestration_run_error_dict` unknown-key handling to per-key tokens.
- [x] Updated message-field validation to reject blank `error_message`.
- [x] Kept `single_task` error-line producer payload shapes unchanged.

## Phase 3 — Safety and Failure Handling
- [x] Updated unknown-key test to assert deterministic token with offending key name.
- [x] Added negative test for empty `error_message`.
- [x] Updated prior “ok with detail” fixture to use non-empty error message.

## Phase 4 — Verification and Observability
- [x] Expanded run-error contract tests in `test_orchestration_run_error_contract.py`.
- [x] Re-ran validate-run API integration checks in `test_validate_run_api.py`.
- [x] Re-ran CLI integration checks in `test_cli.py`.
- [x] Executed focused verification:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_orchestration_run_error_contract.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_validate_run_api.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_cli.py`
  - [x] Result: `29 passed`.

## Definition of Done
- [x] Run-error contract rejects blank `error_message`.
- [x] Unknown keys produce deterministic per-key error tokens.
- [x] Single-task failure paths remain green with stricter contract enforcement.
- [x] Feature checklist is complete for repo-local scope.

## Test Cases
### Unit
- [x] `test_validate_run_error_ok_minimal`.
- [x] `test_validate_run_error_ok_with_detail`.
- [x] `test_validate_run_error_unknown_key`.
- [x] `test_validate_run_error_empty_message_rejected`.
- [x] Existing bad-mode and blank-detail negatives remain green.

### Integration
- [x] `test_validate_run_api.py` remains green.
- [x] `test_cli.py` remains green.

### Negative
- [x] Unknown keys fail with key-specific token (`orchestration_run_error_unknown_key:<key>`).
- [x] Blank `error_message` fails closed.

### Regression
- [x] Contract ID remains stable (`sde.orchestration_run_error.v1`).
- [x] Existing `single_task` run-error producer paths remain valid.

## Out of Scope
- [x] Cross-repository orchestration event harmonization.
- [x] Control-plane orchestration governance beyond local contract enforcement.
