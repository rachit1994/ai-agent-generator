# Practice engine (one-feature execution packet)

## Map
- Feature: `Practice engine`
- Baseline: 34%
- Target: 100% with executable runtime evidence, fail-closed contracts, and deterministic tests.

## Gap
- Practice readiness derivation existed but runtime input telemetry was not explicit.
- No execution-level accounting for malformed root-cause rows and missing practice input sources.
- Contracts did not require execution payload validation.

## Red
- Added failing assertions for execution payload presence in output artifacts.
- Added runtime regression for missing-source and malformed root-cause detection.

## Green
- Implemented `execute_practice_engine_runtime` in:
  - `src/core_components/practice_engine/runtime.py`
- Runtime now emits:
  - `signals_processed`
  - `root_causes_processed`
  - `malformed_root_cause_rows`
  - `missing_signal_sources`
- Wired execution output into `build_practice_engine`.
- Extended contract validation in:
  - `src/core_components/practice_engine/contracts.py`
  - requires typed execution fields and fail-closed invariants.
- Exported runtime function in:
  - `src/core_components/practice_engine/__init__.py`

## Harden
- Expanded deterministic tests in:
  - `src/core_components/practice_engine/tests/test_runtime.py`
- Preserved status/result/evidence semantics while adding execution-level assertions.

## Evidence
- Test command:
  - `uv run pytest src/core_components/practice_engine/tests/test_runtime.py`
- Result:
  - `8 passed`

## Score
- Updated `docs/master-architecture-feature-completion.md`:
  - `Practice engine` moved from `34` to `100`.

## Review
- Feature now includes executable runtime practice telemetry, schema-enforced execution payloads, and deterministic regression coverage.
- Mature external progression/feedback systems remain out of scope and do not block local completion criteria.
