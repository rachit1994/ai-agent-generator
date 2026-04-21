"""Surface scaffold for `evaluation_framework/promotion_evaluation`."""

from __future__ import annotations

SUBHEADING = "evaluation_framework/promotion_evaluation"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "evaluation_framework.promotion_evaluation.contracts",
    "evaluation_framework.promotion_evaluation.runtime",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.promotion_evaluation_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
