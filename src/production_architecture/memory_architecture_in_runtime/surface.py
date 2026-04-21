"""Surface metadata for runtime memory architecture."""

from __future__ import annotations

SUBHEADING = "production_architecture/memory_architecture_in_runtime"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "production_architecture.memory_architecture_in_runtime.runtime",
    "production_architecture.memory_architecture_in_runtime.contracts",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.memory_architecture_runtime_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
