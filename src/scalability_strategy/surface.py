"""Surface metadata for scalability strategy."""

from __future__ import annotations

SUBHEADING = "scalability_strategy/scalability_strategy"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "scalability_strategy.runtime",
    "scalability_strategy.contracts",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.scalability_strategy_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }

