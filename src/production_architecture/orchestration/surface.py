"""Surface scaffold for `production_architecture/orchestration`."""

from __future__ import annotations

SUBHEADING = "production_architecture/orchestration"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "production_architecture.local_runtime.orchestrator.tests.unit.test_orchestration_benchmark_jsonl_contract",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_orchestration_run_end_contract",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_orchestration_run_error_contract",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_orchestration_run_start_contract",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_orchestration_stage_event_contract",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
