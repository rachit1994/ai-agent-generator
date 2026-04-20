# Dual control

## Context
- [x] Verified feature priority and baseline percentage (`57%`) in `docs/master-architecture-feature-completion.md`.
- [x] Verified HS08 implementation in `src/guardrails_and_safety/risk_budgets_permission_matrix/risk_budgets/hard_stops_guarded.py`.
- [x] Verified harness-side dual-ack generation path in `src/workflow_pipelines/production_pipeline_plan_artifact/production_pipeline_task_to_promote/runner/completion_layer.py`.

## Assumptions and Constraints
- [x] Scope is repo-local dual-control gate behavior (HS08 + dual ack contract), not enterprise workflow UI.
- [x] HS08 must fail closed on malformed `dual_control` requirement metadata.
- [x] HS08 must fail closed when ack evidence is malformed or missing required contract fields.

## Phase 0 — Preconditions
- [x] Confirmed HS08 executes only in guarded/phased paths with `program/project_plan.json`.
- [x] Confirmed baseline tests existed for required/missing ack and same/distinct actor IDs.
- [x] Confirmed run-directory validation returns recomputed hard-stops and now enforces failed hard-stop errors.

## Phase 1 — Contracts and Interfaces
- [x] Hardened `_doc_review_dual_control_required` to fail closed when `dual_control` exists but is malformed.
- [x] Hardened `_dual_control_ack_valid` to require non-empty `acknowledged_at`.
- [x] Preserved existing core identity contract: distinct non-empty implementor/reviewer actor IDs.

## Phase 2 — Core Implementation
- [x] Updated `hard_stops_guarded.py` dual-control requirement parsing with strict bool semantics.
- [x] Updated `hard_stops_guarded.py` ack validator to include acknowledgment timestamp requirement.
- [x] Updated `run_directory.py` to append `hard_stop_failed:<id>` errors for any failing recomputed hard-stop IDs.
- [x] Updated `run_directory.py` strict `ok` decision to require zero failed hard-stop IDs.

## Phase 3 — Safety and Failure Handling
- [x] Added negative tests for malformed `doc_review` dual-control block.
- [x] Added negative tests for invalid ack schema version.
- [x] Added negative tests for non-string actor IDs.
- [x] Added negative tests for missing `acknowledged_at`.
- [x] Added negative test for `doc_review.passed == False`.

## Phase 4 — Verification and Observability
- [x] Added positive test for optional ack present and valid when dual-control is not required.
- [x] Re-ran focused dual-control and run-directory suite:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_dual_control_hs08.py`
  - [x] `uv run pytest src/guardrails_and_safety/review_gating_evaluator_authority/review_gating/tests/test_review_gating_positive.py`
  - [x] `uv run pytest src/guardrails_and_safety/review_gating_evaluator_authority/review_gating/tests/test_review_gating_negative.py`
  - [x] Result: `27 passed`.

## Definition of Done
- [x] HS08 fails closed for malformed `dual_control` requirements.
- [x] HS08 fails closed for malformed ack contracts (schema/type/timestamp).
- [x] HS08 passes only when dual-control evidence is structurally valid for required and optional-ack branches.
- [x] Recomputed hard-stop failures now block strict run-directory validation.
- [x] Focused test suite is green.

## Test Cases
### Unit
- [x] `test_hs08_fails_when_doc_review_not_passed`.
- [x] `test_hs08_fails_when_dual_control_block_is_malformed`.
- [x] `test_hs08_fails_when_ack_schema_invalid`.
- [x] `test_hs08_fails_when_ack_actor_not_string`.
- [x] `test_hs08_fails_when_acknowledged_at_missing`.

### Integration
- [x] `test_hs08_passes_when_dual_not_required_and_optional_ack_valid`.
- [x] `test_hs08_passes_dual_required_with_distinct_ack`.
- [x] Review-gating run-directory tests continue to pass after hard-stop failure propagation changes.

### Negative
- [x] `test_hs08_fails_when_dual_required_but_ack_missing`.
- [x] `test_hs08_fails_when_ack_present_but_same_actor_ids`.
- [x] `test_hs08_fails_when_dual_control_block_is_malformed`.

### Regression
- [x] Existing HS08 baseline tests still pass under stricter ack contract.
- [x] Review-gating positive/negative suites still pass with strict hard-stop propagation (`27 passed` aggregate run).

## Out of Scope
- [x] Enterprise maker-checker queue UI and multi-tenant approval workflow productization.
- [x] Cryptographic identity attestation beyond current repo-local actor-id contract checks.
