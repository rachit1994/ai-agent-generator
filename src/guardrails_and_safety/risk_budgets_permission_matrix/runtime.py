"""Deterministic risk-budgets permission-matrix runtime derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    RISK_BUDGETS_PERMISSION_MATRIX_CONTRACT,
    RISK_BUDGETS_PERMISSION_MATRIX_SCHEMA_VERSION,
)


def build_risk_budgets_permission_matrix(
    *,
    run_id: str,
    cto: dict[str, Any],
) -> dict[str, Any]:
    balanced_gates = cto.get("balanced_gates")
    balanced_gates_present = isinstance(balanced_gates, dict)
    validation_ready = bool(cto.get("validation_ready"))
    hard_stops = cto.get("hard_stops")
    hard_stops_list = hard_stops if isinstance(hard_stops, list) else []
    hard_stops_all_pass = all(
        bool(row.get("passed")) for row in hard_stops_list if isinstance(row, dict)
    )
    status = "ready" if balanced_gates_present and validation_ready and hard_stops_all_pass else "degraded"
    return {
        "schema": RISK_BUDGETS_PERMISSION_MATRIX_CONTRACT,
        "schema_version": RISK_BUDGETS_PERMISSION_MATRIX_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "checks": {
            "balanced_gates_present": balanced_gates_present,
            "validation_ready": validation_ready,
            "hard_stops_all_pass": hard_stops_all_pass,
        },
        "counts": {"hard_stop_count": len(hard_stops_list)},
        "evidence": {
            "summary_ref": "summary.json",
            "review_ref": "review.json",
            "runtime_ref": "safety/risk_budgets_permission_matrix_runtime.json",
        },
    }
