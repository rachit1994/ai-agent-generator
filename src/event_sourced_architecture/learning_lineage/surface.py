"""Surface scaffold for `event_sourced_architecture/learning_lineage`."""

from __future__ import annotations

SUBHEADING = "event_sourced_architecture/learning_lineage"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "production_architecture.local_runtime.orchestrator.tests.unit.test_event_lineage_replay_manifest",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.event_lineage_layer",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
