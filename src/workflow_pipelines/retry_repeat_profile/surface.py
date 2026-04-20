"""Surface scaffold for `workflow_pipelines/retry_repeat_profile`."""

from __future__ import annotations

SUBHEADING = "workflow_pipelines/retry_repeat_profile"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "production_architecture.local_runtime.orchestrator.tests.unit.test_retry_pipeline_repeat_contract",
    "guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.run_profile",
    "workflow_pipelines.retry_repeat_profile.retry_pipeline_contract",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
