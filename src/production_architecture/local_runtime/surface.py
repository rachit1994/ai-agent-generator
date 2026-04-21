"""Surface for `production_architecture/local_runtime`."""

from __future__ import annotations

SUBHEADING = "production_architecture/local_runtime"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "production_architecture.local_runtime.runtime",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.local_runtime_spine_layer",
    "production_architecture.local_runtime.tests.test_local_runtime_spine",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
