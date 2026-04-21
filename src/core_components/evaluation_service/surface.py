"""Surface scaffold for `core_components/evaluation_service`."""

from __future__ import annotations

SUBHEADING = "core_components/evaluation_service"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "core_components.evaluation_service.runtime",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evaluation_service_layer",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_core_evaluation_service_surface",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
