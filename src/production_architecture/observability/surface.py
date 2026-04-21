"""Surface metadata for production observability."""

from __future__ import annotations

SUBHEADING = "production_architecture/observability"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "production_architecture.observability.contracts",
    "production_architecture.observability.runtime",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.observability_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
