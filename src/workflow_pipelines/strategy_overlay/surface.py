"""Surface metadata for strategy overlay."""

from __future__ import annotations

SUBHEADING = "workflow_pipelines/strategy_overlay"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "workflow_pipelines.strategy_overlay.runtime",
    "workflow_pipelines.strategy_overlay.contracts",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.strategy_overlay_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
