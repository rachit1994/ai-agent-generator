"""Surface metadata for implementation roadmap."""

from __future__ import annotations

SUBHEADING = "implementation_roadmap/implementation_roadmap"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "implementation_roadmap.implementation_roadmap.contracts",
    "implementation_roadmap.implementation_roadmap.runtime",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.implementation_roadmap_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
