# Event Store Semantics

## Context
- [x] Confirmed scope and baseline (`34%`) from `docs/master-architecture-feature-completion.md`.
- [x] Audited event-store hard-stop enforcement in `hard_stops_events.py` (HS17).
- [x] Identified event-semantics fail-closed gap: HS17 accepted duplicate `event_id` rows and weakly typed required fields.

## Assumptions and Constraints
- [x] Scope is repo-local append-only event semantics enforced through hard stops and tests.
- [x] HS17 should fail closed when persisted event envelopes are malformed, weakly typed, or duplicate by `event_id`.
- [x] HS18/HS19/HS20 behavior should remain unchanged.

## Phase 0 — Preconditions
- [x] Verified existing event-lineage tests covered trace tamper and command-id idempotency.
- [x] Verified no dedicated HS17 test for duplicate `event_id`.
- [x] Verified no dedicated HS17 tests for strict string typing on required envelope fields.

## Phase 1 — Contracts and Interfaces
- [x] Tightened HS17 envelope validation semantics:
  - [x] every non-empty event line must parse as JSON object
  - [x] `contract_version` must be supported
  - [x] `event_id`, `aggregate_id`, `occurred_at` must be non-empty strings
  - [x] `event_id` values must be unique within `run_events.jsonl`
- [x] Kept HS17 output and schedule wiring unchanged.

## Phase 2 — Core Implementation
- [x] Added `_parse_event_line` helper for stable line parsing.
- [x] Added `_validated_event_id` helper for typed envelope validation.
- [x] Updated `_hs17_event_contract` to enforce uniqueness and strict required-field typing.

## Phase 3 — Safety and Failure Handling
- [x] Added negative regression case for duplicate `event_id` replay envelopes.
- [x] Preserved earlier negative coverage for malformed later line and missing required later field.
- [x] Confirmed HS17 now fails deterministically for both duplicate-ID and malformed stream conditions.

## Phase 4 — Verification and Observability
- [x] Added test `test_hs17_fails_when_duplicate_event_id_seen` in `test_event_lineage_replay_manifest.py`.
- [x] Re-ran focused suites:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_event_lineage_replay_manifest.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_hard_stop_schedule.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_public_export_surface.py`
  - [x] Result: `218 passed`.

## Definition of Done
- [x] HS17 enforces strict required-field typing and duplicate `event_id` rejection.
- [x] Event-store semantics are fail-closed for malformed and duplicate envelope scenarios.
- [x] Focused replay/schedule/export suites are green and lint-clean.

## Test Cases
### Unit
- [x] `test_hs17_fails_when_later_event_line_is_malformed`.
- [x] `test_hs17_fails_when_later_event_line_missing_required_field`.
- [x] `test_hs17_fails_when_duplicate_event_id_seen`.

### Integration
- [x] `test_hard_stop_schedule.py` remains green with tightened HS17 semantics.

### Negative
- [x] Duplicate `event_id` in event stream fails HS17.
- [x] Malformed or non-object event line fails HS17.
- [x] Missing required typed fields fail HS17.

### Regression
- [x] HS18 trace tamper detection remains green.
- [x] HS20 duplicate committed mutation guard remains green.
- [x] Public export/import migration surface remains green.

## Out of Scope
- [x] Durable distributed event-store backends and cross-service ordering guarantees.
- [x] Production control-plane event compaction/snapshot orchestration.
