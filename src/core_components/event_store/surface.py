"""Surface metadata for `core_components/event_store`."""

from __future__ import annotations

SUBHEADING = "core_components/event_store"
IMPLEMENTATION_STATUS = "scaffold"

IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "core_components.event_store.contracts",
    "core_components.event_store.runtime",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.event_store_component_layer",
    "guardrails_and_safety.review_gating_evaluator_authority.review_gating.run_directory",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
