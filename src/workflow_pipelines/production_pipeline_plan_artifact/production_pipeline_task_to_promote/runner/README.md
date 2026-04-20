# Folder: `src/workflow_pipelines/production_pipeline_plan_artifact/production_pipeline_task_to_promote/runner`

## Why this folder exists
This folder groups code and artifacts for `runner` within the repository architecture.

## What is present
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `artifacts.py` (file): Implements a concrete part of this folder responsibility.
- `completion_layer.py` (file): Implements a concrete part of this folder responsibility.
- `cto_publish.py` (file): Implements a concrete part of this folder responsibility.
- `event_lineage_layer.py` (file): Handles event lineage, event contracts, or event persistence logic.
- `evolution_layer.py` (file): Implements a concrete part of this folder responsibility.
- `failure_summary.py` (file): Implements a concrete part of this folder responsibility.
- `memory_artifact_layer.py` (file): Implements memory handling and memory-related lifecycle logic.
- `orchestration_run_end_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `orchestration_run_error_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `orchestration_run_start_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `orchestration_stage_event_contract.py` (file): Defines machine-checkable interface and schema expectations.
- `organization_layer.py` (file): Implements a concrete part of this folder responsibility.
- `persist_traces.py` (file): Implements a concrete part of this folder responsibility.
- `single_task.py` (file): Implements a concrete part of this folder responsibility.
- `success_artifacts.py` (file): Implements a concrete part of this folder responsibility.
- `traces_jsonl_event_contract.py` (file): Defines machine-checkable interface and schema expectations.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
