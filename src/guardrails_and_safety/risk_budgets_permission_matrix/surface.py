"""Surface for `guardrails_and_safety/risk_budgets_permission_matrix`."""

from __future__ import annotations

SUBHEADING = "guardrails_and_safety/risk_budgets_permission_matrix"
IMPLEMENTATION_STATUS = "implemented"

REFERENCE_MODULES = [
    "guardrails_and_safety.risk_budgets_permission_matrix.runtime",
    "workflow_pipelines.production_pipeline_plan_artifact.production_pipeline_task_to_promote.runner.risk_budgets_permission_matrix_layer",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_risk_budgets_permission_matrix_surface",
]


def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
