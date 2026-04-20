"""Surface scaffold for `evaluation_framework/regression_testing_surface`."""

from __future__ import annotations

SUBHEADING = "evaluation_framework/regression_testing_surface"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "production_architecture.local_runtime.orchestrator.tests.unit.test_regression_surface_contract",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.regression_surface_contract",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_public_export_surface",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
