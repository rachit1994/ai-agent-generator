# Folder: `src/production_architecture/local_runtime/orchestrator/api`

## Why this folder exists
This folder groups code and artifacts for `api` within the repository architecture.

## What is present
- `status` (folder): Groups related implementation for this subdomain boundary.
- `__init__.py` (file): Implements a concrete part of this folder responsibility.
- `context_pack.py` (file): Implements a concrete part of this folder responsibility.
- `continuous_run.py` (file): Implements a concrete part of this folder responsibility.
- `gemma_roadmap_review.py` (file): Implements review and gating logic for quality/safety decisions.
- `project_aggregate.py` (file): Implements gate logic used to approve/reject progression.
- `project_driver.py` (file): Implements a concrete part of this folder responsibility.
- `project_events.py` (file): Handles event lineage, event contracts, or event persistence logic.
- `project_intake_revise.py` (file): Implements a concrete part of this folder responsibility.
- `project_intake_scaffold.py` (file): Implements a concrete part of this folder responsibility.
- `project_intake_util.py` (file): Implements a concrete part of this folder responsibility.
- `project_lease.py` (file): Implements a concrete part of this folder responsibility.
- `project_parallel.py` (file): Implements a concrete part of this folder responsibility.
- `project_plan.py` (file): Implements a concrete part of this folder responsibility.
- `project_plan_lock.py` (file): Implements a concrete part of this folder responsibility.
- `project_remaining_work.py` (file): Implements a concrete part of this folder responsibility.
- `project_scheduler.py` (file): Implements a concrete part of this folder responsibility.
- `project_schema.py` (file): Captures structural rules used for validation and compatibility.
- `project_stage1_observability_export.py` (file): Implements a concrete part of this folder responsibility.
- `project_status.py` (file): Implements a concrete part of this folder responsibility.
- `project_stop.py` (file): Implements a concrete part of this folder responsibility.
- `project_validate.py` (file): Implements a concrete part of this folder responsibility.
- `project_verify.py` (file): Implements a concrete part of this folder responsibility.
- `project_workspace.py` (file): Implements a concrete part of this folder responsibility.
- `project_worktree.py` (file): Implements a concrete part of this folder responsibility.
- `README.md` (file): Documents folder behavior and usage context.
- `repo_index.py` (file): Implements a concrete part of this folder responsibility.
- `self_evolve.py` (file): Implements a concrete part of this folder responsibility.
- `validate_run.py` (file): Implements a concrete part of this folder responsibility.

## Notes
- Keep this inventory updated when adding/removing files.
- Prefer placing tests close to the most specific leaf module.
