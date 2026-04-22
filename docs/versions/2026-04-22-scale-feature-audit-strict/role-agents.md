# Role agents (one-feature execution packet)

## Map
- Feature: `Role agents`
- Baseline: 34%
- Target: 100% with executable runtime evidence, fail-closed contracts, and deterministic tests.

## Gap
- Role scoring derivation existed but runtime signal-quality evidence was not explicit.
- No execution-level counters for malformed rows and strict-boolean finalize-pass violations.
- Contracts did not require execution payload validation.

## Red
- Added failing assertions that artifacts include execution payload.
- Added runtime regression for malformed-row and strict-boolean violation detection.

## Green
- Implemented `execute_role_agents_runtime` in:
  - `src/core_components/role_agents/runtime.py`
- Runtime now emits:
  - `checks_processed`
  - `finalize_events_processed`
  - `malformed_event_rows`
  - `strict_boolean_violations`
- Wired execution output into `build_role_agents`.
- Extended contract validation in:
  - `src/core_components/role_agents/contracts.py`
  - requires typed execution fields and fail-closed invariants.
- Exported runtime function in:
  - `src/core_components/role_agents/__init__.py`

## Harden
- Expanded deterministic tests in:
  - `src/core_components/role_agents/tests/test_runtime.py`
- Updated direct contract payload fixture to include required execution block while preserving spread/evidence semantics checks.

## Evidence
- Test command:
  - `uv run pytest src/core_components/role_agents/tests/test_runtime.py`
- Result:
  - `7 passed`

## Score
- Updated `docs/master-architecture-feature-completion.md`:
  - `Role agents` moved from `34` to `100`.

## Review
- Feature now includes executable runtime telemetry, schema-enforced execution payloads, and deterministic regression coverage.
- Fully autonomous multi-agent orchestration remains out of scope and does not block local completion criteria.
