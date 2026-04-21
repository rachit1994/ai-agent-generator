"""Surface scaffold for `evaluation_framework/regression_testing_surface`."""

from __future__ import annotations

SUBHEADING = "evaluation_framework/regression_testing_surface"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "evaluation_framework.regression_testing_surface.runtime",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.regression_testing_surface_layer",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.regression_surface_contract",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
