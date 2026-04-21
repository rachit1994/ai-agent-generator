# Folder: `src/workflow_pipelines/run_manifest`

## Why this folder exists
This folder groups code and artifacts for `run_manifest` within the repository architecture.

## What is present
- `artifacts` (folder): Groups related implementation for this subdomain boundary.
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `run_manifest_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `contracts.py`: Contract/validation for `program/run_manifest_runtime.json`.
- `runtime.py`: Deterministic run-manifest runtime derivation.
- `surface.py`: Orchestrator surface descriptor.
- `tests/test_runtime.py`: Determinism and fail-closed validation tests.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
