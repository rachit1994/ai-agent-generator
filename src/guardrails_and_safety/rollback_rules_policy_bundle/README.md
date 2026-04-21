# Folder: `src/guardrails_and_safety/rollback_rules_policy_bundle`

## Why this folder exists
This folder groups code and artifacts for `rollback_rules_policy_bundle` within the repository architecture.

## What is present
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `policy_bundle_rollback.py` (file): Implements a concrete part of this folder responsibility.
- `surface.py` (file): Implements a concrete part of this folder responsibility.
- `contracts.py`: Contract/validation for `program/rollback_rules_policy_bundle.json`.
- `runtime.py`: Deterministic rollback-rules policy-bundle evidence derivation.
- `tests/test_runtime.py`: Determinism and fail-closed validation tests.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
