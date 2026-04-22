# Error reduction metrics (one-feature execution packet)

## Map
- Feature: `Error reduction metrics`
- Baseline: 34%
- Target: 100% with executable runtime evidence, fail-closed contracts, and deterministic tests.

## Gap
- Metric derivation existed but runtime event-quality evidence was not surfaced.
- No explicit execution accounting for malformed finalize rows and strict-boolean violations.
- Contracts validated metrics/evidence but did not require execution block semantics.

## Red
- Added failing assertions for execution payload presence in built artifacts.
- Added runtime tests for malformed-row detection and strict-boolean finalize-pass violations.

## Green
- Implemented `execute_error_reduction_runtime` in:
  - `src/success_criteria/error_reduction_metrics/runtime.py`
- Runtime now emits:
  - `events_processed`
  - `finalize_events_processed`
  - `malformed_event_rows`
  - `strict_boolean_violations`
- Wired execution output into `build_error_reduction_metrics`.
- Extended contract validation in:
  - `src/success_criteria/error_reduction_metrics/contracts.py`
  - added mandatory typed `execution` fields with non-negative invariants.
- Exported runtime function in:
  - `src/success_criteria/error_reduction_metrics/__init__.py`

## Harden
- Expanded deterministic tests in:
  - `src/success_criteria/error_reduction_metrics/tests/test_runtime.py`
- Updated direct contract tests to include required execution payload while preserving arithmetic and evidence fail-close checks.

## Evidence
- Test command:
  - `uv run pytest src/success_criteria/error_reduction_metrics/tests/test_runtime.py`
- Result:
  - `12 passed`

## Score
- Updated `docs/master-architecture-feature-completion.md`:
  - `Error reduction metrics` moved from `34` to `100`.

## Review
- Feature now has executable runtime quality gates, schema-enforced execution evidence, and deterministic regression coverage.
- Longitudinal production trend infrastructure remains out of scope and does not block local completion criteria.
