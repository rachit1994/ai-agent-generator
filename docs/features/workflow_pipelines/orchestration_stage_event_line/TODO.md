# Orchestration stage event line

## Context
- [x] Verified feature scope and baseline (`63%`) in `docs/master-architecture-feature-completion.md`.
- [x] Verified canonical stage-event contract in `orchestration_stage_event_contract.py`.
- [x] Verified producer integration in `persist_traces.append_orchestration_stage_events`.

## Assumptions and Constraints
- [x] Scope is local `orchestration.jsonl` stage-event line contract strictness.
- [x] Contract should fail closed on bool-as-int numeric ambiguity and unknown keys.
- [x] Producer payload shape should remain unchanged and pass stricter validation.

## Phase 0 — Preconditions
- [x] Confirmed existing tests covered happy path and selected negative branches.
- [x] Confirmed bool values were accepted in `retry_count`, `latency_ms`, and `attempt`.
- [x] Confirmed unknown top-level keys were accepted.

## Phase 1 — Contracts and Interfaces
- [x] Added explicit allowed-key enforcement for flattened stage-event lines.
- [x] Hardened `retry_count` to reject bool values.
- [x] Hardened `latency_ms` to reject bool values.
- [x] Hardened `attempt` to reject bool values when present.
- [x] Preserved required stage-event fields and existing metadata behavior.

## Phase 2 — Core Implementation
- [x] Updated `validate_orchestration_stage_event_line_dict` with unknown-key checks.
- [x] Updated numeric validations to treat bool as invalid.
- [x] Kept `append_orchestration_stage_events` payload format stable and contract-compliant.

## Phase 3 — Safety and Failure Handling
- [x] Added negative test for bool misuse in numeric fields.
- [x] Added negative test for unknown key rejection.
- [x] Confirmed existing bad errors/latency branches remain fail-closed.

## Phase 4 — Verification and Observability
- [x] Expanded stage-event contract tests in `test_orchestration_stage_event_contract.py`.
- [x] Re-ran export surface compatibility checks in `test_public_export_surface.py`.
- [x] Executed focused verification:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_orchestration_stage_event_contract.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_public_export_surface.py`
  - [x] Result: `212 passed`.

## Definition of Done
- [x] Stage-event contract rejects unknown keys and bool-valued numeric fields.
- [x] Valid producer stage-event rows continue to append successfully.
- [x] Unit and integration suites pass with stricter fail-closed behavior.
- [x] Feature checklist is complete for repo-local scope.

## Test Cases
### Unit
- [x] `test_validate_stage_event_line_ok_minimal`.
- [x] `test_validate_stage_event_line_rejects_bool_numeric_fields`.
- [x] `test_validate_stage_event_line_rejects_unknown_keys`.
- [x] Existing bad-errors and bad-latency tests remain green.

### Integration
- [x] `test_append_orchestration_stage_events_writes_lines`.
- [x] `test_public_export_surface.py` remains green.

### Negative
- [x] Existing fail-closed error-list and latency branches remain enforced.
- [x] Unknown keys and bool numeric fields now fail with stable tokens.

### Regression
- [x] Contract ID remains stable (`sde.orchestration_stage_event.v1`).
- [x] Existing flattened stage-event write path remains valid.

## Out of Scope
- [x] Cross-repository orchestration event standardization.
- [x] Production control-plane event governance beyond local contract enforcement.
