"""Surface scaffold for `scalability_strategy/replay_scaling`."""

from __future__ import annotations

SUBHEADING = "scalability_strategy/replay_scaling"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "production_architecture.local_runtime.orchestrator.tests.unit.test_event_lineage_replay_manifest",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_replay",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.replay",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
