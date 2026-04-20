"""Surface scaffold for `event_sourced_architecture/event_store`."""

from __future__ import annotations

SUBHEADING = "event_sourced_architecture/event_store"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "production_architecture.local_runtime.orchestrator.tests.unit.test_event_lineage_replay_manifest",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_orchestration_stage_event_contract",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_traces_jsonl_event_contract",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.event_lineage_layer",
    "workflow_pipelines.orchestration_stage_event.orchestration_stage_event_contract",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
