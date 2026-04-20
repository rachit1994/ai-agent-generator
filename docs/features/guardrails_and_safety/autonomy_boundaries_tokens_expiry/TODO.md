# Autonomy boundaries (tokens, expiry)

## Context
- [x] Verified this feature priority and baseline percentage (`74%`) in `docs/master-architecture-feature-completion.md`.
- [x] Verified producer path in `src/guardrails_and_safety/autonomy_boundaries/autonomy_boundaries_tokens_expiry/token_context.py`.
- [x] Verified consumer enforcement in `src/guardrails_and_safety/risk_budgets_permission_matrix/risk_budgets/hard_stops.py` (`HS06`) and `hard_stops_organization.py` (`HS30`).

## Assumptions and Constraints
- [x] Scope is local autonomy boundary enforcement in file-based artifacts, not external IAM/session services.
- [x] Expiry and token checks must fail closed for malformed input.
- [x] High-risk actions require approval token and valid expiry evidence.

## Phase 0 — Preconditions
- [x] Confirmed `build_token_context` emits `autonomy_anchor_at`, `context_expires_at`, and `context_ttl_seconds`.
- [x] Confirmed HS06 evaluates stage budgets plus expiry window.
- [x] Confirmed HS30 evaluates high-risk approval-token expiry.

## Phase 1 — Contracts and Interfaces
- [x] Hardened `build_token_context` argument contracts: positive `max_tokens`, `model_context_limit`, and `context_ttl_seconds` required.
- [x] Hardened stage token parsing contract in `build_token_context` using safe integer parsing.
- [x] Aligned budget interface to use `effective_budget = min(max_tokens, model_context_limit)`.

## Phase 2 — Core Implementation
- [x] Added `_safe_int` helper in `token_context.py` to prevent crashes on malformed token fields.
- [x] Updated `build_token_context` to mark stage `budget_status = fail_closed` for invalid token fields.
- [x] Updated `build_token_context` to avoid direct `int(...)` conversion crashes.
- [x] Updated HS06 in `hard_stops.py` to fail when any stage entry is non-dict.

## Phase 3 — Safety and Failure Handling
- [x] Hardened HS30 in `hard_stops_organization.py` to reject missing/blank `approval_token_id`.
- [x] Hardened HS30 to reject missing/blank `approval_token_expires_at` for high-risk actions.
- [x] Kept HS30 invalid-date parse path fail-closed.

## Phase 4 — Verification and Observability
- [x] Added `build_token_context` robustness tests for invalid token values and effective-budget behavior.
- [x] Added test for invalid TTL rejection.
- [x] Added HS06 tests for invalid expiry format, non-dict stage rows, and explicit `fail_closed` stage status.
- [x] Added HS30 tests for missing expiry and whitespace token IDs.
- [x] Ran focused suite:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_autonomy_boundaries_expiry.py src/production_architecture/local_runtime/orchestrator/tests/unit/test_risk_budget_hard_stops_core.py`
  - [x] Result: `19 passed`.

## Definition of Done
- [x] Token-context generation is deterministic and fails closed for invalid token inputs.
- [x] HS06 rejects malformed/expired autonomy contexts and malformed stage structures.
- [x] HS30 enforces high-risk approval token + expiry presence and validity.
- [x] Focused autonomy-boundary tests pass with no failures.

## Test Cases
### Unit
- [x] `test_build_token_context_emits_expiry_fields`.
- [x] `test_build_token_context_uses_effective_budget_and_fail_closes_invalid_tokens`.
- [x] `test_build_token_context_rejects_invalid_ttl`.
- [x] `test_hs06_fails_closed_for_non_numeric_budget_values`.

### Integration
- [x] `test_hs06_fails_on_expired_context`.
- [x] `test_hs06_passes_when_expiry_absent`.
- [x] `test_hs06_fails_when_context_expiry_invalid_format`.
- [x] `test_hs30_passes_high_risk_with_future_approval_expiry`.

### Negative
- [x] `test_hs06_fails_when_stage_entry_not_object`.
- [x] `test_hs06_fails_when_budget_status_fail_closed`.
- [x] `test_hs30_fails_when_high_risk_missing_approval_token_id`.
- [x] `test_hs30_fails_when_high_risk_expiry_missing`.
- [x] `test_hs30_fails_when_high_risk_expiry_invalid_format`.
- [x] `test_hs30_fails_when_high_risk_token_whitespace`.

### Regression
- [x] `test_parse_iso_utc_accepts_zulu_and_rejects_garbage`.
- [x] `test_hs30_passes_low_risk_without_token`.
- [x] Focused suite remains green (`19 passed`) after autonomy-boundary hardening.

## Out of Scope
- [x] Organization-wide session orchestration services outside local run artifact validation.
- [x] External IAM/token-issuer integration beyond repo-local hard-stop enforcement.
