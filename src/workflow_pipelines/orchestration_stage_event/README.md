# Folder: `src/workflow_pipelines/orchestration_stage_event`

## Why this folder exists
This folder groups code and artifacts for `orchestration_stage_event` within the repository architecture.

## What is present
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `orchestration_stage_event_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `surface.py` (file): Implements a concrete part of this folder responsibility.
- `contracts.py`: Contract/validation for `orchestration/stage_event_runtime.json`.
- `runtime.py`: Deterministic stage-event runtime derivation.
- `tests/test_runtime.py`: Determinism and fail-closed validation tests.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
