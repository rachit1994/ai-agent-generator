# Regression testing surface

## Context
- [x] Verified feature scope and baseline (`57%`) in `docs/master-architecture-feature-completion.md`.
- [x] Verified current implementation centers on `regression_surface_contract.py` and associated unit tests.
- [x] Confirmed feature remains scaffolded at `evaluation_framework/regression_testing_surface/surface.py` with contract-backed local enforcement.

## Assumptions and Constraints
- [x] Scope is repo-local regression anchor contract correctness and deterministic validation behavior.
- [x] Validation must fail closed for malformed anchor taxonomy and duplicate anchors.
- [x] Existing anchor-to-disk checks must remain stable and deterministic.

## Phase 0 — Preconditions
- [x] Confirmed existing tests covered mostly happy path (contract id, non-empty anchors, clean repo-tree pass).
- [x] Confirmed missing negative-path coverage for missing anchors, unknown dimensions, and duplicate anchors.
- [x] Confirmed missing explicit dimension coverage assertion.

## Phase 1 — Contracts and Interfaces
- [x] Added explicit dimension taxonomy constant (`REGRESSION_DIMENSIONS`) in contract module.
- [x] Added fail-closed validation for unknown dimension labels.
- [x] Added fail-closed validation for duplicate anchor paths.
- [x] Added fail-closed validation for uncovered required dimensions.

## Phase 2 — Core Implementation
- [x] Hardened `validate_regression_anchors` with deterministic, append-order error reporting.
- [x] Preserved existing missing-file error token format and anchor-order behavior.
- [x] Preserved current anchor set while improving contract strictness.

## Phase 3 — Safety and Failure Handling
- [x] Added tests for full missing-anchor token list and deterministic order.
- [x] Added tests for unknown-dimension rejection.
- [x] Added tests for duplicate-anchor rejection and uncovered-dimension signaling.
- [x] Added test asserting expected dimension coverage in declared anchors.

## Phase 4 — Verification and Observability
- [x] Ran targeted regression-surface test suite:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_regression_surface_contract.py`
  - [x] Result: passed.
- [x] Ran public export compatibility suite to ensure no regression:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_public_export_surface.py`
  - [x] Result: passed.
- [x] Combined run result: `212 passed`.

## Definition of Done
- [x] Regression anchor contract now fails closed for unknown dimensions, duplicates, and uncovered dimension taxonomy.
- [x] Regression contract test coverage includes both positive and negative branches.
- [x] Public export surface tests remain green after contract hardening.
- [x] Feature checklist is fully completed for repo-local scope.

## Test Cases
### Unit
- [x] `test_regression_surface_contract_id`.
- [x] `test_regression_dimension_anchors_non_empty`.
- [x] `test_regression_dimension_anchors_cover_expected_dimensions`.
- [x] `test_validate_regression_anchors_reports_all_missing_tokens_in_order`.
- [x] `test_validate_regression_anchors_rejects_unknown_dimension`.
- [x] `test_validate_regression_anchors_rejects_duplicate_anchor`.

### Integration
- [x] `test_validate_regression_anchors_clean_on_repo_tree`.
- [x] `test_public_export_surface.py` full suite passes to confirm no export regressions.

### Negative
- [x] Unknown dimension labels are rejected with deterministic error token.
- [x] Duplicate anchor paths are rejected with deterministic error token.
- [x] Missing anchors yield deterministic ordered missing-file error list.

### Regression
- [x] Existing clean repo-tree validation still returns no errors.
- [x] Existing exported benchmark modules remain stable under `test_public_export_surface.py`.

## Out of Scope
- [x] Full runtime regression coordination matrix/service orchestration.
- [x] Organization-wide control-plane expansion beyond local contract/test surface.
