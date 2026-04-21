# Folder: `src/production_architecture/orchestration`

## Why this folder exists
This folder provides deterministic production orchestration artifacts for local runs.

## What is present
- `contracts.py`: Contract/validation for `orchestration/production_orchestration.json`.
- `runtime.py`: Deterministic orchestration derivation.
- `surface.py`: Implemented surface metadata.
- `tests/test_runtime.py`: Determinism and fail-closed validation tests.
# Folder: `src/production_architecture/orchestration`

## Why this folder exists
This folder groups code and artifacts for `orchestration` within the repository architecture.

## What is present
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `surface.py` (file): Implements a concrete part of this folder responsibility.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
