"""Surface scaffold for `workflow_pipelines/orchestration_run_start`."""

from __future__ import annotations

SUBHEADING = "workflow_pipelines/orchestration_run_start"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "workflow_pipelines.orchestration_run_start.runtime",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.orchestration_run_start_layer",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_orchestration_run_start_runtime_surface",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
