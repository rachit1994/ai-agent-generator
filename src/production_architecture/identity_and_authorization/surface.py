"""Surface metadata for production identity-and-authorization."""

from __future__ import annotations

SUBHEADING = "production_architecture/identity_and_authorization"
IMPLEMENTATION_STATUS = "implemented"
REFERENCE_MODULES = [
    "production_architecture.identity_and_authorization.runtime",
    "production_architecture.identity_and_authorization.contracts",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.production_identity_authorization_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
