"""Surface scaffold for `workflow_pipelines/orchestration_stage_event`."""

from __future__ import annotations

SUBHEADING = "workflow_pipelines/orchestration_stage_event"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "production_architecture.local_runtime.orchestrator.tests.unit.test_orchestration_stage_event_contract",
    "workflow_pipelines.orchestration_stage_event.orchestration_stage_event_contract",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_event_lineage_replay_manifest",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_orchestration_benchmark_jsonl_contract",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_orchestration_run_end_contract",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
