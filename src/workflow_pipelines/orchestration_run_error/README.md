# Folder: `src/workflow_pipelines/orchestration_run_error`

## Why this folder exists
This folder groups code and artifacts for `orchestration_run_error` within the repository architecture.

## What is present
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `orchestration_run_error_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `surface.py` (file): Implements a concrete part of this folder responsibility.
- `contracts.py`: Contract/validation for `orchestration/run_error_runtime.json`.
- `runtime.py`: Deterministic run-error runtime derivation.
- `tests/test_runtime.py`: Determinism and fail-closed validation tests.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
