# Replay Fail Closed

## Context
- [x] Confirmed scope and baseline (`50%`) from `docs/master-architecture-feature-completion.md`.
- [x] Audited replay/event-lineage hard-stop implementation in `hard_stops_events.py` (HS17–HS20).
- [x] Identified fail-closed gap: HS17 only validated the first event-store line.

## Assumptions and Constraints
- [x] Scope is repo-local replay safety via hard-stop enforcement and contracts.
- [x] HS17 should fail closed when any persisted event line is malformed or contract-incomplete.
- [x] Existing HS18/HS19/HS20 behavior should remain intact.

## Phase 0 — Preconditions
- [x] Verified event-lineage tests existed for HS18/HS20 and coding-only bypass.
- [x] Verified no HS17 regression coverage for malformed later lines.
- [x] Verified no HS17 regression coverage for missing required fields on later lines.

## Phase 1 — Contracts and Interfaces
- [x] Hardened HS17 validation semantics:
  - [x] require at least one non-empty event line
  - [x] parse and validate every non-empty line
  - [x] fail on malformed JSON or non-object lines
  - [x] require `contract_version`, `event_id`, `aggregate_id`, `occurred_at` for each line
- [x] Preserved supported event contract set (`1.0`) and output shape.

## Phase 2 — Core Implementation
- [x] Updated `_hs17_event_contract` in `hard_stops_events.py` to validate the full event stream.
- [x] Kept HS18 replay digest checks unchanged.
- [x] Kept HS19 kill-switch lineage and HS20 idempotency checks unchanged.

## Phase 3 — Safety and Failure Handling
- [x] Added negative test for malformed later event line.
- [x] Added negative test for later line missing required field.
- [x] Confirmed HS17 now fails closed for these invalid persisted-stream states.

## Phase 4 — Verification and Observability
- [x] Added tests in `test_event_lineage_replay_manifest.py`.
- [x] Ran focused suites:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_event_lineage_replay_manifest.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_hard_stop_schedule.py`
  - [x] Result: `12 passed`.

## Definition of Done
- [x] HS17 evaluates all persisted event lines, not just the first line.
- [x] Malformed or contract-incomplete later lines now fail HS17 deterministically.
- [x] Focused replay/event-lineage tests are green with no linter regressions.

## Test Cases
### Unit
- [x] Existing HS18/HS20 unit tests remain green.
- [x] `test_hs17_fails_when_later_event_line_is_malformed`.
- [x] `test_hs17_fails_when_later_event_line_missing_required_field`.

### Integration
- [x] `test_hard_stop_schedule.py` remains green with updated HS17 semantics.

### Negative
- [x] Non-JSON later event rows fail HS17.
- [x] Missing `occurred_at` on later event row fails HS17.

### Regression
- [x] HS18 replay-digest tamper detection test remains green.
- [x] HS20 duplicate committed mutation guard remains green.

## Out of Scope
- [x] Distributed event-store service semantics and external replay infrastructure.
- [x] Production control-plane lineage guarantees beyond repo-local artifacts and hard stops.
