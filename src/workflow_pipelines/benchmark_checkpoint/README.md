# Folder: `src/workflow_pipelines/benchmark_checkpoint`

## Why this folder exists
This folder groups code and artifacts for `benchmark_checkpoint` within the repository architecture.

## What is present
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `benchmark_checkpoint_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `surface.py` (file): Implements a concrete part of this folder responsibility.
- `contracts.py`: Contract/validation for `benchmark-checkpoint-runtime.json`.
- `runtime.py`: Deterministic benchmark-checkpoint runtime derivation.
- `tests/test_runtime.py`: Determinism and fail-closed validation tests.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
