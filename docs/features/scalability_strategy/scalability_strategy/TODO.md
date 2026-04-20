# Scalability Strategy

## Context
- [x] Confirmed scope and baseline (`14%`) from `docs/master-architecture-feature-completion.md`.
- [x] Audited parallel scheduling path in `orchestrator/api/project_scheduler.py`.
- [x] Identified fail-closed gap: malformed `path_scope` values could degrade to empty scopes and appear non-conflicting, enabling unsafe parallelism.

## Assumptions and Constraints
- [x] Scope is repo-local multi-agent tick scheduling and conflict arbitration under malformed plan inputs.
- [x] Malformed scope definitions must not increase parallelism.
- [x] Existing valid-disjoint scope behavior should remain unchanged.

## Phase 0 — Preconditions
- [x] Verified scheduler selected steps by path-scope conflict checks.
- [x] Verified malformed/non-list/non-string scopes previously degraded to `[]` (low-conflict behavior).
- [x] Verified no dedicated scheduler unit tests for malformed scope fail-closed behavior.

## Phase 1 — Contracts and Interfaces
- [x] Added explicit scope-normalization contract:
  - [x] `path_scope` absent -> valid empty scope
  - [x] non-list `path_scope` -> malformed
  - [x] non-string/blank entries -> malformed
- [x] Added concurrency guard contract:
  - [x] `max_concurrent_agents` must be int and not bool
- [x] Preserved step ordering and output shape.

## Phase 2 — Core Implementation
- [x] Added `_normalize_scopes` helper.
- [x] Added `_by_step_id` helper.
- [x] Added `_conflicts_with_chosen` helper.
- [x] Updated `select_steps_for_tick` to fail closed on malformed scopes:
  - [x] malformed first candidate can run alone
  - [x] malformed scopes conflict with any concurrently chosen step

## Phase 3 — Safety and Failure Handling
- [x] Added negative test for non-int/bool concurrency budget.
- [x] Added negative test for malformed path scopes forcing sequential selection.
- [x] Confirmed no regression in existing parallel worktree behavior tests.

## Phase 4 — Verification and Observability
- [x] Added `test_project_scheduler.py` with fail-closed scheduler coverage.
- [x] Ran focused suites:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_project_scheduler.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_project_parallel.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_public_export_surface.py`
  - [x] Result: `209 passed`.

## Definition of Done
- [x] Scheduler no longer parallelizes unsafe malformed scope plans.
- [x] Concurrency budget typing is fail-closed.
- [x] Focused scheduler/parallel/export suites are green and lint-clean.

## Test Cases
### Unit
- [x] `test_select_steps_for_tick_fails_closed_on_non_int_concurrency`.
- [x] `test_select_steps_for_tick_treats_malformed_path_scope_as_conflicting`.

### Integration
- [x] `test_parallel_worktrees_runs_both_steps` remains green.
- [x] `test_parallel_disabled_without_git_or_flag_sequential` remains green.

### Negative
- [x] Malformed `path_scope` definitions no longer allow unsafe concurrent scheduling.
- [x] Bool/non-int concurrency values are rejected.

### Regression
- [x] Existing parallel execution flow remains intact for valid plans.
- [x] Public export surface remains stable.

## Out of Scope
- [x] Distributed multi-host scheduling and remote worker orchestration.
- [x] Production control-plane autoscaling and queue-depth based admission control.
