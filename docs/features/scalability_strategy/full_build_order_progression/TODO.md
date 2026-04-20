# Full Build Order Progression

## Context
- [x] Confirmed scope and baseline (`24%`) from `docs/master-architecture-feature-completion.md`.
- [x] Audited project-session progression behavior in `orchestrator/api/project_driver.py`.
- [x] Identified fail-closed gap: invalid `max_concurrent_agents` values (`True`, `0`) were not rejected at API ingress and could devolve into ambiguous runtime stop states.

## Assumptions and Constraints
- [x] Progression control should reject invalid budget/concurrency parameters before mutating session state.
- [x] Existing stop-report/session-event behavior for valid runs must remain unchanged.
- [x] Input contract strictness should align with existing fail-closed scheduler policy.

## Phase 0 — Preconditions
- [x] Verified `max_steps` already has strict input validation (`>=1`), while concurrency did not.
- [x] Verified scheduler-level checks alone are insufficient because invalid values still enter the main driver path.
- [x] Confirmed no test covered invalid `max_concurrent_agents` handling in driver ingress.

## Phase 1 — Contracts and Interfaces
- [x] Defined driver ingress rule: `max_concurrent_agents` must be `int` (not `bool`) and `>= 1`.
- [x] Added explicit `ValueError` contract for invalid concurrency inputs at `run_project_session` entry.
- [x] Preserved external signature and return schema for valid invocations.

## Phase 2 — Core Implementation
- [x] Implemented strict guard in `run_project_session`:
  - [x] reject non-`int` or `bool`
  - [x] reject values `< 1`
  - [x] raise `ValueError("max_concurrent_agents must be an integer >= 1")`
- [x] Added regression tests for both malformed boolean and non-positive integer cases.

## Phase 3 — Safety and Failure Handling
- [x] Ensured invalid concurrency fails fast before execution ticks and lease/worktree activity.
- [x] Ensured no fallback into misleading blocked states like `no_runnable_step` for bad inputs.
- [x] Ensured valid plans and parallel execution pathways remain unchanged.

## Phase 4 — Verification and Observability
- [x] Added `test_run_project_session_rejects_non_int_or_non_positive_concurrency`.
- [x] Ran focused suites:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_project_stop.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_project_parallel.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_project_scheduler.py`
  - [x] Result: `9 passed`.

## Definition of Done
- [x] Driver ingress now fail-closes malformed concurrency inputs.
- [x] Deterministic progression behavior is preserved for valid inputs.
- [x] Targeted unit suites are green.

## Test Cases
### Unit
- [x] Rejects `max_concurrent_agents=True`.
- [x] Rejects `max_concurrent_agents=0`.

### Integration
- [x] Existing project parallel path tests still pass unchanged.
- [x] Existing scheduler conflict/concurrency tests still pass unchanged.

### Negative
- [x] Invalid concurrency no longer reaches runtime progression loop.
- [x] Invalid concurrency fails with explicit `ValueError`.

### Regression
- [x] `test_parallel_worktrees_runs_both_steps` still green.
- [x] `test_parallel_disabled_without_git_or_flag_sequential` still green.

## Out of Scope
- [x] Dynamic autoscaling heuristics for concurrency selection.
- [x] Multi-session global arbitration beyond current session-local controls.
