# Rollback rules (policy bundle evidence)

## Context
- [x] Verified feature priority and baseline percentage (`56%`) in `docs/master-architecture-feature-completion.md`.
- [x] Verified validator implementation in `src/guardrails_and_safety/rollback_rules_policy_bundle/policy_bundle_rollback.py`.
- [x] Verified run-directory integration in `src/guardrails_and_safety/review_gating_evaluator_authority/review_gating/run_directory.py`.
- [x] Verified completion harness writes rollback evidence stub in `completion_layer.py`.

## Assumptions and Constraints
- [x] Scope is repo-local rollback evidence contract quality and fail-closed validation behavior.
- [x] Optional-file behavior is accepted, but when file exists it must validate strictly and never raise.
- [x] Rollback evidence errors must propagate to run-directory validation errors.

## Phase 0 — Preconditions
- [x] Confirmed baseline tests existed for absent file, `status=none`, invalid sha, and valid atomic payload.
- [x] Confirmed missing branch coverage for invalid JSON, schema/status errors, paths validation, and non-object JSON.
- [x] Confirmed run-directory integration path consumes `validate_policy_bundle_rollback`.

## Phase 1 — Contracts and Interfaces
- [x] Hardened rollback validator to reject non-object JSON payloads with stable error code (`policy_bundle_rollback_json_not_object`).
- [x] Hardened atomic rollback contract to require `previous_policy_sha256 != current_policy_sha256`.
- [x] Hardened atomic rollback contract to reject duplicate `paths_touched` entries.
- [x] Preserved existing schema/status contract and sha/path shape checks.

## Phase 2 — Core Implementation
- [x] Updated `_errors_for_atomic_rollback` to accumulate multiple errors instead of short-circuiting at first failure.
- [x] Added non-object payload type guard in `validate_policy_bundle_rollback`.
- [x] Kept run-directory error propagation unchanged while extending validator error surface.

## Phase 3 — Safety and Failure Handling
- [x] Added explicit negative unit tests for invalid JSON payload.
- [x] Added explicit negative unit tests for non-object JSON payload.
- [x] Added explicit negative unit tests for schema mismatch and invalid status.
- [x] Added explicit negative unit tests for empty/invalid/duplicate `paths_touched`.
- [x] Added explicit negative unit test for unchanged sha pair in atomic rollback.

## Phase 4 — Verification and Observability
- [x] Added integration tests for run-directory propagation of rollback validation errors.
- [x] Added integration test that valid atomic rollback does not emit rollback-specific errors.
- [x] Re-ran focused rollback + run-directory suite:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_policy_bundle_rollback.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_run_directory_policy_bundle_rollback_integration.py`
  - [x] `uv run pytest src/guardrails_and_safety/review_gating_evaluator_authority/review_gating/tests/test_review_gating_positive.py`
  - [x] `uv run pytest src/guardrails_and_safety/review_gating_evaluator_authority/review_gating/tests/test_review_gating_negative.py`
  - [x] Result: `30 passed`.

## Definition of Done
- [x] Rollback validator is fail-closed for malformed and non-object payloads.
- [x] Atomic rollback validation enforces sha-change + path-quality constraints.
- [x] Run-directory validation surfaces rollback contract errors end-to-end.
- [x] Focused rollback-related tests are green.

## Test Cases
### Unit
- [x] `test_validate_invalid_json`.
- [x] `test_validate_non_object_json`.
- [x] `test_validate_schema_version_error`.
- [x] `test_validate_invalid_status`.
- [x] `test_validate_atomic_requires_non_empty_paths`.
- [x] `test_validate_atomic_rejects_blank_paths_and_duplicate_paths`.
- [x] `test_validate_atomic_requires_sha_change`.
- [x] Existing `test_validate_none_status_ok` and `test_validate_atomic_ok` remain green.

### Integration
- [x] `test_run_directory_surfaces_policy_bundle_invalid_json`.
- [x] `test_run_directory_accepts_valid_atomic_policy_bundle`.

### Negative
- [x] Invalid JSON payload returns `policy_bundle_rollback_invalid_json`.
- [x] Non-object payload returns `policy_bundle_rollback_json_not_object`.
- [x] Invalid status returns `policy_bundle_rollback_status_invalid`.
- [x] Unchanged rollback hashes return `policy_bundle_rollback_sha256_must_change`.

### Regression
- [x] Existing review-gating positive suite remains green after rollback validator changes.
- [x] Existing review-gating negative suite remains green after rollback validator changes.
- [x] Focused aggregate run remains green (`30 passed`).

## Out of Scope
- [x] Distributed rollback control-plane implementation and multi-node orchestration.
- [x] Cryptographic signing/attestation service for policy bundles beyond current repo-local evidence schema.
