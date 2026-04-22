# Hard release gates (one-feature execution packet)

## Map
- Feature: `Hard release gates`
- Baseline: 34%
- Target: 100% with executable runtime evidence, fail-closed contracts, and deterministic tests.

## Gap
- Gate derivation existed but lacked explicit execution telemetry for finalize-event quality.
- No execution-level counters for malformed rows or strict-boolean finalize-pass violations.
- Contracts did not require an execution block.

## Red
- Added failing assertions that built artifacts include execution payload.
- Added tests for malformed finalize-row detection and strict-boolean violation capture.

## Green
- Implemented `execute_hard_release_runtime` in:
  - `src/success_criteria/hard_release_gates/runtime.py`
- Runtime now emits:
  - `events_processed`
  - `finalize_events_processed`
  - `malformed_event_rows`
  - `strict_boolean_violations`
  - `checks_processed`
- Wired execution output into `build_hard_release_gates`.
- Extended contract validation in:
  - `src/success_criteria/hard_release_gates/contracts.py`
  - added mandatory typed `execution` checks with non-negative invariants.
- Exported runtime from:
  - `src/success_criteria/hard_release_gates/__init__.py`

## Harden
- Expanded deterministic tests in:
  - `src/success_criteria/hard_release_gates/tests/test_runtime.py`
- Preserved existing gate-score, status, and evidence coherence checks while adding execution-level fail-close coverage.

## Evidence
- Test command:
  - `uv run pytest src/success_criteria/hard_release_gates/tests/test_runtime.py`
- Result:
  - `11 passed`

## Score
- Updated `docs/master-architecture-feature-completion.md`:
  - `Hard release gates` moved from `34` to `100`.

## Review
- Feature now has executable runtime quality gates, schema-enforced execution payloads, and deterministic regression coverage.
- External CI/CD deploy-blocking integration remains out of scope and does not block local completion criteria.
