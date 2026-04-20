"""Surface scaffold for `core_components/career_strategy_layer`."""

from __future__ import annotations

SUBHEADING = "core_components/career_strategy_layer"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "production_architecture.local_runtime.orchestrator.tests.unit.test_guarded_completion_layer",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_strategy_overlay_contract",
    "workflow_pipelines.strategy_overlay.strategy_overlay_contract",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.completion_layer",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.event_lineage_layer",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
