"""Surface scaffold for `event_sourced_architecture/auditability`."""

from __future__ import annotations

SUBHEADING = "event_sourced_architecture/auditability"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES: list[str] = [
    "event_sourced_architecture.auditability.runtime",
    "event_sourced_architecture.auditability.contracts",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.auditability_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
