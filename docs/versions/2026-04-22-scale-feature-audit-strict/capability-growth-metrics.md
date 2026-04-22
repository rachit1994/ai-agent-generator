# Capability growth metrics (one-feature execution packet)

## Map
- Feature: `Capability growth metrics`
- Baseline: 34%
- Target: 100% with executable runtime evidence, fail-closed contracts, and deterministic tests.

## Gap
- Artifact previously derived metrics from finalize traces but did not expose runtime execution evidence.
- No explicit runtime accounting for malformed finalize rows and reliability-range violations.
- Contracts did not require or validate execution block shape.

## Red
- Added failing expectations that execution metadata is present in produced artifacts.
- Added runtime-focused tests for malformed event-row counting and reliability violation capture.

## Green
- Implemented `execute_capability_growth_runtime` in:
  - `src/success_criteria/capability_growth_metrics/runtime.py`
- Runtime now computes:
  - `events_processed`
  - `growth_events_processed`
  - `malformed_event_rows`
  - `reliability_violations`
  - `skill_node_count`
- Wired execution block into `build_capability_growth_metrics`.
- Extended contract validation in:
  - `src/success_criteria/capability_growth_metrics/contracts.py`
  - required typed execution fields and non-negative integer invariants.
- Exported runtime function from:
  - `src/success_criteria/capability_growth_metrics/__init__.py`

## Harden
- Added deterministic tests and fail-closed regressions:
  - `src/success_criteria/capability_growth_metrics/tests/test_runtime.py`
- Verified strict metric coherence checks still pass with new execution payload.

## Evidence
- Test command:
  - `uv run pytest src/success_criteria/capability_growth_metrics/tests/test_runtime.py`
- Result:
  - `10 passed`

## Score
- Updated `docs/master-architecture-feature-completion.md`:
  - `Capability growth metrics` moved from `34` to `100`.

## Review
- Runtime behavior is now executable, schema-constrained, and fail-closed for malformed/invalid finalize evidence.
- Remaining out-of-scope item is external long-horizon analytics infrastructure, which does not block local feature completion gates.
