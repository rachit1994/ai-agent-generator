# Folder: `src/production_architecture/local_runtime/orchestrator`

## Why this folder exists
This folder groups code and artifacts for `orchestrator` within the repository architecture.

## What is present
- `api` (folder): Exposes callable API surface for this subsystem.
- `runtime` (folder): Groups related implementation for this subdomain boundary.
- `tests` (folder): Provides validation coverage for this folder behavior.
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `README.md` (file): Documents folder behavior and usage context.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
