"""Surface for `evaluation_framework/offline_evaluation`."""

from __future__ import annotations

SUBHEADING = "evaluation_framework/offline_evaluation"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "evaluation_framework.offline_evaluation.runtime",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.run_benchmark",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_offline_evaluation_runtime_surface",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
