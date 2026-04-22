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


def test_build_risk_budgets_permission_matrix_treats_truthy_non_boolean_as_failed() -> None:
    payload = build_risk_budgets_permission_matrix(
        run_id="rid-risk",
        cto={
            "validation_ready": "true",
            "balanced_gates": {"all_ok": True},
            "hard_stops": [{"id": "HS-01", "passed": "true"}],
        },
    )
    assert payload["status"] == "degraded"
    assert payload["checks"]["validation_ready"] is False
    assert payload["checks"]["hard_stops_all_pass"] is False


def test_validate_risk_budgets_permission_matrix_rejects_status_checks_mismatch() -> None:
    payload = build_risk_budgets_permission_matrix(
        run_id="rid-risk",
        cto={
            "validation_ready": True,
            "balanced_gates": {"all_ok": True},
            "hard_stops": [{"id": "HS-01", "passed": True}],
        },
    )
    payload["status"] = "degraded"
    errs = validate_risk_budgets_permission_matrix_dict(payload)
    assert "risk_budgets_permission_matrix_status_checks_mismatch" in errs


def test_build_risk_budgets_permission_matrix_requires_non_empty_hard_stops() -> None:
    payload = build_risk_budgets_permission_matrix(
        run_id="rid-risk-empty-hard-stops",
        cto={
            "validation_ready": True,
            "balanced_gates": {"all_ok": True},
            "hard_stops": [],
        },
    )
    assert payload["status"] == "degraded"
    assert payload["checks"]["hard_stops_all_pass"] is False
    assert payload["counts"]["hard_stop_count"] == 0


def test_validate_risk_budgets_permission_matrix_rejects_count_check_mismatch() -> None:
    payload = build_risk_budgets_permission_matrix(
        run_id="rid-risk-count-mismatch",
        cto={
            "validation_ready": True,
            "balanced_gates": {"all_ok": True},
            "hard_stops": [{"id": "HS-01", "passed": True}],
        },
    )
    payload["counts"]["hard_stop_count"] = 0
    payload["checks"]["hard_stops_all_pass"] = True
    errs = validate_risk_budgets_permission_matrix_dict(payload)
    assert "risk_budgets_permission_matrix_counts_checks_mismatch" in errs


def test_build_risk_budgets_permission_matrix_fail_closed_for_non_dict_hard_stop_rows() -> None:
    payload = build_risk_budgets_permission_matrix(
        run_id="rid-risk-malformed-hard-stops",
        cto={
            "validation_ready": True,
            "balanced_gates": {"all_ok": True},
            "hard_stops": [True],
        },
    )
    assert payload["status"] == "degraded"
    assert payload["checks"]["hard_stops_all_pass"] is False
