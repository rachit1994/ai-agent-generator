# Learning service (one-feature execution packet)

## Map
- Feature: `Learning service`
- Baseline: 34%
- Target: 100% with executable runtime evidence, fail-closed contracts, and deterministic tests.

## Gap
- Service health derivation existed but runtime signal telemetry was not explicitly captured.
- No execution-level accounting for malformed event rows and missing learning signal sources.
- Contracts did not require an execution payload.

## Red
- Added failing assertions for execution payload presence in output artifacts.
- Added runtime regression for missing signal-source and malformed event-row detection.

## Green
- Implemented `execute_learning_service_runtime` in:
  - `src/core_components/learning_service/runtime.py`
- Runtime now emits:
  - `reflections_processed`
  - `canary_rows_processed`
  - `finalize_events_processed`
  - `malformed_event_rows`
  - `missing_signal_sources`
- Wired execution output into `build_learning_service`.
- Extended contract validation in:
  - `src/core_components/learning_service/contracts.py`
  - requires typed execution fields and fail-closed invariants.
- Exported runtime function in:
  - `src/core_components/learning_service/__init__.py`

## Harden
- Expanded deterministic tests in:
  - `src/core_components/learning_service/tests/test_runtime.py`
- Preserved existing strict finalize-pass and metric/status/evidence coherence checks while adding execution-level assertions.

## Evidence
- Test command:
  - `uv run pytest src/core_components/learning_service/tests/test_runtime.py`
- Result:
  - `8 passed`

## Score
- Updated `docs/master-architecture-feature-completion.md`:
  - `Learning service` moved from `34` to `100`.

## Review
- Feature now includes executable runtime learning-signal telemetry, schema-enforced execution payloads, and deterministic regression coverage.
- Durable external feedback/model-update infrastructure remains out of scope and does not block local completion criteria.
