"""Surface metadata for production storage architecture."""

from __future__ import annotations

SUBHEADING = "production_architecture/storage"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "production_architecture.storage.runtime",
    "production_architecture.storage.contracts",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.storage_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }

