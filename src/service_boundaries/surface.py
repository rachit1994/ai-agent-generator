"""Surface metadata for service boundaries."""

from __future__ import annotations

SUBHEADING = "service_boundaries/service_boundaries"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "service_boundaries.runtime",
    "service_boundaries.contracts",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.service_boundaries_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }

