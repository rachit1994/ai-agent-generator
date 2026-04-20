# Run manifest

## Context
- [x] Verified feature scope and baseline (`56%`) in `docs/master-architecture-feature-completion.md`.
- [x] Verified canonical run-manifest contract in `run_manifest_contract.py`.
- [x] Verified producer and consumer integration in `runner/single_task.py` and replay/validate tests.

## Assumptions and Constraints
- [x] Scope is repo-local single-task run anchor contract quality and deterministic replay linkage.
- [x] Manifest should fail closed on unknown keys and partial project linkage metadata.
- [x] Existing producer behavior (baseline/guarded/phased + optional project metadata) must remain valid.

## Phase 0 — Preconditions
- [x] Confirmed existing tests covered happy path and several key negative checks.
- [x] Confirmed manifest accepted unknown keys without rejection.
- [x] Confirmed manifest allowed only one of project linkage fields to be present.

## Phase 1 — Contracts and Interfaces
- [x] Added explicit allowed-key enforcement for run-manifest payload.
- [x] Added project linkage consistency rule requiring both `project_step_id` and `project_session_dir` when either is present.
- [x] Preserved existing required top-level contract fields (`schema`, `run_id`, `mode`, `task`).

## Phase 2 — Core Implementation
- [x] Hardened `validate_run_manifest_dict` with unknown-key and project-linkage consistency checks.
- [x] Kept producer output in `single_task.py` compatible with stricter validation.
- [x] Preserved replay/validate-run compatibility for existing manifest payloads.

## Phase 3 — Safety and Failure Handling
- [x] Added negative test for partial project linkage metadata.
- [x] Added negative test for unknown keys.
- [x] Added path-level negative tests for missing file, invalid JSON, and non-object JSON payloads.

## Phase 4 — Verification and Observability
- [x] Expanded run manifest contract tests in `test_run_manifest_contract.py`.
- [x] Re-ran replay integration suite in `test_replay.py`.
- [x] Re-ran runner artifact integration in `test_runner_artifacts.py`.
- [x] Executed focused verification:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_run_manifest_contract.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_replay.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_runner_artifacts.py`
  - [x] Result: `19 passed`.

## Definition of Done
- [x] Run manifest contract now rejects unknown keys and inconsistent project linkage metadata.
- [x] Producer and replay/runner integrations remain stable under stricter validation.
- [x] Unit and integration tests cover new fail-closed branches and existing behavior.
- [x] Feature checklist is complete for repo-local scope.

## Test Cases
### Unit
- [x] `test_validate_run_manifest_ok`.
- [x] `test_validate_run_manifest_with_project_fields_ok`.
- [x] `test_validate_run_manifest_project_linkage_requires_both_fields`.
- [x] `test_validate_run_manifest_rejects_unknown_keys`.
- [x] `test_validate_run_manifest_bad_schema`.
- [x] `test_validate_run_manifest_bad_mode`.
- [x] `test_validate_run_manifest_blank_task`.

### Integration
- [x] `test_replay.py` suite remains green with stricter run-manifest validation.
- [x] `test_runner_artifacts.py` remains green with producer contract checks.

### Negative
- [x] `test_validate_run_manifest_path_missing_and_bad_json`.
- [x] `test_validate_run_manifest_path_non_object_json`.
- [x] existing blank project step id negative remains covered.

### Regression
- [x] Existing run-manifest contract ID and valid path tests remain green.
- [x] Producer emits contract-valid manifest for single-task and project-driven paths.

## Out of Scope
- [x] Multi-repo manifest orchestration and distributed run-index control plane.
- [x] Enterprise lifecycle governance services beyond local contract enforcement and replay linkage.
