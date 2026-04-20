"""Surface scaffold for `workflow_pipelines/orchestration_run_error`."""

from __future__ import annotations

SUBHEADING = "workflow_pipelines/orchestration_run_error"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "production_architecture.local_runtime.orchestrator.tests.unit.test_orchestration_run_error_contract",
    "workflow_pipelines.orchestration_run_error.orchestration_run_error_contract",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_orchestration_run_end_contract",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_orchestration_run_start_contract",
    "workflow_pipelines.orchestration_run_end.orchestration_run_end_contract",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
