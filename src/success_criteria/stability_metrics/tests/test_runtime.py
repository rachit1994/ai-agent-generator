from __future__ import annotations

from success_criteria.stability_metrics import (
    build_stability_metrics,
    validate_stability_metrics_dict,
)


def test_build_stability_metrics_is_deterministic() -> None:
    events = [
        {"stage": "finalize", "score": {"passed": True, "reliability": 0.9}},
        {"stage": "finalize", "score": {"passed": False, "reliability": 0.6}},
        {"stage": "repair"},
    ]
    one = build_stability_metrics(run_id="rid-stability", events=events)
    two = build_stability_metrics(run_id="rid-stability", events=events)
    assert one == two
    assert validate_stability_metrics_dict(one) == []


def test_validate_stability_metrics_fail_closed() -> None:
    errs = validate_stability_metrics_dict({"schema": "bad"})
    assert "stability_metrics_schema" in errs
    assert "stability_metrics_schema_version" in errs
