"""Surface metadata for production readiness program."""

from __future__ import annotations

SUBHEADING = "implementation_roadmap/production_readiness_program"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "implementation_roadmap.production_readiness_program.runtime",
    "implementation_roadmap.production_readiness_program.contracts",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.production_readiness_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }

