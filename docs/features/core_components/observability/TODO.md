# Observability

## Context
- [x] Confirmed scope and baseline (`48%`) from `docs/master-architecture-feature-completion.md`.
- [x] Audited Stage 1 observability export surface in `project_stage1_observability_export.py`.
- [x] Identified fail-open gap: numeric knobs (`max_concurrent_agents`, status byte caps) could accept bool/non-positive values and be silently coerced downstream.

## Assumptions and Constraints
- [x] Observability export contract should reject malformed numeric controls at ingress.
- [x] Existing behavior for valid positive integer controls should remain unchanged.
- [x] Error mode should be explicit (raise `ValueError`) rather than silent coercion.

## Phase 0 — Preconditions
- [x] Verified no local guardrails on numeric knobs in export builder.
- [x] Verified values are forwarded into status path where coercion can hide invalid caller inputs.
- [x] Verified tests lacked coverage for invalid numeric control rejection.

## Phase 1 — Contracts and Interfaces
- [x] Added strict numeric validators:
  - [x] `_require_positive_int`
  - [x] `_require_optional_positive_int`
- [x] Enforced contract for:
  - [x] `max_concurrent_agents`
  - [x] `max_status_json_bytes`
  - [x] `max_status_jsonl_full_scan_bytes`
  - [x] `max_status_jsonl_tail_bytes`
  - [x] `max_status_listed_step_ids`

## Phase 2 — Core Implementation
- [x] Added ingress validation in `build_project_stage1_observability_export`.
- [x] Reject bool/non-int/non-positive values with deterministic `ValueError` messages.
- [x] Preserved export body schema and write path behavior for valid inputs.

## Phase 3 — Safety and Failure Handling
- [x] Added negative tests for invalid numeric knobs.
- [x] Confirmed export now fails closed before status traversal when controls are malformed.
- [x] Confirmed public export surface remains stable.

## Phase 4 — Verification and Observability
- [x] Added test: `test_build_stage1_observability_export_rejects_invalid_numeric_knobs`.
- [x] Ran focused suites:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_project_stage1_observability_export.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_public_export_surface.py`
  - [x] Result: `212 passed`.

## Definition of Done
- [x] Observability export knobs are strictly validated and fail closed.
- [x] New negative tests lock in non-coercive behavior.
- [x] Export surface and module public contracts remain green.

## Test Cases
### Unit
- [x] Valid Stage 1 observability export still builds with correct schema.
- [x] Bool `max_concurrent_agents` is rejected.
- [x] Non-positive size/list caps are rejected.

### Integration
- [x] Export write roundtrip remains valid for correct inputs.
- [x] CLI/export surface compatibility remains green.

### Negative
- [x] Invalid numeric knobs raise deterministic `ValueError`.
- [x] No silent coercion of malformed observability control values.

### Regression
- [x] Existing observability export schema tests remain green.
- [x] Public export surface tests remain green.

## Out of Scope
- [x] Redesign of export schema payload fields.
- [x] External telemetry backend integrations beyond local JSON export.
