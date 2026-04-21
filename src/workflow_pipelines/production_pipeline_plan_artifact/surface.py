"""Surface metadata for production pipeline plan artifact."""

from __future__ import annotations

SUBHEADING = "workflow_pipelines/production_pipeline_plan_artifact"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "workflow_pipelines.production_pipeline_plan_artifact.contracts",
    "workflow_pipelines.production_pipeline_plan_artifact.runtime",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.production_pipeline_plan_artifact_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
