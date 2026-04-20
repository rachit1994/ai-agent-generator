# Folder: `src/production_architecture`

## Why this folder exists
This folder groups code and artifacts for `production_architecture` within the repository architecture.

## What is present
- `identity_and_authorization` (folder): Groups related implementation for this subdomain boundary.
- `local_runtime` (folder): Groups related implementation for this subdomain boundary.
- `memory` (folder): Implements memory handling and memory-related lifecycle logic.
- `observability` (folder): Groups related implementation for this subdomain boundary.
- `orchestration` (folder): Defines orchestration event or state contracts for run flow.
- `storage` (folder): Handles file or state persistence concerns.
- `__init__.py` (file): Implements a concrete part of this folder responsibility.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
