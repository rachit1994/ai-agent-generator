"""Surface metadata for full build order progression."""

from __future__ import annotations

SUBHEADING = "scalability_strategy/full_build_order_progression"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "scalability_strategy.full_build_order_progression.runtime",
    "scalability_strategy.full_build_order_progression.contracts",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.full_build_order_progression_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }

