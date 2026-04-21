# Folder: `src/production_architecture/identity_and_authorization`

## Why this folder exists
This folder groups code and artifacts for `identity_and_authorization` within the repository architecture.

## What is present
- `contracts.py`: Strict contract for `iam/production_identity_authorization.json`.
- `runtime.py`: Deterministic runtime derivation for production identity/authz status.
- `surface.py`: Surface metadata consumed by orchestrator-level tests.
- `tests/test_runtime.py`: Determinism and fail-closed validation tests.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
