"""Surface scaffold for `success_criteria/extended_binary_gates`."""

from __future__ import annotations

SUBHEADING = "success_criteria/extended_binary_gates"
IMPLEMENTATION_STATUS = "scaffold"

REFERENCE_MODULES = [
    "guardrails_and_safety.risk_budgets_permission_matrix.gates_constants.constants",
    "guardrails_and_safety.risk_budgets_permission_matrix.gates_manifest.manifest",
    "guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.balanced_gates",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_cto_gates",
    "production_architecture.local_runtime.orchestrator.tests.unit.test_static_gates",
]

def describe_surface() -> dict[str, object]:
    return {
        "subheading": SUBHEADING,
        "status": IMPLEMENTATION_STATUS,
        "references": REFERENCE_MODULES,
    }
