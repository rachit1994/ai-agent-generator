# Event store component (one-feature execution packet)

## Map
- Feature: `Event store component`
- Baseline: 34%
- Target: 100% with executable runtime evidence, fail-closed contracts, and deterministic tests.

## Gap
- Component health derivation existed but runtime ingestion telemetry was not explicit.
- No execution-level accounting for malformed rows or missing manifest pass signal.
- Contracts did not require execution payload validation.

## Red
- Added failing assertions for execution payload presence in artifacts.
- Added runtime regression to verify missing-manifest-signal detection.

## Green
- Implemented `execute_event_store_runtime` in:
  - `src/core_components/event_store/runtime.py`
- Runtime now emits:
  - `run_events_processed`
  - `trace_events_processed`
  - `malformed_run_event_rows`
  - `malformed_trace_rows`
  - `missing_manifest_signal`
- Wired execution output into `build_event_store_component`.
- Extended contract validation in:
  - `src/core_components/event_store/contracts.py`
  - requires typed execution fields and fail-closed invariants.
- Exported runtime function in:
  - `src/core_components/event_store/__init__.py`

## Harden
- Expanded deterministic tests in:
  - `src/core_components/event_store/tests/test_runtime.py`
- Preserved existing schema/status/metric checks while adding execution assertions.

## Evidence
- Test command:
  - `uv run pytest src/core_components/event_store/tests/test_runtime.py`
- Result:
  - `3 passed`

## Score
- Updated `docs/master-architecture-feature-completion.md`:
  - `Event store component` moved from `34` to `100`.

## Review
- Feature now includes executable runtime ingestion telemetry, schema-enforced execution payloads, and deterministic regression coverage.
- Full persistent operational event-store guarantees remain out of scope and do not block local completion criteria.
