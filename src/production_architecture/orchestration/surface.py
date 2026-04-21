"""Surface metadata for production orchestration."""

from __future__ import annotations

SUBHEADING = "production_architecture/orchestration"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "production_architecture.orchestration.contracts",
    "production_architecture.orchestration.runtime",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.production_orchestration_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
