# Folder: `src/guardrails_and_safety/dual_control`

## Why this folder exists
This folder contains deterministic dual-control runtime evidence for guarded/phased runs.

## What is present
- `contracts.py`: Contract + validators for `program/dual_control_runtime.json`.
- `runtime.py`: Deterministic derivation from `doc_review` and `dual_control_ack`.
- `surface.py`: Orchestrator surface descriptor for this feature.
- `tests/test_runtime.py`: Determinism and fail-closed validation tests.

## Notes
- Keep imports at top-level and avoid inline imports.
# Folder: `src/guardrails_and_safety/dual_control`

## Why this folder exists
This folder groups code and artifacts for `dual_control` within the repository architecture.

## What is present
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `surface.py` (file): Implements a concrete part of this folder responsibility.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
