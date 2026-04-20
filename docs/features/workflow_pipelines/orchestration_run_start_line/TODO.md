# Orchestration run start line

## Context
- [x] Verified feature scope and baseline (`62%`) in `docs/master-architecture-feature-completion.md`.
- [x] Verified canonical run-start contract in `orchestration_run_start_contract.py`.
- [x] Verified append-path integration in `persist_traces.append_orchestration_run_start`.

## Assumptions and Constraints
- [x] Scope is local `orchestration.jsonl` `run_start` line contract strictness.
- [x] Contract should fail closed for unknown keys, not just malformed known fields.
- [x] Producer output shape should remain unchanged and valid.

## Phase 0 — Preconditions
- [x] Confirmed existing tests covered happy path, bad mode, and bad type branches.
- [x] Confirmed unknown keys were previously accepted.
- [x] Confirmed append path already validates before writing.

## Phase 1 — Contracts and Interfaces
- [x] Added explicit allowed-key enforcement to run-start contract.
- [x] Added stable token format for unknown keys (`orchestration_run_start_unknown_key:<key>`).
- [x] Preserved required fields and mode/type/value semantics.

## Phase 2 — Core Implementation
- [x] Hardened `validate_orchestration_run_start_dict` with unknown key rejection.
- [x] Kept `append_orchestration_run_start` payload unchanged and contract-compliant.
- [x] Preserved downstream `orchestration.jsonl` write behavior.

## Phase 3 — Safety and Failure Handling
- [x] Added negative test for unknown-key rejection.
- [x] Confirmed existing bad-mode and bad-type paths remain fail-closed.
- [x] Confirmed integration write path still succeeds for valid lines.

## Phase 4 — Verification and Observability
- [x] Expanded run-start contract tests in `test_orchestration_run_start_contract.py`.
- [x] Re-ran validate-run API integration checks in `test_validate_run_api.py`.
- [x] Re-ran public export surface checks in `test_public_export_surface.py`.
- [x] Executed focused verification:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_orchestration_run_start_contract.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_validate_run_api.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_public_export_surface.py`
  - [x] Result: `218 passed`.

## Definition of Done
- [x] Run-start contract rejects unknown keys with stable error tokens.
- [x] Valid run-start lines continue to serialize and append successfully.
- [x] Unit and integration checks pass with stricter validation behavior.
- [x] Feature checklist is complete for repo-local scope.

## Test Cases
### Unit
- [x] `test_validate_orchestration_run_start_ok`.
- [x] `test_validate_orchestration_run_start_bad_mode`.
- [x] `test_validate_orchestration_run_start_bad_type`.
- [x] `test_validate_orchestration_run_start_rejects_unknown_keys`.

### Integration
- [x] `test_append_orchestration_run_start_writes_valid_line`.
- [x] `test_validate_run_api.py` suite remains green.

### Negative
- [x] Unknown-key payloads fail with `orchestration_run_start_unknown_key:<key>`.
- [x] Invalid mode/type payloads still fail as expected.

### Regression
- [x] Contract ID remains stable (`sde.orchestration_run_start.v1`).
- [x] Existing producer payload shape remains valid under stricter contract.

## Out of Scope
- [x] Cross-repository orchestration bus standards.
- [x] Control-plane orchestration runtime governance beyond local contract enforcement.
