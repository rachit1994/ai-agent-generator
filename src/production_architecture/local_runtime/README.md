# Folder: `src/production_architecture/local_runtime`

## Why this folder exists
This folder groups code and artifacts for `local_runtime` within the repository architecture.

## What is present
- `model_adapter` (folder): Wraps model-facing logic and invocation behavior.
- `orchestrator` (folder): Groups related implementation for this subdomain boundary.
- `__init__.py` (file): Implements a concrete part of this folder responsibility.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
