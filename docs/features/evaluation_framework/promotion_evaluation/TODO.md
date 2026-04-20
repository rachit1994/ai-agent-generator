# Promotion evaluation

## Context
- [x] Verified feature scope and baseline (`44%`) in `docs/master-architecture-feature-completion.md`.
- [x] Verified promotion package contract implementation in `promotion_eval_contract.py` and lifecycle integration in `evolution_layer.py`.
- [x] Verified HS26 enforcement path in `hard_stops_evolution.py`.

## Assumptions and Constraints
- [x] Scope is repo-local promotion package contract strictness and hard-stop consistency.
- [x] Validation must fail closed for malformed payloads and weak evidence linking.
- [x] Camel/snake contract aliases must remain supported consistently between validators and hard-stops.

## Phase 0 — Preconditions
- [x] Confirmed existing contract tests covered happy path and a small subset of negative paths.
- [x] Confirmed missing checks for schema version value, unknown keys, duplicate list values, and aggregate/evidence linkage.
- [x] Confirmed HS26 previously accepted only snake_case field and could crash on non-object JSON.

## Phase 1 — Contracts and Interfaces
- [x] Added explicit schema version constant and strict schema value validation (`1.0`).
- [x] Added unknown-key contract rejection for promotion package payloads.
- [x] Added duplicate detection for evaluator signal IDs and evidence window.
- [x] Added cross-field integrity requirement: `aggregate_id` must appear in `evidence_window`.

## Phase 2 — Core Implementation
- [x] Hardened `validate_promotion_package_dict` with additional fail-closed checks while preserving existing valid payload behavior.
- [x] Updated HS26 to enforce full promotion-package contract via `validate_promotion_package_dict` instead of ad-hoc list check.
- [x] Ensured HS26 now handles camelCase valid payloads and non-object payloads without crashes.

## Phase 3 — Safety and Failure Handling
- [x] Added negative tests for schema-version mismatch.
- [x] Added negative tests for unknown keys.
- [x] Added negative tests for missing aggregate evidence linkage.
- [x] Added negative tests for duplicate evaluator/evidence lists.
- [x] Added HS26 fail-closed test for non-object promotion package JSON.

## Phase 4 — Verification and Observability
- [x] Added/updated unit tests in:
  - [x] `test_promotion_eval_package_contract.py`
  - [x] `test_evolution_organization_hard_stops.py`
- [x] Ran focused verification:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_promotion_eval_package_contract.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_evolution_organization_hard_stops.py`
  - [x] Result: `19 passed`.

## Definition of Done
- [x] Promotion package contract enforces stronger structural and cross-field integrity checks.
- [x] HS26 uses the same contract logic as package validation and fails closed on malformed payloads.
- [x] Promotion evaluation test coverage now includes key missing negative and compatibility paths.
- [x] Feature checklist is complete for repo-local implementation scope.

## Test Cases
### Unit
- [x] `test_validate_promotion_package_dict_minimal_ok`.
- [x] `test_validate_promotion_package_dict_schema_version_value`.
- [x] `test_validate_promotion_package_dict_unknown_key`.
- [x] `test_validate_promotion_package_dict_requires_aggregate_in_evidence_window`.
- [x] `test_validate_promotion_package_dict_rejects_duplicate_lists`.
- [x] `test_validate_promotion_package_path_non_object_json`.

### Integration
- [x] `test_write_evolution_artifacts_writes_valid_promotion_package`.
- [x] `test_hs26_passes_with_camel_case_promotion_package`.

### Negative
- [x] `test_validate_promotion_package_dict_empty_signals`.
- [x] `test_validate_promotion_package_path_bad_json`.
- [x] `test_hs26_fails_closed_when_promotion_package_not_object`.

### Regression
- [x] Existing promotion contract constant and missing-path tests remain green.
- [x] Existing evolution/organization hard-stop tests remain green after HS26 hardening.

## Out of Scope
- [x] Production governance committee runtime and cross-repository promotion orchestration.
- [x] Multi-tenant control-plane promotion services beyond local artifact contract enforcement.
