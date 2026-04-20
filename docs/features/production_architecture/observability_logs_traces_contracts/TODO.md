# Observability logs traces contracts

## Context
- [x] Verified feature scope and baseline (`48%`) in `docs/master-architecture-feature-completion.md`.
- [x] Verified Stage 1 observability export contract surface in `project_stage1_observability_export.py`.
- [x] Focused closure on fail-closed schema strictness for observability export payloads.

## Assumptions and Constraints
- [x] Scope is local observability artifact contract strictness and deterministic validation behavior.
- [x] Schema validator should reject unknown top-level keys to prevent silent contract drift.
- [x] Existing writer/builder roundtrip behavior should remain unchanged for valid payloads.

## Phase 0 — Preconditions
- [x] Confirmed schema validator enforced required keys/types but allowed unknown top-level keys.
- [x] Confirmed no dedicated unknown-key negative test existed for Stage 1 observability export.
- [x] Confirmed export write/read roundtrip and CLI export path were already covered.

## Phase 1 — Contracts and Interfaces
- [x] Added explicit allowed top-level key set for Stage 1 observability export schema.
- [x] Added deterministic unknown-key token format: `unknown_key:<key>`.
- [x] Preserved existing schema/kind/captured_at/session_dir/revise_metrics/status_at_a_glance validation semantics.

## Phase 2 — Core Implementation
- [x] Updated `stage1_observability_export_schema_errors` to reject unknown top-level keys.
- [x] Kept builder and writer behavior unchanged for valid payloads.
- [x] Maintained existing schema version and kind constants.

## Phase 3 — Safety and Failure Handling
- [x] Added unit test for unknown-key rejection in observability export schema validator.
- [x] Confirmed invalid payload path returns explicit schema errors (including unknown key token).
- [x] Confirmed valid export build/write paths remain green.

## Phase 4 — Verification and Observability
- [x] Expanded tests in `test_project_stage1_observability_export.py`.
- [x] Re-ran public export surface tests in `test_public_export_surface.py`.
- [x] Re-ran CLI suite in `test_cli.py`.
- [x] Executed focused verification:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_project_stage1_observability_export.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_public_export_surface.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_cli.py`
  - [x] Result: `226 passed`.

## Definition of Done
- [x] Stage 1 observability export schema fails closed on unknown top-level keys.
- [x] Export builder/writer remain stable for valid payloads.
- [x] Unit and integration suites pass with hardened observability schema validation.
- [x] Feature checklist is complete for repo-local scope.

## Test Cases
### Unit
- [x] `test_stage1_observability_export_schema_errors_empty_for_built_export`.
- [x] `test_stage1_observability_export_schema_errors_detect_invalid`.
- [x] `test_stage1_observability_export_schema_errors_reject_unknown_key`.

### Integration
- [x] `test_write_project_stage1_observability_export_roundtrip`.
- [x] `test_cli_export_stage1_observability_main_writes_file`.

### Negative
- [x] Unknown key payloads fail with `unknown_key:<key>`.
- [x] Existing required-field/type validation negatives remain green.

### Regression
- [x] Schema version and export kind constants remain unchanged.
- [x] Export roundtrip contract remains valid under stricter schema checking.

## Out of Scope
- [x] External telemetry backends or distributed observability data planes.
- [x] Cross-repository observability governance beyond local contract enforcement.
