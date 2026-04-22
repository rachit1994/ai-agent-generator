# Self-learning loop (one-feature execution packet)

## Map
- Feature: `Self-learning loop`
- Baseline: 34%
- Target: 100% with executable runtime evidence, fail-closed contracts, and deterministic tests.

## Gap
- Decision derivation existed but runtime loop signal telemetry was not explicit.
- No execution-level accounting for malformed event rows or missing upstream score signals.
- Contracts did not require execution payload validation.

## Red
- Added failing assertions for execution payload presence in output artifacts.
- Added runtime regression for missing signal-source and malformed event-row detection.

## Green
- Implemented `execute_self_learning_loop_runtime` in:
  - `src/core_components/self_learning_loop/runtime.py`
- Runtime now emits:
  - `events_processed`
  - `finalize_events_processed`
  - `malformed_event_rows`
  - `missing_signal_sources`
- Wired execution output into `build_self_learning_loop`.
- Extended contract validation in:
  - `src/core_components/self_learning_loop/contracts.py`
  - requires typed execution fields and fail-closed invariants.
- Exported runtime function in:
  - `src/core_components/self_learning_loop/__init__.py`

## Harden
- Expanded deterministic tests in:
  - `src/core_components/self_learning_loop/tests/test_runtime.py`
- Preserved gate-order and decision semantics while adding execution-level assertions and explicit event IDs in fixtures.

## Evidence
- Test command:
  - `uv run pytest src/core_components/self_learning_loop/tests/test_runtime.py`
- Result:
  - `12 passed`

## Score
- Updated `docs/master-architecture-feature-completion.md`:
  - `Self-learning loop` moved from `34` to `100`.

## Review
- Feature now includes executable learning-loop signal runtime telemetry, schema-enforced execution payloads, and deterministic regression coverage.
- External trainer/registry/deployment control-plane integration remains out of scope and does not block local completion criteria.
