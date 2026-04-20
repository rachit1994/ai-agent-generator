"""Surface scaffold for `success_criteria/hard_release_gates`."""

from __future__ import annotations

SUBHEADING = "success_criteria/hard_release_gates"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "guardrails_and_safety.risk_budgets_permission_matrix.gates_constants.constants",
    "guardrails_and_safety.risk_budgets_permission_matrix.gates_manifest.manifest",
    "guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.balanced_gates",
    "guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.hard_stop_schedule",
    "guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.hard_stops",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
