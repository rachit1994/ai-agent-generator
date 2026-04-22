from __future__ import annotations

import math

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


def test_validate_scalability_strategy_rejects_missing_evidence_object() -> None:
    payload = build_scalability_strategy(
        run_id="run-scalability-missing-evidence",
        mode="guarded_pipeline",
        parsed={"checks": [{"name": "a", "passed": True}]},
        events=[{"stage": "finalize", "retry_count": 0, "score": {"passed": True}}],
        cto={"balanced_gates": {"validation_ready": True}, "hard_stops": [{"id": "HS01", "passed": True}]},
    )
    payload["evidence"] = None
    errs = validate_scalability_strategy_dict(payload)
    assert "scalability_strategy_evidence" in errs


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("summary_ref", "summary.txt"),
        ("review_ref", "review.txt"),
        ("scalability_ref", "strategy/other.json"),
        ("summary_ref", "../summary.json"),
        ("review_ref", "/tmp/review.json"),
    ],
)
def test_validate_scalability_strategy_rejects_noncanonical_evidence_refs(key: str, value: str) -> None:
    payload = build_scalability_strategy(
        run_id="run-scalability-bad-evidence",
        mode="guarded_pipeline",
        parsed={"checks": [{"name": "a", "passed": True}]},
        events=[{"stage": "finalize", "retry_count": 0, "score": {"passed": True}}],
        cto={"balanced_gates": {"validation_ready": True}, "hard_stops": [{"id": "HS01", "passed": True}]},
    )
    payload["evidence"][key] = value
    errs = validate_scalability_strategy_dict(payload)
    assert f"scalability_strategy_evidence_ref:{key}" in errs


def test_validate_scalability_strategy_rejects_unknown_mode() -> None:
    payload = build_scalability_strategy(
        run_id="run-scalability-mode",
        mode="guarded_pipeline",
        parsed={"checks": [{"name": "a", "passed": True}]},
        events=[{"stage": "finalize", "retry_count": 0, "score": {"passed": True}}],
        cto={"balanced_gates": {"validation_ready": True}, "hard_stops": [{"id": "HS01", "passed": True}]},
    )
    payload["mode"] = "experimental"
    errs = validate_scalability_strategy_dict(payload)
    assert "scalability_strategy_mode" in errs


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_validate_scalability_strategy_rejects_non_finite_scores(value: float) -> None:
    payload = build_scalability_strategy(
        run_id="run-scalability-non-finite",
        mode="guarded_pipeline",
        parsed={"checks": [{"name": "a", "passed": True}]},
        events=[{"stage": "finalize", "retry_count": 0, "score": {"passed": True}}],
        cto={"balanced_gates": {"validation_ready": True}, "hard_stops": [{"id": "HS01", "passed": True}]},
    )
    payload["scores"]["overall_scaling_score"] = value
    errs = validate_scalability_strategy_dict(payload)
    assert "scalability_strategy_score_range:overall_scaling_score" in errs

