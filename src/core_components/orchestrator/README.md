# Folder: `src/core_components/orchestrator`

## Why this folder exists
This folder groups code and artifacts for `orchestrator` within the repository architecture.

## What is present
- `common` (folder): Groups related implementation for this subdomain boundary.
- `sde_types` (folder): Groups related implementation for this subdomain boundary.
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `contracts.py`: Contract/validation for `orchestrator/component_runtime.json`.
- `runtime.py`: Deterministic orchestrator-component runtime derivation.
- `surface.py`: Orchestrator feature surface descriptor.
- `tests/test_component_runtime.py`: Determinism and fail-closed tests.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
