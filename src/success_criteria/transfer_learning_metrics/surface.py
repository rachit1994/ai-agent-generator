"""Surface scaffold for `success_criteria/transfer_learning_metrics`."""

from __future__ import annotations

SUBHEADING = "success_criteria/transfer_learning_metrics"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.metrics_helpers",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
