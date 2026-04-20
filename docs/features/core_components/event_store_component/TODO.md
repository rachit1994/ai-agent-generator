# Event Store Component

## Context
- [x] Confirmed scope and baseline (`35%`) from `docs/master-architecture-feature-completion.md`.
- [x] Audited local event-store persistence utilities in `production_architecture/storage/storage/storage.py`.
- [x] Identified fail-open serialization gap: JSON writers allowed non-finite floats (`NaN`, `Inf`), which can create non-portable/invalid artifacts for downstream event consumers.

## Assumptions and Constraints
- [x] Event-store artifacts should be strict JSON and deterministic across runtimes/parsers.
- [x] Non-finite values must fail fast rather than being serialized as `NaN`/`Infinity`.
- [x] Existing deterministic key-ordering behavior must remain unchanged.

## Phase 0 — Preconditions
- [x] Verified `_stable_json_dumps` did not disable `allow_nan`.
- [x] Verified both `write_json` and `append_jsonl` depend on `_stable_json_dumps`.
- [x] Verified no explicit tests covered non-finite float rejection.

## Phase 1 — Contracts and Interfaces
- [x] Tightened JSON serialization contract to disallow non-finite floats.
- [x] Preserved existing pretty/compact deterministic formatting and key ordering.
- [x] Failure mode is explicit `ValueError` from serializer.

## Phase 2 — Core Implementation
- [x] Updated `_stable_json_dumps` to use `allow_nan=False` for both pretty and compact modes.
- [x] Applied contract to both `write_json` and `append_jsonl` through shared helper.
- [x] Left read-path behavior unchanged.

## Phase 3 — Safety and Failure Handling
- [x] Added negative tests for non-finite number rejection in both JSON and JSONL writes.
- [x] Confirmed malformed numeric payloads now fail before persistence.
- [x] Confirmed stable roundtrip behavior still passes for valid payloads.

## Phase 4 — Verification and Observability
- [x] Added tests:
  - [x] `test_write_json_rejects_non_finite_numbers`
  - [x] `test_append_jsonl_rejects_non_finite_numbers`
- [x] Ran focused suites:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_storage_utils.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_public_export_surface.py`
  - [x] Result: `211 passed`.

## Definition of Done
- [x] Event-store serializers reject non-finite floats fail-closed.
- [x] Unit tests lock in strict JSON compatibility behavior.
- [x] Storage and public surface regressions are green.

## Test Cases
### Unit
- [x] Stable JSON write/read roundtrip remains valid.
- [x] Stable JSONL append/read roundtrip remains valid.
- [x] `NaN`/`Inf` serialization attempts are rejected.

### Integration
- [x] Storage utility suite remains green.
- [x] Public export surface remains green.

### Negative
- [x] Non-finite numeric artifacts are blocked before write.
- [x] Invalid JSONL line behavior on read remains fail-closed.

### Regression
- [x] Existing deterministic key-order assertions remain green.
- [x] Existing missing-file / invalid-line read behavior remains green.

## Out of Scope
- [x] Schema-level validation of event payload semantics beyond JSON compatibility.
- [x] External durable event-store infrastructure (databases/streams).
