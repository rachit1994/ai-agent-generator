# Folder: `src/workflow_pipelines/benchmark_orchestration_jsonl`

## Why this folder exists
This folder groups code and artifacts for `benchmark_orchestration_jsonl` within the repository architecture.

## What is present
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `orchestration_benchmark_jsonl_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `surface.py` (file): Implements a concrete part of this folder responsibility.
- `contracts.py`: Contract/validation for `benchmark-orchestration-runtime.json`.
- `runtime.py`: Deterministic benchmark-orchestration runtime derivation.
- `tests/test_runtime.py`: Determinism and fail-closed validation tests.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
