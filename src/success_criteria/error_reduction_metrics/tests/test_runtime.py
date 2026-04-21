from __future__ import annotations

from success_criteria.error_reduction_metrics import (
    build_error_reduction_metrics,
    validate_error_reduction_metrics_dict,
)


def test_build_error_reduction_metrics_is_deterministic() -> None:
    parsed = {"checks": [{"name": "a", "passed": False}, {"name": "b", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    one = build_error_reduction_metrics(run_id="rid-erm", parsed=parsed, events=events, skill_nodes=None)
    two = build_error_reduction_metrics(run_id="rid-erm", parsed=parsed, events=events, skill_nodes=None)
    assert one == two
    assert validate_error_reduction_metrics_dict(one) == []


def test_validate_error_reduction_metrics_fail_closed() -> None:
    errs = validate_error_reduction_metrics_dict({"schema": "bad"})
    assert "error_reduction_metrics_schema" in errs
    assert "error_reduction_metrics_schema_version" in errs

