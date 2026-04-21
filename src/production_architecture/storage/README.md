# Folder: `src/production_architecture/storage`

## Why this folder exists
This folder groups code and artifacts for `storage` within the repository architecture.

## What is present
- `storage` (folder): Handles file or state persistence concerns.
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `contracts.py` (file): Storage architecture artifact contract and validator.
- `runtime.py` (file): Deterministic storage architecture derivation.
- `surface.py` (file): Top-level feature-surface metadata.
- `tests/` (folder): Unit tests for storage architecture runtime.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
