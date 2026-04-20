# Capability Growth Metrics

## Context
- [x] Confirmed scope and baseline (`12%`) from `docs/master-architecture-feature-completion.md`.
- [x] Audited capability evidence gate in `hard_stops_memory.py` (`HS23` skill surface).
- [x] Identified fail-closed gap: HS23 previously accepted any `nodes` list, including malformed or duplicate skill entries.

## Assumptions and Constraints
- [x] Scope is repo-local capability growth evidence quality through `capability/skill_nodes.json`.
- [x] Keep harness compatibility (empty `nodes` list remains allowed), while rejecting structurally invalid node entries.
- [x] Existing HS21/HS22/HS24 behavior should remain unchanged.

## Phase 0 — Preconditions
- [x] Verified HS23 only checked `schema_version` and `nodes` list type.
- [x] Verified no tests covered malformed node entries or duplicate skill IDs.
- [x] Verified memory hard-stop tests did not yet assert HS23 semantics explicitly.

## Phase 1 — Contracts and Interfaces
- [x] Hardened HS23 skill-node contract:
  - [x] each node must be an object
  - [x] each node must include non-empty `skill_id` (or camel-case `skillId`)
  - [x] each node must include numeric non-bool `score`
  - [x] duplicate skill IDs are rejected
- [x] Preserved top-level schema contract (`schema_version == "1.0"` and list `nodes`).

## Phase 2 — Core Implementation
- [x] Updated `_hs23_skill_surface` to validate per-node shape and duplicate IDs.
- [x] Kept no-op compatibility for empty `nodes` list.
- [x] Left other memory hard-stop checks untouched.

## Phase 3 — Safety and Failure Handling
- [x] Added negative test for malformed skill node missing `score`.
- [x] Added negative test for duplicate skill IDs across snake/camel key variants.
- [x] Confirmed HS23 now fails closed for malformed capability growth evidence.

## Phase 4 — Verification and Observability
- [x] Expanded `test_memory_hard_stops.py` with HS23 negative coverage.
- [x] Ran focused suites:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_memory_hard_stops.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_hard_stop_schedule.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_public_export_surface.py`
  - [x] Result: `218 passed`.

## Definition of Done
- [x] Capability growth evidence gate rejects malformed/duplicate skill node structures.
- [x] HS23 semantics are covered by explicit negative tests.
- [x] Focused memory hard-stop and regression suites are green and lint-clean.

## Test Cases
### Unit
- [x] `test_hs23_fails_when_skill_nodes_items_are_malformed`.
- [x] `test_hs23_fails_when_skill_nodes_have_duplicate_skill_ids`.

### Integration
- [x] `test_hard_stop_schedule.py` remains green with tightened HS23 behavior.
- [x] `test_public_export_surface.py` remains green with unchanged exports.

### Negative
- [x] Missing required capability-node score fails HS23.
- [x] Duplicate skill IDs fail HS23.

### Regression
- [x] Existing HS21 provenance-related tests remain green.
- [x] Existing HS22 quarantine and coding-only skip behavior remains green.

## Out of Scope
- [x] Multi-run capability trend analytics and dashboard pipelines.
- [x] Organization-wide growth scoring governance outside local run artifacts.
