"""Surface scaffold for `success_criteria/error_reduction_metrics`."""

from __future__ import annotations

SUBHEADING = "success_criteria/error_reduction_metrics"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.metrics_helpers",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_orchestration_run_error_contract",
    "workflow_pipelines.orchestration_run_error.orchestration_run_error_contract",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
