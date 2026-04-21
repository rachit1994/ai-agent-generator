from __future__ import annotations

from core_components.evaluation_service import (
    build_evaluation_service,
    validate_evaluation_service_dict,
)


def test_build_evaluation_service_is_deterministic() -> None:
    summary = {"metrics": {"passRate": 1.0}}
    online_eval = {"status": "ok"}
    promotion_eval = {"status": "promote"}
    one = build_evaluation_service(
        run_id="rid-eval",
        summary=summary,
        online_eval=online_eval,
        promotion_eval=promotion_eval,
    )
    two = build_evaluation_service(
        run_id="rid-eval",
        summary=summary,
        online_eval=online_eval,
        promotion_eval=promotion_eval,
    )
    assert one == two
    assert one["status"] == "ready"
    assert validate_evaluation_service_dict(one) == []


def test_validate_evaluation_service_fail_closed() -> None:
    errs = validate_evaluation_service_dict({"schema": "bad"})
    assert "evaluation_service_schema" in errs
    assert "evaluation_service_schema_version" in errs
