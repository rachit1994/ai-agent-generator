# Closure Security Reliability Scalability Plans

## Context
- [x] Confirmed scope and baseline (`23%`) from `docs/master-architecture-feature-completion.md`.
- [x] Audited read-only preflight behavior in `orchestrator/api/project_validate.py`.
- [x] Identified fail-open gap: malformed/unreadable `progress.json` produced warnings but still returned validation success.

## Assumptions and Constraints
- [x] Preflight must fail closed on malformed state artifacts used for execution decisions.
- [x] Missing `progress.json` remains acceptable; only existing invalid progress artifacts should fail.
- [x] Valid plan/workspace/intake behavior should remain unchanged.

## Phase 0 — Preconditions
- [x] Verified existing flow appended `progress_warnings` and returned `EXIT_VALIDATE_OK`.
- [x] Confirmed no dedicated tests asserted invalid `progress.json` should block validation.
- [x] Confirmed `validate_progress` already returns deterministic contract errors suitable for hard failure.

## Phase 1 — Contracts and Interfaces
- [x] Updated preflight contract:
  - [x] existing but invalid `progress.json` -> `EXIT_VALIDATE_INVALID`, `error=invalid_progress_json`
  - [x] unreadable `progress.json` -> `EXIT_VALIDATE_INVALID`, `error=progress_read_failed`
- [x] Kept success schema unchanged for valid progress payloads.
- [x] Kept missing progress file behavior unchanged.

## Phase 2 — Core Implementation
- [x] Implemented `_progress_preflight_or_error` helper to centralize fail-closed progress handling.
- [x] Replaced warning-only path with explicit invalid exits.
- [x] Preserved remaining validate flow (plan, cycle, workspace, lock, intake checks).

## Phase 3 — Safety and Failure Handling
- [x] Added negative tests for both invalid-structure and unreadable progress artifacts.
- [x] Confirmed invalid progress now blocks preflight before returning `ok=True`.
- [x] Confirmed valid progress path and intake projection remain intact.

## Phase 4 — Verification and Observability
- [x] Added tests:
  - [x] `test_validate_project_session_rejects_nonconforming_progress_json`
  - [x] `test_validate_project_session_rejects_unreadable_progress_json`
- [x] Ran focused suites:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_project_validate.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_project_meta.py`
  - [x] Result: `42 passed`.

## Definition of Done
- [x] Preflight now fail-closes malformed/unreadable progress state.
- [x] Negative tests cover both invalid schema and read failure scenarios.
- [x] Focused validate/meta suites are green.

## Test Cases
### Unit
- [x] Valid progress payload keeps validate success path.
- [x] Nonconforming progress payload fails with `invalid_progress_json`.
- [x] Unreadable progress payload fails with `progress_read_failed`.

### Integration
- [x] Existing workspace and plan-lock validation flows remain unchanged.
- [x] Intake projection still reports `progress_intake_loaded_last` for valid progress.

### Negative
- [x] Progress contract violations no longer degrade to warnings.
- [x] Broken progress JSON no longer passes preflight.

### Regression
- [x] Existing project validate tests remain green.
- [x] Project meta progress contract tests remain green.

## Out of Scope
- [x] Automatic repair/migration of malformed progress artifacts.
- [x] Runtime recovery flows beyond validation-stage rejection.
