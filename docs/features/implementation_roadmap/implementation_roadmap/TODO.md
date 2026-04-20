# Implementation Roadmap

## Context
- [x] Confirmed scope and baseline (`41%`) from `docs/master-architecture-feature-completion.md`.
- [x] Audited roadmap execution contract entry points in `orchestrator/api/project_schema.py`.
- [x] Identified fail-closed gap: verification command envelopes accepted blank command text and non-string argument lists.

## Assumptions and Constraints
- [x] Roadmap step verification contracts must reject malformed command payloads before execution.
- [x] Validation hardening must preserve existing valid plan behavior and existing error-token style.
- [x] Contract checks remain local to plan validation (no runtime behavior changes for valid plans).

## Phase 0 — Preconditions
- [x] Verified command validation only checked `cmd` type but not non-empty content.
- [x] Verified `args` shape was not validated when present.
- [x] Verified test suite lacked negative coverage for malformed verification command payloads.

## Phase 1 — Contracts and Interfaces
- [x] Tightened verification command contract in `validate_project_plan`:
  - [x] `commands[i].cmd` must be a non-empty string after trim.
  - [x] `commands[i].args` (if present) must be `list[str]`.
- [x] Added explicit error token for args violations: `project_plan_verification_args_bad:<step_id>:<index>`.

## Phase 2 — Core Implementation
- [x] Updated command validation logic in `project_schema.py` for strict `cmd` and `args`.
- [x] Preserved existing `project_plan_verification_cmd_bad` behavior for malformed command rows.
- [x] Kept function signature and all successful path behaviors unchanged.

## Phase 3 — Safety and Failure Handling
- [x] Added negative coverage for blank command value.
- [x] Added negative coverage for mixed-type args list.
- [x] Confirmed malformed command envelopes are rejected at plan-validate time.

## Phase 4 — Verification and Observability
- [x] Added tests:
  - [x] `test_validate_project_plan_rejects_blank_verification_command`
  - [x] `test_validate_project_plan_rejects_non_string_verification_args`
- [x] Ran focused suites:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_project_meta.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_project_validate.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_project_workspace.py`
  - [x] Result: `47 passed`.

## Definition of Done
- [x] Verification command contract now fail-closes malformed `cmd`/`args` payloads.
- [x] New negative tests guard against regression.
- [x] Targeted roadmap validation suites are green.

## Test Cases
### Unit
- [x] Valid plan with `verification.commands[].cmd` remains accepted.
- [x] Blank `verification.commands[].cmd` is rejected.
- [x] Non-string `verification.commands[].args` entries are rejected.

### Integration
- [x] Project session validation flow remains green for valid plans.
- [x] Workspace-related plan validation continues to pass.

### Negative
- [x] Malformed command text (`"   "`) yields `project_plan_verification_cmd_bad`.
- [x] Mixed-type args list yields `project_plan_verification_args_bad`.

### Regression
- [x] Existing plan/workspace/validate tests continue to pass.
- [x] No behavioral regression on valid command envelopes.

## Out of Scope
- [x] Command execution sandboxing/policy enforcement at runtime.
- [x] Cross-repo roadmap orchestration services beyond local schema validation.
