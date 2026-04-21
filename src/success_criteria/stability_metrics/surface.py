"""Surface scaffold for `success_criteria/stability_metrics`."""

from __future__ import annotations

SUBHEADING = "success_criteria/stability_metrics"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "success_criteria.stability_metrics.runtime",
    "success_criteria.stability_metrics.contracts",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.evolution_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
