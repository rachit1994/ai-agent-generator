# Folder: `src/production_architecture/observability`

## Why this folder exists
This folder provides deterministic production observability artifacts for local runs.

## What is present
- `contracts.py`: Contract/validation for `observability/production_observability.json`.
- `runtime.py`: Deterministic observability derivation.
- `surface.py`: Implemented surface metadata.
- `tests/test_runtime.py`: Determinism and fail-closed validation tests.
# Folder: `src/production_architecture/observability`

## Why this folder exists
This folder groups code and artifacts for `observability` within the repository architecture.

## What is present
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `project_stage1_observability_export.py` (file): Implements a concrete part of this folder responsibility.
- `surface.py` (file): Implements a concrete part of this folder responsibility.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
