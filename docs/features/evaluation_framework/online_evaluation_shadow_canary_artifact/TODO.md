# Online evaluation (shadow/canary artifact)

## Context
- [x] Verified feature scope and baseline (`32%`) in `docs/master-architecture-feature-completion.md`.
- [x] Verified canonical canary contract in `online_eval_shadow_contract.py`.
- [x] Verified runtime producer (`evolution_layer.py`) and HS28 consumer (`hard_stops_evolution.py`) paths.

## Assumptions and Constraints
- [x] Scope is repo-local shadow/canary artifact contract robustness and HS28 contract consistency.
- [x] HS28 must use the same validation criteria as the online evaluation shadow contract.
- [x] Contract checks must fail closed for malformed schema version and weak metric payloads.

## Phase 0 — Preconditions
- [x] Confirmed contract tests existed but missed key branches (schema version value, promote missing, recorded_at missing, metric semantics).
- [x] Confirmed HS28 previously used ad-hoc checks weaker than canonical contract.
- [x] Confirmed evolution layer already emits a contract-shaped canary payload that can satisfy stricter rules.

## Phase 1 — Contracts and Interfaces
- [x] Added explicit contract schema version constant (`ONLINE_EVAL_SHADOW_SCHEMA_VERSION`).
- [x] Enforced schema version value check (`1.0`).
- [x] Enforced required shadow metric key `latency_p95_ms`.
- [x] Enforced shadow metric type/range checks (numeric, non-bool, non-negative).

## Phase 2 — Core Implementation
- [x] Hardened `validate_canary_report_dict` to reject unsupported schema versions and weak metrics.
- [x] Updated HS28 to validate canary payload via `validate_canary_report_dict` (single source of truth).
- [x] Preserved alias support (snake_case/camelCase) through contract-driven HS28 validation.

## Phase 3 — Safety and Failure Handling
- [x] Added negative tests for schema version mismatch.
- [x] Added negative tests for missing promote flag and missing recorded timestamp.
- [x] Added negative tests for missing/invalid/negative latency metric.
- [x] Added HS28 fail-closed test for canary payload missing required contract fields.

## Phase 4 — Verification and Observability
- [x] Expanded canary contract tests in `test_online_eval_shadow_contract.py`.
- [x] Expanded evolution hard-stop tests in `test_evolution_organization_hard_stops.py`.
- [x] Ran focused verification:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_online_eval_shadow_contract.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_evolution_organization_hard_stops.py`
  - [x] Result: `24 passed`.

## Definition of Done
- [x] Online eval canary contract enforces schema version and metric semantics beyond shape-only checks.
- [x] HS28 evaluation is contract-consistent with canary validator and fails closed on malformed artifacts.
- [x] Contract and HS28 tests cover critical positive/negative/camelCase-compat paths.
- [x] Feature checklist is complete for repo-local scope.

## Test Cases
### Unit
- [x] `test_validate_canary_report_dict_hs28_ok`.
- [x] `test_validate_canary_report_dict_requires_schema_version_value`.
- [x] `test_validate_canary_report_dict_promote_missing`.
- [x] `test_validate_canary_report_dict_recorded_at_missing`.
- [x] `test_validate_canary_report_dict_requires_latency_metric`.
- [x] `test_validate_canary_report_dict_rejects_latency_type_and_range`.
- [x] `test_validate_canary_report_dict_accepts_camel_case_aliases`.

### Integration
- [x] `test_write_evolution_artifacts_writes_valid_canary_report`.
- [x] `test_hs28_passes_with_camel_case_canary_payload`.

### Negative
- [x] `test_validate_canary_report_path_bad_json`.
- [x] `test_validate_canary_report_path_non_object_json`.
- [x] `test_hs28_fails_when_canary_missing_contract_fields`.

### Regression
- [x] Existing HS25/HS26/HS27/HS29/HS31/HS32 tests remain green after HS28 change.
- [x] Existing contract ID and missing-path tests remain green.

## Out of Scope
- [x] Live shadow traffic routing and production canary control-plane orchestration.
- [x] Organization-level rollout governance beyond local artifact contract enforcement.
