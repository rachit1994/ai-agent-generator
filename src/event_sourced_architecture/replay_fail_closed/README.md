# Folder: `src/event_sourced_architecture/replay_fail_closed`

## Why this folder exists
This folder provides deterministic replay fail-closed verification artifacts for local runs.

## What is present
- `contracts.py`: Contract/validation for `replay/fail_closed.json`.
- `runtime.py`: Deterministic replay fail-closed derivation.
- `surface.py`: Implemented surface metadata.
- `tests/test_runtime.py`: Determinism and fail-closed validation tests.
