# Folder: `src/production_architecture/local_runtime`

## Why this folder exists
This folder groups code and artifacts for `local_runtime` within the repository architecture.

## What is present
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `contracts.py` (file): Defines machine-checkable interface and schema expectations.
- `model_adapter` (folder): Wraps model-facing logic and invocation behavior.
- `orchestrator` (folder): Groups related implementation for this subdomain boundary.
- `runtime.py` (file): Implements a concrete part of this folder responsibility.
- `surface.py` (file): Implements a concrete part of this folder responsibility.
- `tests` (folder): Provides validation coverage for this folder behavior.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
