# Folder: `src/core_components/identity_and_authorization_plane`

## Why this folder exists
This folder groups code and artifacts for `identity_and_authorization_plane` within the repository architecture.

## What is present
- `__init__.py` (file): Public exports for identity/authz runtime and contracts.
- `contracts.py` (file): Contract constants and fail-closed validators.
- `runtime.py` (file): Deterministic identity/authz derivation.
- `surface.py` (file): Feature-surface metadata.
- `tests/` (folder): Focused runtime and contract tests.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
