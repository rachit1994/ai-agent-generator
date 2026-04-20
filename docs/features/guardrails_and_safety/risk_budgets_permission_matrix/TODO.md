# Risk budgets + permission matrix

## Context
- [x] Verified this is the second-highest feature in `Guardrails and safety` and currently tracked at `63%` in `docs/master-architecture-feature-completion.md`.
- [x] Verified implementation core in `src/guardrails_and_safety/risk_budgets_permission_matrix/risk_budgets/hard_stops.py`.
- [x] Verified schedule parity module in `src/guardrails_and_safety/risk_budgets_permission_matrix/risk_budgets/hard_stop_schedule.py`.
- [x] Verified organization-layer hard-stop logic in `src/guardrails_and_safety/risk_budgets_permission_matrix/risk_budgets/hard_stops_organization.py`.

## Assumptions and Constraints
- [x] Scope is repo-local hard-stop and permission-matrix enforcement, not external IAM services.
- [x] Validation must remain fail-closed for malformed JSON/JSONL or invalid budget fields.
- [x] `HS01–HS32` schedule parity must remain consistent between evaluator and expected schedule IDs.
- [x] Organization checks (`HS29–HS32`) require concrete on-disk lease and IAM evidence.

## Phase 0 — Preconditions
- [x] Confirmed `evaluate_hard_stops` emits the `HS01–HS32` band based on mode and artifact presence.
- [x] Confirmed schedule parity tests exist in `src/production_architecture/local_runtime/orchestrator/tests/unit/test_hard_stop_schedule.py`.
- [x] Confirmed HS29/HS30 coverage existed and identified missing HS31/HS32 and branch cases.

## Phase 1 — Contracts and Interfaces
- [x] Upgraded `HS01` semantics in `hard_stops.py` to use `validate_review_payload` instead of key-presence-only checks.
- [x] Kept required key subset check in `HS01` to preserve explicit contract surface.
- [x] Aligned schedule profile source by switching `hard_stop_schedule.py` to shared `run_profile.is_coding_only`.
- [x] Enforced permission-matrix contract presence/shape via `_permission_matrix_valid` in `hard_stops_organization.py`.

## Phase 2 — Core Implementation
- [x] Hardened `HS03` truncation provenance matching in `hard_stops.py` to fail on missing/non-string provenance IDs.
- [x] Added safe integer parsing helper `_safe_int` in `hard_stops.py`.
- [x] Hardened `HS06` in `hard_stops.py` to fail closed on non-numeric token budget values.
- [x] Updated `HS29` in `hard_stops_organization.py` to fail when `action_audit.jsonl` is missing.
- [x] Updated `HS29` in `hard_stops_organization.py` to fail when `lease_id` is missing/blank in audit lines.
- [x] Updated `HS30` in `hard_stops_organization.py` to fail when `action_audit.jsonl` is missing.

## Phase 3 — Safety and Failure Handling
- [x] Added `HS30` branch tests for missing high-risk approval token.
- [x] Added `HS30` branch tests for invalid expiry format.
- [x] Added `HS30` branch tests for low-risk rows without approval token.
- [x] Added `HS29` branch test for audit rows missing `lease_id`.
- [x] Added `HS31` branch tests for multi-shard handoff requirement (fail without envelope, pass with envelope).
- [x] Added `HS32` branch tests for autonomy self-approval requirement (`requires_promotion_package` + `proposal_ref`).

## Phase 4 — Verification and Observability
- [x] Added new focused core hard-stop regression file: `test_risk_budget_hard_stops_core.py`.
- [x] Added `HS01` negative semantic payload test (`invalid status`) in core hard-stop tests.
- [x] Added `HS03` provenance integrity negative test in core hard-stop tests.
- [x] Added `HS06` non-numeric fail-closed test in core hard-stop tests.
- [x] Ran focused suite:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_autonomy_boundaries_expiry.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_evolution_organization_hard_stops.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_hard_stop_schedule.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_risk_budget_hard_stops_core.py`
  - [x] Result: `23 passed`.

## Definition of Done
- [x] `HS01` validates semantic review payload correctness, not only key presence.
- [x] `HS03` rejects malformed truncation/reduction provenance inputs.
- [x] `HS06` rejects malformed numeric budget values without exceptions.
- [x] `HS29/HS30` are fail-closed for missing IAM audit evidence.
- [x] `HS31/HS32` critical branches are explicitly covered by tests.
- [x] Schedule parity still passes after switching to shared run-profile logic.

## Test Cases
### Unit
- [x] `test_hs01_fails_for_semantically_invalid_review_payload`.
- [x] `test_hs03_fails_when_truncation_row_missing_provenance_id`.
- [x] `test_hs06_fails_closed_for_non_numeric_budget_values`.
- [x] `test_hs30_fails_when_high_risk_missing_approval_token_id`.
- [x] `test_hs30_fails_when_high_risk_expiry_invalid_format`.

### Integration
- [x] `test_hs31_requires_handoff_envelope_when_multi_shard`.
- [x] `test_hs32_requires_promotion_package_and_proposal_ref`.
- [x] `test_schedule_full_stack_matches_evaluate`.
- [x] `test_schedule_guarded_with_plan_and_replay`.

### Negative
- [x] `test_hs29_fails_when_audit_lease_unknown`.
- [x] `test_hs29_fails_when_audit_line_missing_lease_id`.
- [x] `test_hs30_fails_when_high_risk_approval_expired`.
- [x] `test_hs06_fails_on_expired_context`.

### Regression
- [x] `test_schedule_empty_baseline_matches_evaluate`.
- [x] `test_schedule_coding_only_skips_extension_bands`.
- [x] `test_schedule_baseline_replay_adds_hs17_hs20`.
- [x] Focused risk-budget suite remains green (`23 passed`).

## Out of Scope
- [x] Building a distributed IAM service or external policy engine.
- [x] Multi-tenant control-plane rollout beyond local repo hard-stop enforcement.
