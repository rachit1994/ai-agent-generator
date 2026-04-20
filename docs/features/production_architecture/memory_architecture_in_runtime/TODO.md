# Memory architecture in runtime

## Context
- [x] Verified feature scope and baseline (`30%`) in `docs/master-architecture-feature-completion.md`.
- [x] Verified memory hard-stop checks in `hard_stops_memory.py` (HS21–HS24).
- [x] Focused closure on provenance-chain reliability for runtime memory retrieval validation (HS21).

## Assumptions and Constraints
- [x] Scope is local runtime memory guardrail behavior, not a distributed memory service.
- [x] HS21 should validate retrieval provenance against all valid events in `event_store/run_events.jsonl`, not just the first line.
- [x] Malformed event lines should not crash checks and should not erase valid provenance discovered on other lines.

## Phase 0 — Preconditions
- [x] Confirmed HS21 currently derives provenance IDs from `run_events.jsonl`.
- [x] Confirmed prior implementation only inspected the first line of `run_events.jsonl`.
- [x] Confirmed this can create false negatives when valid provenance appears later in the event stream.

## Phase 1 — Contracts and Interfaces
- [x] Updated provenance extraction to scan all lines and collect all valid `event_id` values.
- [x] Defined malformed-line behavior as ignore-and-continue (fail-closed only when no valid provenance satisfies HS21).
- [x] Preserved HS21/HS22/HS23/HS24 external contract and token surface.

## Phase 2 — Core Implementation
- [x] Refactored `_provenance_ids_in_event_store` to iterate full JSONL stream.
- [x] Added tolerant parsing: skip blank/non-object/malformed lines while preserving valid IDs.
- [x] Kept downstream HS21 evaluation logic unchanged except for richer provenance set input.

## Phase 3 — Safety and Failure Handling
- [x] Added regression test for matching provenance found on a later event-store line.
- [x] Added regression test ensuring malformed lines do not block valid provenance resolution.
- [x] Confirmed existing unresolved-quarantine and coding-only skip behavior remain intact.

## Phase 4 — Verification and Observability
- [x] Expanded memory hard-stop tests in `test_memory_hard_stops.py`.
- [x] Re-ran hard-stop schedule suite in `test_hard_stop_schedule.py`.
- [x] Re-ran export surface suite in `test_public_export_surface.py`.
- [x] Executed focused verification:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_memory_hard_stops.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_hard_stop_schedule.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_public_export_surface.py`
  - [x] Result: `216 passed`.

## Definition of Done
- [x] HS21 provenance matching is robust across full event-store JSONL streams.
- [x] Malformed event lines are tolerated without sacrificing valid provenance detection.
- [x] Memory hard-stop and related orchestration suites pass with no regressions.
- [x] Feature checklist is complete for repo-local runtime memory scope.

## Test Cases
### Unit
- [x] `test_hs21_fails_when_provenance_not_in_event_store`.
- [x] `test_hs21_passes_when_matching_provenance_is_on_later_event_line`.
- [x] `test_hs21_ignores_malformed_event_lines_but_uses_valid_ids`.

### Integration
- [x] `test_hard_stop_schedule.py` remains green.
- [x] `test_public_export_surface.py` remains green.

### Negative
- [x] Provenance mismatch still fails HS21.
- [x] Malformed event lines do not produce false pass without a valid matching `event_id`.

### Regression
- [x] Existing HS22 unresolved quarantine behavior remains unchanged.
- [x] Existing coding-only skip behavior remains unchanged.

## Out of Scope
- [x] Persistent distributed memory store and cross-run memory lifecycle orchestration.
- [x] External memory indexing/search infrastructure beyond local file-based artifacts.
