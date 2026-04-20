"""Surface scaffold for `evaluation_framework/promotion_evaluation`."""

from __future__ import annotations

SUBHEADING = "evaluation_framework/promotion_evaluation"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "evaluation_framework.offline_evaluation.sde_eval.eval",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_promotion_eval_package_contract",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.promotion_eval_contract",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
