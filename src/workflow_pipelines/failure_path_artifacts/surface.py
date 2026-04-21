"""Surface scaffold for `workflow_pipelines/failure_path_artifacts`."""

from __future__ import annotations

SUBHEADING = "workflow_pipelines/failure_path_artifacts"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "production_architecture.local_runtime.orchestrator.tests.unit.test_failure_pipeline_contract",
    "workflow_pipelines.failure_path_artifacts.runtime",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_runner_artifacts",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.failure_path_artifacts_layer",
    "workflow_pipelines.failure_path_artifacts.failure_pipeline_contract",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.artifacts",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.failure_summary",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
