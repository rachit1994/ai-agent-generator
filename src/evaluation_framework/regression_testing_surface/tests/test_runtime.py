from __future__ import annotations

from evaluation_framework.regression_testing_surface import (
    build_regression_testing_surface,
    validate_regression_testing_surface_dict,
)


def test_build_regression_testing_surface_is_deterministic() -> None:
    summary = {"metrics": {"passRate": 1.0}}
    promotion_eval = {"decision": "promote"}
    online_eval = {"decision": "promote"}
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
