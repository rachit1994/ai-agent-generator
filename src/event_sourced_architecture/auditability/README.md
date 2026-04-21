# Folder: `src/event_sourced_architecture/auditability`

## Why this folder exists
This folder groups code and artifacts for `auditability` within the repository architecture.

## What is present
- `__init__.py` (file): Public exports for auditability runtime and contracts.
- `contracts.py` (file): Contract constants and fail-closed validators.
- `runtime.py` (file): Deterministic auditability derivation.
- `surface.py` (file): Feature-surface metadata.
- `tests/` (folder): Focused runtime and contract tests.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
