from __future__ import annotations

from evaluation_framework.regression_testing_surface import (
    build_regression_testing_surface,
    validate_regression_testing_surface_dict,
)


def test_build_regression_testing_surface_is_deterministic() -> None:
    summary = {"metrics": {"passRate": 1.0}}
    promotion_eval = {"decision": "promote"}
    online_eval = {"decision": {"decision": "promote"}}
    one = build_regression_testing_surface(
        run_id="rid-regression-surface",
        anchor_errors=[],
        promotion_evaluation=promotion_eval,
        online_evaluation=online_eval,
        summary=summary,
    )
    two = build_regression_testing_surface(
        run_id="rid-regression-surface",
        anchor_errors=[],
        promotion_evaluation=promotion_eval,
        online_evaluation=online_eval,
        summary=summary,
    )
    assert one == two
    assert one["status"] == "ready"
    assert validate_regression_testing_surface_dict(one) == []


def test_validate_regression_testing_surface_fail_closed() -> None:
    errs = validate_regression_testing_surface_dict({"schema": "bad"})
    assert "regression_testing_surface_schema" in errs
    assert "regression_testing_surface_schema_version" in errs


def test_build_regression_testing_surface_treats_missing_status_payloads_as_degraded() -> None:
    payload = build_regression_testing_surface(
        run_id="rid-regression-surface",
        anchor_errors=[],
        promotion_evaluation={"result": "promote"},
        online_evaluation={"result": "promote"},
        summary={"metrics": {"passRate": 1.0}},
    )
    assert payload["status"] == "degraded"
    assert payload["metrics"]["has_promotion_eval"] is False
    assert payload["metrics"]["has_online_eval"] is False


def test_build_regression_testing_surface_uses_contract_shaped_decisions() -> None:
    payload = build_regression_testing_surface(
        run_id="rid-regression-surface",
        anchor_errors=[],
        promotion_evaluation={"decision": "hold"},
        online_evaluation={"decision": {"decision": "promote"}},
        summary={"metrics": {"passRate": 1.0}},
    )
    assert payload["status"] == "ready"
    assert payload["metrics"]["has_promotion_eval"] is True
    assert payload["metrics"]["has_online_eval"] is True


def test_validate_regression_testing_surface_rejects_status_metrics_mismatch() -> None:
    payload = build_regression_testing_surface(
        run_id="rid-regression-surface",
        anchor_errors=[],
        promotion_evaluation={"decision": "promote"},
        online_evaluation={"decision": {"decision": "promote"}},
        summary={"metrics": {"passRate": 1.0}},
    )
    payload["status"] = "degraded"
    errs = validate_regression_testing_surface_dict(payload)
    assert "regression_testing_surface_status_metrics_mismatch" in errs
