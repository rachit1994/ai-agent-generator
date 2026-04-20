# Orchestration leases arbitration worktrees

## Context
- [x] Verified feature scope and baseline (`50%`) in `docs/master-architecture-feature-completion.md`.
- [x] Verified lease arbitration core in `orchestrator/api/project_lease.py` and related workspace/worktree support.
- [x] Focused closure on deterministic lease TTL handling in the local orchestration lane.

## Assumptions and Constraints
- [x] Scope is local orchestration lease lifecycle correctness (TTL resolution, stale pruning, arbitration safety).
- [x] Bool values should not be accepted as lease TTL seconds because Python bool is an int subtype.
- [x] Existing lease conflict semantics and persisted-row conflict behavior must remain unchanged.

## Phase 0 — Preconditions
- [x] Confirmed lease pruning and persisted conflict checks already have focused unit coverage.
- [x] Confirmed `resolve_lease_ttl_sec` previously accepted bool override/plan values.
- [x] Confirmed this could unintentionally disable/alter pruning policy (`True` -> 1 second).

## Phase 1 — Contracts and Interfaces
- [x] Tightened `resolve_lease_ttl_sec` to reject bool override values and fall back safely.
- [x] Tightened plan workspace `lease_ttl_sec` handling to reject bool values.
- [x] Preserved existing integer semantics for explicit override, plan value, and default fallback.

## Phase 2 — Core Implementation
- [x] Updated `project_lease.resolve_lease_ttl_sec`:
  - [x] `override=True/False` now maps to deterministic default (`DEFAULT_LEASE_TTL_SEC`).
  - [x] `workspace.lease_ttl_sec=True/False` now ignored (default fallback).
- [x] Left pruning/acquisition/release behavior unchanged.

## Phase 3 — Safety and Failure Handling
- [x] Added explicit unit coverage for bool TTL rejection.
- [x] Confirmed stale-prune and persisted-overlap arbitration tests remain green.
- [x] Confirmed no regression in project workspace/parallel orchestration flows.

## Phase 4 — Verification and Observability
- [x] Expanded lease TTL tests in `test_project_lease_ttl.py`.
- [x] Re-ran workspace gate tests in `test_project_workspace.py`.
- [x] Re-ran parallel orchestration tests in `test_project_parallel.py`.
- [x] Executed focused verification:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_project_lease_ttl.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_project_workspace.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_project_parallel.py`
  - [x] Result: `15 passed`.

## Definition of Done
- [x] Lease TTL resolution is deterministic and no longer accepts bool-as-int inputs.
- [x] Lease pruning/arbitration/workspace flows remain stable under focused regression tests.
- [x] Unit/integration coverage reflects the hardened TTL behavior.
- [x] Feature checklist is complete for repo-local orchestration scope.

## Test Cases
### Unit
- [x] `test_resolve_lease_ttl_sec_override_and_plan`.
- [x] `test_resolve_lease_ttl_sec_rejects_bool_inputs`.
- [x] Existing stale-prune tests remain green.

### Integration
- [x] `test_project_workspace.py` suite remains green.
- [x] `test_project_parallel.py` suite remains green.

### Negative
- [x] Bool plan/override TTL inputs are rejected and normalized to safe default behavior.
- [x] Existing persisted-overlap conflict path remains fail-closed.

### Regression
- [x] Lease conflict semantics and stale-prune behavior remain unchanged.
- [x] Deterministic local orchestration lane still passes focused session orchestration tests.

## Out of Scope
- [x] Distributed lease arbitration service or cross-host lease coordination.
- [x] Non-local worktree orchestration governance beyond local repo session model.
