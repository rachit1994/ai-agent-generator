# Folder: `src/workflow_pipelines/production_pipeline_plan_artifact/production_pipeline_task_to_promote/benchmark`

## Why this folder exists
This folder groups code and artifacts for `benchmark` within the repository architecture.

## What is present
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `benchmark_aggregate_summary_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `benchmark_checkpoint_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `benchmark_manifest_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `failure_pipeline_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `offline_eval_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `online_eval_shadow_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `orchestration_benchmark_jsonl_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `production_pipeline_plan_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `promotion_eval_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `regression_surface_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `retry_pipeline_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `run_benchmark.py` (file): Implements benchmark/evaluation flows and related contracts.
- `run_manifest_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `strategy_overlay_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `suite.py` (file): Implements a concrete part of this folder responsibility.
- `summary_payload.py` (file): Implements a concrete part of this folder responsibility.
- `task_loop.py` (file): Implements a concrete part of this folder responsibility.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
