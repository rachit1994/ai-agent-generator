# Service Boundaries

## Context
- [x] Confirmed scope and baseline (`18%`) from `docs/master-architecture-feature-completion.md`.
- [x] Audited workspace boundary checks in `orchestrator/api/project_workspace.py`.
- [x] Identified fail-closed gap: path-scope prefix checks allowed "overlap" in both directions, so a broad scope (e.g. `src/**`) could pass against a narrow allowed service prefix.

## Assumptions and Constraints
- [x] Scope is repo-local service boundary enforcement via `workspace.allowed_path_prefixes` and per-step `path_scope`.
- [x] Allowed prefixes must constrain step scopes (`scope ⊆ allowed`), not just overlap.
- [x] Existing validation and runtime workspace gate interfaces must remain unchanged.

## Phase 0 — Preconditions
- [x] Verified current `path_scope_pattern_allowed` allowed bidirectional prefix overlap.
- [x] Verified no explicit tests rejected broad scopes that exceed narrow allowed service prefixes.
- [x] Verified plan validation relies on this helper for boundary checks.

## Phase 1 — Contracts and Interfaces
- [x] Tightened contract for `path_scope_pattern_allowed`:
  - [x] only permit when normalized scope prefix starts with an allowed prefix
  - [x] reject patterns outside allowed prefixes, including broad supersets
- [x] Preserved existing input and return signature.

## Phase 2 — Core Implementation
- [x] Updated `path_scope_pattern_allowed` containment logic from overlap to strict containment.
- [x] Refactored workspace-path validation internals to helper functions:
  - [x] `_normalized_allowed_prefixes`
  - [x] `_path_scope_errors_for_step`
- [x] Preserved externally visible behavior/error token format for existing valid/invalid cases.

## Phase 3 — Safety and Failure Handling
- [x] Added negative test for broad scope against narrow allowed prefix.
- [x] Confirmed out-of-prefix scopes are rejected at plan-validate time.
- [x] Confirmed no regressions in branch gate and other workspace checks.

## Phase 4 — Verification and Observability
- [x] Expanded `test_project_workspace.py` with strict-boundary coverage.
- [x] Ran focused suites:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_project_workspace.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_project_validate.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_public_export_surface.py`
  - [x] Result: `222 passed`.

## Definition of Done
- [x] Workspace allowed prefixes now enforce strict service-boundary containment.
- [x] Broad/superset step scopes are no longer accepted against narrow allowed prefixes.
- [x] Focused workspace/validation/export suites are green and lint-clean.

## Test Cases
### Unit
- [x] `test_path_scope_pattern_allowed_overlap`.
- [x] `test_path_scope_pattern_allowed_rejects_broader_scope_than_allowed_prefix`.

### Integration
- [x] `test_validate_project_plan_workspace_path_violation`.
- [x] `test_validate_project_session_workspace_gate`.

### Negative
- [x] Broad scope (`src/**`) fails when only a narrow service subtree is allowed.
- [x] Outside-prefix patterns continue to fail.

### Regression
- [x] Existing workspace branch checks remain green.
- [x] Public export surface remains stable.

## Out of Scope
- [x] Cross-repository service boundary governance and centralized policy engines.
- [x] Production control-plane enforcement beyond repo-local plan/workspace validation.
