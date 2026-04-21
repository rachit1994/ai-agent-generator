# Folder: `src/core_components/evaluation_service`

## Why this folder exists
This folder groups code and artifacts for `evaluation_service` within the repository architecture.

## What is present
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `surface.py` (file): Implements a concrete part of this folder responsibility.
- `contracts.py`: Contract/validation for `evaluation/service_runtime.json`.
- `runtime.py`: Deterministic evaluation-service runtime derivation.
- `tests/test_runtime.py`: Determinism and fail-closed validation tests.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
