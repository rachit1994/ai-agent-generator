# Failure path artifacts

## Context
- [x] Verified feature scope and baseline (`52%`) in `docs/master-architecture-feature-completion.md`.
- [x] Verified canonical failure/replay contracts in `failure_pipeline_contract.py`.
- [x] Verified failure summary producer path in `runner/failure_summary.py`.

## Assumptions and Constraints
- [x] Scope is repo-local failure-summary and replay-manifest contract quality.
- [x] Contract validation must fail closed for malformed hash anchors and blank failure message payloads.
- [x] Existing failure artifact producers should remain compatible with stricter checks.

## Phase 0 — Preconditions
- [x] Confirmed existing tests cover core happy path and several negative branches.
- [x] Confirmed replay hash fields were only non-empty string checked, not hash format checked.
- [x] Confirmed failure summary error message accepted blank strings.

## Phase 1 — Contracts and Interfaces
- [x] Added SHA-256 format validator helper for replay hash fields.
- [x] Enforced SHA-256 format for `sources[].sha256`.
- [x] Enforced SHA-256 format for `chain_root`.
- [x] Enforced non-empty failure summary error message strings.

## Phase 2 — Core Implementation
- [x] Hardened `validate_replay_manifest_dict` with strict hash semantics.
- [x] Hardened `validate_failure_summary_dict` for blank message fail-closed behavior.
- [x] Preserved existing contract IDs and path-level validation interfaces.

## Phase 3 — Safety and Failure Handling
- [x] Added negative test for non-SHA replay source and chain root values.
- [x] Added negative test for blank failure summary error message.
- [x] Confirmed existing path-level missing/bad-json failures remain covered.

## Phase 4 — Verification and Observability
- [x] Expanded contract tests in `test_failure_pipeline_contract.py`.
- [x] Re-ran event-lineage replay-manifest integration suite in `test_event_lineage_replay_manifest.py`.
- [x] Executed focused verification:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_failure_pipeline_contract.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_event_lineage_replay_manifest.py`
  - [x] Result: `17 passed`.

## Definition of Done
- [x] Failure-path contracts now reject weak hash anchors and blank failure messages.
- [x] Replay manifest and failure summary validation remain stable for existing valid payloads.
- [x] Unit/integration tests cover added fail-closed branches and existing regression expectations.
- [x] Feature checklist is complete for repo-local scope.

## Test Cases
### Unit
- [x] `test_validate_replay_manifest_minimal_hs18_shape_ok`.
- [x] `test_validate_replay_manifest_rejects_non_sha_hashes`.
- [x] `test_validate_replay_manifest_wrong_contract`.
- [x] `test_validate_failure_summary_ok`.
- [x] `test_validate_failure_summary_rejects_blank_message`.

### Integration
- [x] `test_validate_replay_manifest_path_ok`.
- [x] `test_event_lineage_replay_manifest.py` suite remains green with stricter replay hash checks.

### Negative
- [x] `test_validate_replay_manifest_path_missing`.
- [x] `test_validate_replay_manifest_bad_passed_type_when_present`.
- [x] `test_validate_failure_summary_not_failed`.
- [x] failure summary/replay path bad JSON and missing-file behaviors remain validated.

### Regression
- [x] Existing failure/replay contract IDs remain unchanged and verified.
- [x] Existing producer-compatible payloads remain valid under hardened checks.

## Out of Scope
- [x] Distributed incident-response control plane and global rollback orchestration.
- [x] Cross-repository production rollout governance beyond local artifact contract enforcement.
