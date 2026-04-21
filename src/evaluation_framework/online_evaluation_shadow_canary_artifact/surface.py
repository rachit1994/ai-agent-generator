"""Surface metadata for online evaluation shadow/canary artifact."""

from __future__ import annotations

SUBHEADING = "evaluation_framework/online_evaluation_shadow_canary_artifact"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "evaluation_framework.online_evaluation_shadow_canary_artifact.runtime",
    "evaluation_framework.online_evaluation_shadow_canary_artifact.contracts",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.online_evaluation_shadow_canary_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
