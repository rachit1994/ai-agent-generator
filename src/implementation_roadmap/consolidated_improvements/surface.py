"""Surface metadata for consolidated improvements."""

from __future__ import annotations

SUBHEADING = "implementation_roadmap/consolidated_improvements"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "implementation_roadmap.consolidated_improvements.runtime",
    "implementation_roadmap.consolidated_improvements.contracts",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.consolidated_improvements_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }

