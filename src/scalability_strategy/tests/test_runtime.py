from __future__ import annotations

import pytest

from scalability_strategy import build_scalability_strategy, validate_scalability_strategy_dict


def test_build_scalability_strategy_is_deterministic() -> None:
    parsed = {"checks": [{"name": "a", "passed": True}, {"name": "b", "passed": True}]}
    events = [{"stage": "finalize", "retry_count": 0, "score": {"passed": True}}]
    cto = {"balanced_gates": {"validation_ready": True}, "hard_stops": [{"id": "HS01", "passed": True}]}
    one = build_scalability_strategy(
        run_id="run-scalability",
        mode="guarded_pipeline",
        parsed=parsed,
        events=events,
        cto=cto,
    )
    two = build_scalability_strategy(
        run_id="run-scalability",
        mode="guarded_pipeline",
        parsed=parsed,
        events=events,
        cto=cto,
    )
    assert one == two
    assert validate_scalability_strategy_dict(one) == []


def test_validate_scalability_strategy_fail_closed() -> None:
    errs = validate_scalability_strategy_dict({"schema": "bad"})
    assert "scalability_strategy_schema" in errs
    assert "scalability_strategy_schema_version" in errs


def test_build_scalability_strategy_treats_truthy_non_bools_as_fail_closed() -> None:
    payload = build_scalability_strategy(
        run_id="run-scalability-truthy",
        mode="guarded_pipeline",
        parsed={"checks": [{"name": "a", "passed": "true"}]},
        events=[{"stage": "finalize", "retry_count": 0, "score": {"passed": 1}}],
        cto={
            "balanced_gates": {"validation_ready": "true"},
            "hard_stops": [{"id": "HS01", "passed": "yes"}],
        },
    )
    scores = payload["scores"]
    assert scores["event_scaling_score"] == pytest.approx(0.0)
    assert scores["memory_scaling_score"] == pytest.approx(0.0)
    assert payload["status"] == "constrained"


def test_validate_scalability_strategy_rejects_status_score_mismatch() -> None:
    payload = build_scalability_strategy(
        run_id="run-scalability-mismatch",
        mode="guarded_pipeline",
        parsed={"checks": [{"name": "a", "passed": False}]},
        events=[{"stage": "finalize", "retry_count": 2, "score": {"passed": False}}],
        cto={
            "balanced_gates": {"validation_ready": False},
            "hard_stops": [{"id": "HS01", "passed": True}],
        },
    )
    payload["status"] = "scalable"
    errs = validate_scalability_strategy_dict(payload)
    assert "scalability_strategy_status_score_mismatch" in errs


def test_validate_scalability_strategy_rejects_constrained_status_when_score_is_high() -> None:
    payload = build_scalability_strategy(
        run_id="run-scalability-status-mismatch-high",
        mode="guarded_pipeline",
        parsed={"checks": [{"name": "a", "passed": True}]},
        events=[{"stage": "finalize", "retry_count": 0, "score": {"passed": True}}],
        cto={
            "balanced_gates": {"validation_ready": True},
            "hard_stops": [{"id": "HS01", "passed": True}],
        },
    )
    payload["status"] = "constrained"
    errs = validate_scalability_strategy_dict(payload)
    assert "scalability_strategy_status_score_mismatch" in errs


def test_validate_scalability_strategy_rejects_overall_score_weight_mismatch() -> None:
    payload = build_scalability_strategy(
        run_id="run-scalability-weight-mismatch",
        mode="guarded_pipeline",
        parsed={"checks": [{"name": "a", "passed": True}]},
        events=[{"stage": "finalize", "retry_count": 0, "score": {"passed": True}}],
        cto={
            "balanced_gates": {"validation_ready": True},
            "hard_stops": [{"id": "HS01", "passed": True}],
        },
    )
    payload["scores"]["overall_scaling_score"] = 0.0
    errs = validate_scalability_strategy_dict(payload)
    assert "scalability_strategy_overall_score_mismatch" in errs

