# Hard Release Gates

## Context
- [x] Confirmed scope and baseline (`24%`) from `docs/master-architecture-feature-completion.md`.
- [x] Audited hard release gate computation and readiness logic in `risk_budgets/balanced_gates.py`.
- [x] Identified fail-closed gap: malformed numeric inputs could raise or produce unsafe truthy coercions in gate scoring.

## Assumptions and Constraints
- [x] Scope is repo-local hard gate stability (`compute_balanced_gates` + `validation_ready`) under malformed inputs.
- [x] Gate computations must remain deterministic and conservative when metrics payloads are malformed.
- [x] Existing output schema and threshold profile contract must stay unchanged.

## Phase 0 — Preconditions
- [x] Verified no focused tests existed for malformed reliability inputs in balanced gate computation.
- [x] Verified no focused tests existed for missing/malformed readiness score fields.
- [x] Verified hard gate functions are part of exported guardrail surface and used by CTO gate flows.

## Phase 1 — Contracts and Interfaces
- [x] Added safe numeric coercion semantics for balanced gate scoring:
  - [x] bool values are rejected as numeric signal
  - [x] malformed/empty strings coerce to zero
  - [x] missing fields coerce to zero
- [x] Preserved balanced gate return structure and key names.

## Phase 2 — Core Implementation
- [x] Added `_to_float_or_zero` helper.
- [x] Added `_to_int_or_zero` helper.
- [x] Updated `compute_balanced_gates` to safely coerce reliability before scaling.
- [x] Updated `validation_ready` to safely coerce readiness dimensions before threshold checks.

## Phase 3 — Safety and Failure Handling
- [x] Added negative test for malformed reliability input (`"not-a-number"`).
- [x] Added negative tests for missing/malformed readiness scores (returns `False`).
- [x] Confirmed valid numeric-string readiness payloads still pass when thresholds are met.

## Phase 4 — Verification and Observability
- [x] Added `test_balanced_gates.py` with fail-closed coverage.
- [x] Ran focused suites:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_balanced_gates.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_public_export_surface.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_cto_gates.py`
  - [x] Result: `209 passed`.

## Definition of Done
- [x] Hard release gate scoring is fail-closed for malformed numeric metric inputs.
- [x] Readiness checks no longer rely on raw untrusted dict values.
- [x] Focused hard-gate and regression suites are green and lint-clean.

## Test Cases
### Unit
- [x] `test_compute_balanced_gates_fails_closed_for_malformed_reliability`.
- [x] `test_validation_ready_fails_closed_for_missing_or_malformed_scores`.

### Integration
- [x] `test_cto_gates.py` remains green after balanced gate hardening.
- [x] `test_public_export_surface.py` remains green with unchanged exported symbols.

### Negative
- [x] Malformed reliability no longer raises and safely maps to conservative scoring.
- [x] Missing/malformed readiness dimensions now fail closed.

### Regression
- [x] Well-formed score paths still satisfy strict thresholds as before.
- [x] Guardrails public export surface remains stable.

## Out of Scope
- [x] Enterprise release governance workflows and external release approval systems.
- [x] Production rollout orchestration and canary automation policies.
