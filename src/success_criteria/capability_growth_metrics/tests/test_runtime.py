from __future__ import annotations

import math

import pytest

from success_criteria.capability_growth_metrics import (
    build_capability_growth_metrics,
    validate_capability_growth_metrics_dict,
)


def test_build_capability_growth_metrics_is_deterministic() -> None:
    parsed = {"checks": [{"name": "a", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}]
    skill_nodes = {"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": 0.75}]}
    one = build_capability_growth_metrics(
        run_id="rid-cg", parsed=parsed, events=events, skill_nodes=skill_nodes
    )
    two = build_capability_growth_metrics(
        run_id="rid-cg", parsed=parsed, events=events, skill_nodes=skill_nodes
    )
    assert one == two
    assert validate_capability_growth_metrics_dict(one) == []


def test_validate_capability_growth_metrics_fail_closed() -> None:
    errs = validate_capability_growth_metrics_dict({"schema": "wrong"})
    assert "capability_growth_metrics_schema" in errs
    assert "capability_growth_metrics_schema_version" in errs


def test_build_capability_growth_metrics_clamps_non_finite_inputs() -> None:
    payload = build_capability_growth_metrics(
        run_id="rid-cg",
        parsed={},
        events=[{"stage": "finalize", "score": {"passed": True, "reliability": math.nan}}],
        skill_nodes={"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": math.inf}]},
    )
    assert payload["metrics"]["capability_growth_rate"] == pytest.approx(0.5)
    assert payload["metrics"]["capability_stability_rate"] == pytest.approx(0.0)
    assert payload["metrics"]["growth_confidence"] == pytest.approx(0.15)
    assert validate_capability_growth_metrics_dict(payload) == []


def test_validate_capability_growth_metrics_rejects_non_finite_metric_values() -> None:
    errs = validate_capability_growth_metrics_dict(
        {
            "schema": "sde.capability_growth_metrics.v1",
            "schema_version": "1.0",
            "run_id": "rid-cg",
            "metrics": {
                "capability_growth_rate": math.nan,
                "capability_stability_rate": 0.2,
                "promotion_readiness_delta": 0.0,
                "growth_confidence": math.inf,
            },
        }
    )
    assert "capability_growth_metrics_metric_non_finite:capability_growth_rate" in errs
    assert "capability_growth_metrics_metric_non_finite:growth_confidence" in errs
