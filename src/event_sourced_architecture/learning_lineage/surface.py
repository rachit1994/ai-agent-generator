"""Surface scaffold for `event_sourced_architecture/learning_lineage`."""

from __future__ import annotations

SUBHEADING = "event_sourced_architecture/learning_lineage"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "event_sourced_architecture.learning_lineage.runtime",
    "event_sourced_architecture.learning_lineage.contracts",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.learning_lineage_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
