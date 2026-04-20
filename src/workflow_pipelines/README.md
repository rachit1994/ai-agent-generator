# Folder: `src/workflow_pipelines`

## Why this folder exists
This folder groups code and artifacts for `workflow_pipelines` within the repository architecture.

## What is present
- `benchmark_aggregate_manifest` (folder): Implements benchmark/evaluation flows and related contracts.
- `benchmark_aggregate_summary` (folder): Implements benchmark/evaluation flows and related contracts.
- `benchmark_checkpoint` (folder): Implements benchmark/evaluation flows and related contracts.
- `benchmark_orchestration_jsonl` (folder): Implements benchmark/evaluation flows and related contracts.
- `failure_path_artifacts` (folder): Groups related implementation for this subdomain boundary.
- `orchestration_run_end` (folder): Defines orchestration event or state contracts for run flow.
- `orchestration_run_error` (folder): Defines orchestration event or state contracts for run flow.
- `orchestration_run_start` (folder): Defines orchestration event or state contracts for run flow.
- `orchestration_stage_event` (folder): Handles event lineage, event contracts, or event persistence logic.
- `production_pipeline_plan_artifact` (folder): Implements stage/pipeline behavior for task execution lifecycle.
- `retry_repeat_profile` (folder): Groups related implementation for this subdomain boundary.
- `run_manifest` (folder): Groups related implementation for this subdomain boundary.
- `strategy_overlay` (folder): Groups related implementation for this subdomain boundary.
- `traces_jsonl` (folder): Groups related implementation for this subdomain boundary.
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `README.md` (file): Documents folder behavior and usage context.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
