"""Surface metadata for self-learning loop."""

from __future__ import annotations

SUBHEADING = "core_components/self_learning_loop"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "core_components.self_learning_loop.runtime",
    "core_components.self_learning_loop.contracts",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.self_learning_loop_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
