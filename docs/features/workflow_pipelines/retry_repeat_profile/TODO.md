# Retry / repeat profile

## Context
- [x] Verified feature scope and baseline (`58%`) in `docs/master-architecture-feature-completion.md`.
- [x] Verified canonical repeat envelope contract in `retry_pipeline_contract.py`.
- [x] Verified repeat envelope generation and validation coupling in `runner/single_task.py`.

## Assumptions and Constraints
- [x] Scope is repo-local repeat envelope contract strictness and consistency guarantees.
- [x] Repeat envelope booleans must be consistent with per-run outcomes.
- [x] Legacy exports must remain compatible with existing public export tests.

## Phase 0 — Preconditions
- [x] Confirmed existing tests covered happy path and several structural negatives.
- [x] Confirmed contract lacked required envelope schema field enforcement.
- [x] Confirmed error payload shape and aggregate consistency checks were under-specified.

## Phase 1 — Contracts and Interfaces
- [x] Added required top-level `schema` contract field validation.
- [x] Tightened run-error envelope shape to require non-empty `error.type` and `error.message`.
- [x] Added cross-field consistency checks:
  - [x] `all_runs_no_pipeline_error` must match whether any run has `error`.
  - [x] `validation_ready_all` cannot be `True` when any run has `error`.

## Phase 2 — Core Implementation
- [x] Updated repeat envelope producer in `single_task.py` to emit `schema = RETRY_PIPELINE_REPEAT_CONTRACT`.
- [x] Hardened `validate_repeat_profile_result` to fail closed on schema and consistency violations.
- [x] Preserved existing retry execution behavior and repeat result structure.

## Phase 3 — Safety and Failure Handling
- [x] Added negative tests for non-object repeat result with `repeat >= 2`.
- [x] Added negative tests for missing schema.
- [x] Added negative tests for malformed error payload (`type`/`message`).
- [x] Added negative tests for inconsistent aggregate booleans vs per-run errors.

## Phase 4 — Verification and Observability
- [x] Expanded repeat contract tests in `test_retry_pipeline_repeat_contract.py`.
- [x] Verified repeat integration path in `test_cto_gates.py`.
- [x] Verified export compatibility remains green in `test_public_export_surface.py`.
- [x] Executed focused verification:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_retry_pipeline_repeat_contract.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_cto_gates.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_public_export_surface.py`
  - [x] Result: `219 passed`.

## Definition of Done
- [x] Retry/repeat envelope contract now enforces schema presence, error payload shape, and aggregate consistency semantics.
- [x] Repeat envelope producer emits contract identifier and remains validation-clean.
- [x] Unit and integration coverage includes key fail-closed and consistency branches.
- [x] Feature checklist is complete for repo-local scope.

## Test Cases
### Unit
- [x] `test_retry_pipeline_repeat_contract_id`.
- [x] `test_validate_repeat_profile_ok`.
- [x] `test_validate_repeat_profile_not_object_for_repeat_gte_2`.
- [x] `test_validate_repeat_profile_requires_schema`.
- [x] `test_validate_repeat_profile_error_shape_requires_type_and_message`.
- [x] `test_validate_repeat_profile_enforces_consistency_flags`.

### Integration
- [x] `test_execute_single_task_repeat_two_isolated_runs` in `test_cto_gates.py`.

### Negative
- [x] Existing outcome-shape negatives remain covered (`both_output_and_error`, `neither_output_nor_error`).
- [x] Existing repeat mismatch / runs length negatives remain covered.
- [x] Added schema and semantic consistency negatives for aggregate flags.

### Regression
- [x] `test_public_export_surface.py` remains green after contract/producer updates.
- [x] Existing repeat path behavior for `repeat < 2` and valid error-run envelope remains green.

## Out of Scope
- [x] Centralized escalation/retry orchestration service and control-plane policying.
- [x] Cross-repository rollout automation for repeat policy governance.
