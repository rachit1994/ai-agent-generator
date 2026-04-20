# Identity and authorization

## Context
- [x] Verified feature scope and baseline (`30%`) in `docs/master-architecture-feature-completion.md`.
- [x] Verified IAM/authorization-related hard stops in `hard_stops_organization.py` (HS29–HS32).
- [x] Focused closure on action-audit identity integrity in HS29 lease-audit enforcement.

## Assumptions and Constraints
- [x] Scope is repo-local identity/authz checks via permission matrix + action audit contracts.
- [x] HS29 should enforce actor attribution and action semantics per audit line, not just lease linkage.
- [x] Existing lease linkage validation and high-risk token checks should remain unchanged.

## Phase 0 — Preconditions
- [x] Confirmed HS29 validated `lease_id` membership but did not validate `action`, `actor_id`, or timestamp format.
- [x] Confirmed producer (`organization_layer.py`) already emits these fields, so stricter checks are compatible.
- [x] Confirmed existing tests covered lease mismatch/missing lease cases but not actor/action requirements.

## Phase 1 — Contracts and Interfaces
- [x] Tightened HS29 action-audit line requirements:
  - [x] `action` must be non-empty string.
  - [x] `actor_id` must be non-empty string.
  - [x] `occurred_at` must be ISO timestamp parseable by `parse_iso_utc`.
- [x] Preserved existing requirements:
  - [x] active lease existence
  - [x] valid permission matrix
  - [x] lease_id must be present and mapped to active leases

## Phase 2 — Core Implementation
- [x] Updated `_hs29_lease_audit` in `hard_stops_organization.py` with identity/authorization field validation.
- [x] Kept HS30/HS31/HS32 logic intact and unchanged.
- [x] Kept organization artifact producer payload shape unchanged.

## Phase 3 — Safety and Failure Handling
- [x] Added negative test for missing `action`/`actor_id` in action audit lines.
- [x] Confirmed existing lease mismatch and missing lease-id negative paths still fail closed.
- [x] Confirmed no regression in unrelated organization/evolution hard stop checks.

## Phase 4 — Verification and Observability
- [x] Expanded tests in `test_evolution_organization_hard_stops.py`.
- [x] Re-ran hard-stop schedule suite in `test_hard_stop_schedule.py`.
- [x] Re-ran export surface suite in `test_public_export_surface.py`.
- [x] Executed focused verification:
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_evolution_organization_hard_stops.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_hard_stop_schedule.py`
  - [x] `uv run pytest src/production_architecture/local_runtime/orchestrator/tests/unit/test_public_export_surface.py`
  - [x] Result: `222 passed`.

## Definition of Done
- [x] HS29 enforces actor-bound audit identity fields and parseable timestamps.
- [x] Lease-auth linkage remains enforced and compatible with existing IAM artifacts.
- [x] Organization/evolution hard-stop suites remain green under stricter authz validation.
- [x] Feature checklist is complete for repo-local identity/authz scope.

## Test Cases
### Unit
- [x] `test_hs29_fails_when_audit_lease_unknown`.
- [x] `test_hs29_fails_when_audit_line_missing_lease_id`.
- [x] `test_hs29_fails_when_audit_actor_or_action_missing`.

### Integration
- [x] `test_hard_stop_schedule.py` remains green.
- [x] `test_public_export_surface.py` remains green.

### Negative
- [x] Missing or malformed audit identity fields now fail HS29.
- [x] Invalid lease ownership still fails HS29.

### Regression
- [x] HS30/HS31/HS32 behaviors remain unchanged.
- [x] Existing organization hard-stop tests remain green with stricter HS29 checks.

## Out of Scope
- [x] Cryptographic identity, external IAM federation, and multi-tenant auth control planes.
- [x] Cross-repository policy distribution/governance beyond local hard-stop enforcement.
