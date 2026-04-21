"""Surface descriptor for core-components orchestrator feature."""

from __future__ import annotations

SUBHEADING = "core_components/orchestrator"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "core_components.orchestrator.runtime",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.orchestrator_component_layer",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_core_orchestrator_surface",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
