from __future__ import annotations

from guardrails_and_safety.risk_budgets_permission_matrix import (
    build_risk_budgets_permission_matrix,
    validate_risk_budgets_permission_matrix_dict,
)


def test_build_risk_budgets_permission_matrix_deterministic() -> None:
    cto = {
        "validation_ready": True,
        "balanced_gates": {"all_ok": True},
        "hard_stops": [{"id": "HS-01", "passed": True}],
    }
    one = build_risk_budgets_permission_matrix(run_id="rid-risk", cto=cto)
    two = build_risk_budgets_permission_matrix(run_id="rid-risk", cto=cto)
    assert one == two
    assert one["status"] == "ready"
    assert validate_risk_budgets_permission_matrix_dict(one) == []


def test_validate_risk_budgets_permission_matrix_fail_closed() -> None:
    errs = validate_risk_budgets_permission_matrix_dict({"schema": "bad"})
    assert "risk_budgets_permission_matrix_schema" in errs
    assert "risk_budgets_permission_matrix_schema_version" in errs
