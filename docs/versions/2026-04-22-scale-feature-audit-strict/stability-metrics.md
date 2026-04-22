# Stability metrics (one-feature execution packet)

## Map
- Feature: `Stability metrics`
- Baseline: 34%
- Target: 100% with executable runtime evidence, fail-closed contracts, and deterministic tests.

## Gap
- Metric derivation existed but lacked explicit runtime execution telemetry on event quality.
- No execution-level accounting for malformed rows and out-of-range reliability values.
- Contract validation did not require an execution block.

## Red
- Added failing expectations for execution payload presence in the built artifact.
- Added runtime tests for malformed-row detection and reliability-violation capture.

## Green
- Implemented `execute_stability_runtime` in:
  - `src/success_criteria/stability_metrics/runtime.py`
- Runtime now emits:
  - `events_processed`
  - `stable_events_processed`
  - `malformed_event_rows`
  - `reliability_violations`
- Wired execution output into `build_stability_metrics`.
- Extended contract validation in:
  - `src/success_criteria/stability_metrics/contracts.py`
  - added mandatory, typed `execution` field checks with non-negative invariants.
- Exported runtime function in:
  - `src/success_criteria/stability_metrics/__init__.py`

## Harden
- Expanded deterministic tests in:
  - `src/success_criteria/stability_metrics/tests/test_runtime.py`
- Preserved existing arithmetic/status/evidence coherence checks while adding execution-level fail-close checks.

## Evidence
- Test command:
  - `uv run pytest src/success_criteria/stability_metrics/tests/test_runtime.py`
- Result:
  - `11 passed`

## Score
- Updated `docs/master-architecture-feature-completion.md`:
  - `Stability metrics` moved from `34` to `100`.

## Review
- Feature now has executable runtime quality gates with schema-enforced execution output and deterministic regressions.
- External production ingestion/alerting pipelines remain out of scope and do not block local completion criteria.
