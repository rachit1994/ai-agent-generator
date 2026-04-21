# Folder: `src/event_sourced_architecture/event_store`

## Why this folder exists
This folder groups code and artifacts for `event_store` within the repository architecture.

## What is present
- `contracts.py`: Contract/validation for `event_store/semantics.json`.
- `runtime.py`: Deterministic event-store semantics derivation.
- `surface.py`: Implemented surface metadata for orchestrator discovery.
- `tests/test_runtime.py`: Determinism and fail-closed validation tests.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
