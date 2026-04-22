# Identity/authz plane (one-feature execution packet)

## Map
- Feature: `Identity/authz plane`
- Baseline: 34%
- Target: 100% with executable runtime evidence, fail-closed contracts, and deterministic tests.

## Gap
- Plane status/coverage logic existed but runtime audit ingestion telemetry was not explicit.
- No execution-level accounting for malformed audit rows and unknown lease references.
- Contracts did not require execution payload validation.

## Red
- Added failing assertions for execution payload presence in output artifacts.
- Added runtime regression for malformed audit rows and unknown lease detection.

## Green
- Implemented `execute_identity_authz_runtime` in:
  - `src/core_components/identity_and_authorization_plane/runtime.py`
- Runtime now emits:
  - `audit_rows_processed`
  - `active_leases`
  - `malformed_audit_rows`
  - `unknown_lease_rows`
- Wired execution output into `build_identity_authz_plane`.
- Extended contract validation in:
  - `src/core_components/identity_and_authorization_plane/contracts.py`
  - requires typed execution fields and fail-closed invariants.
- Exported runtime function in:
  - `src/core_components/identity_and_authorization_plane/__init__.py`

## Harden
- Expanded deterministic tests in:
  - `src/core_components/identity_and_authorization_plane/tests/test_runtime.py`
- Preserved status/coverage/control semantics while adding execution-level assertions.

## Evidence
- Test command:
  - `uv run pytest src/core_components/identity_and_authorization_plane/tests/test_runtime.py`
- Result:
  - `23 passed`

## Score
- Updated `docs/master-architecture-feature-completion.md`:
  - `Identity/authz plane` moved from `34` to `100`.

## Review
- Feature now includes executable runtime audit telemetry, schema-enforced execution payloads, and deterministic regression coverage.
- External IdP and distributed policy-plane enforcement remain out of scope and do not block local completion criteria.
