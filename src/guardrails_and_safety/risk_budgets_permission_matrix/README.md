# Folder: `src/guardrails_and_safety/risk_budgets_permission_matrix`

## Why this folder exists
This folder groups code and artifacts for `risk_budgets_permission_matrix` within the repository architecture.

## What is present
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `contracts.py` (file): Defines machine-checkable interface and schema expectations.
- `gates_constants` (folder): Implements gate logic used to approve/reject progression.
- `gates_manifest` (folder): Implements gate logic used to approve/reject progression.
- `risk_budgets` (folder): Contains safety/risk enforcement checks and guardrails.
- `runtime.py` (file): Implements a concrete part of this folder responsibility.
- `surface.py` (file): Implements a concrete part of this folder responsibility.
- `tests/test_runtime.py` (file): Tests behavior and contracts for this folder.
- `time_and_budget` (folder): Groups related implementation for this subdomain boundary.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
