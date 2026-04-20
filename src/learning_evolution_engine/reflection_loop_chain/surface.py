"""Surface scaffold for `learning_evolution_engine/reflection_loop_chain`."""

from __future__ import annotations

SUBHEADING = "learning_evolution_engine/reflection_loop_chain"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.benchmark.task_loop",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
