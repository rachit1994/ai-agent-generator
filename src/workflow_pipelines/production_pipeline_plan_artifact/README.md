# Folder: `src/workflow_pipelines/production_pipeline_plan_artifact`

## Why this folder exists
This folder groups code and artifacts for `production_pipeline_plan_artifact` within the repository architecture.

## What is present
- `production_pipeline_task_to_promote` (folder): Implements stage/pipeline behavior for task execution lifecycle.
- `contracts.py`: Contract/validation for `program/production_pipeline_plan_artifact.json`.
- `runtime.py`: Deterministic production-pipeline-plan-artifact derivation.
- `surface.py`: Implemented surface metadata.
- `tests/test_runtime.py`: Determinism and fail-closed validation tests.
- `__init__.py` (file): Package exports for this feature runtime.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
