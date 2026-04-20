# Production Readiness Program

## Context
- [x] Confirmed scope and baseline (`14%`) from `docs/master-architecture-feature-completion.md`.
- [x] Audited Stage 1 plan-lock readiness and manifest writers in `orchestrator/api/project_plan_lock.py`.
- [x] Identified fail-open gap: boolean gate flags accepted non-bool values and relied on implicit truthiness.

## Assumptions and Constraints
- [x] Readiness controls must fail closed for malformed policy flags.
- [x] Existing bool-based caller behavior remains unchanged.
- [x] Error payloads should be explicit and machine-parseable.

## Phase 0 — Preconditions
- [x] Verified no strict type guards existed for `require_revise_state` and `allow_local_stub_attestation`.
- [x] Verified coercion risk (`"false"`/`1`/`0`) could silently alter policy behavior.
- [x] Verified no unit tests covered non-bool flag handling.

## Phase 1 — Contracts and Interfaces
- [x] Added strict ingress checks to:
  - [x] `write_intake_lineage_manifest`
  - [x] `evaluate_project_plan_lock_readiness`
  - [x] `write_project_plan_lock`
- [x] Added explicit errors:
  - [x] `require_revise_state_not_bool`
  - [x] `allow_local_stub_attestation_not_bool`

## Phase 2 — Core Implementation
- [x] Implemented fail-closed returns for invalid flag types before file access/evaluation.
- [x] Ensured `ok=False` contract on malformed controls.
- [x] Added shared constant for lineage manifest filename to reduce literal drift.

## Phase 3 — Safety and Failure Handling
- [x] Added unit tests for non-bool flag rejection in all touched entry points.
- [x] Confirmed readiness/lock flow remains green for valid bool inputs.
- [x] Confirmed preflight/project validate integration remains green.

## Phase 4 — Verification and Observability
- [x] Added tests:
  - [x] `test_write_intake_lineage_manifest_rejects_non_bool_flag`
  - [x] `test_evaluate_project_plan_lock_readiness_rejects_non_bool_flags`
  - [x] `test_write_project_plan_lock_rejects_non_bool_flags`
- [x] Ran focused suites:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_project_plan_lock.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_project_validate.py`
  - [x] Result: `29 passed`.

## Definition of Done
- [x] Plan-lock/readiness controls now fail closed on malformed policy flag types.
- [x] New unit tests enforce non-bool rejection behavior.
- [x] Related validate flow remains green.

## Test Cases
### Unit
- [x] Reject non-bool `require_revise_state` in lineage writer.
- [x] Reject non-bool readiness flags in readiness evaluator.
- [x] Reject non-bool flags in lock writer.

### Integration
- [x] Existing lock readiness happy-path tests remain green.
- [x] Project validate tests remain green with strict readiness controls.

### Negative
- [x] String/int pseudo-bool inputs now fail explicitly.
- [x] Policy flags no longer rely on implicit truthiness.

### Regression
- [x] Existing attestation and lineage-drift tests remain green.
- [x] Existing readiness lock write/read behavior remains green for valid bools.

## Out of Scope
- [x] CLI-level schema redesign for boolean flags.
- [x] Cross-session policy orchestration beyond current local plan-lock surfaces.
