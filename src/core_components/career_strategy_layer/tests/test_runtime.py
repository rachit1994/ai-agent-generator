from __future__ import annotations

import math

from core_components.career_strategy_layer import (
    build_career_strategy_layer,
    execute_career_strategy_runtime,
    validate_career_strategy_layer_dict,
)


def test_build_career_strategy_layer_is_deterministic() -> None:
    summary = {"quality": {"validation_ready": True}}
    review = {"status": "completed_review_pass"}
    promotion = {"proposed_stage": "senior"}
    capability = {"metrics": {"capability_growth_rate": 0.8}}
    transfer = {"metrics": {"transfer_efficiency_score": 0.75}}
    error = {"metrics": {"error_reduction_rate": 0.7}}
    scale = {"scores": {"overall_scaling_score": 0.7}}
    one = build_career_strategy_layer(
        run_id="rid-career",
        mode="guarded_pipeline",
        summary=summary,
        review=review,
        promotion_package=promotion,
        capability_growth=capability,
        transfer_learning=transfer,
        error_reduction=error,
        scalability_strategy=scale,
    )
    two = build_career_strategy_layer(
        run_id="rid-career",
        mode="guarded_pipeline",
        summary=summary,
        review=review,
        promotion_package=promotion,
        capability_growth=capability,
        transfer_learning=transfer,
        error_reduction=error,
        scalability_strategy=scale,
    )
    assert one == two
    assert validate_career_strategy_layer_dict(one) == []
    assert one["execution"]["signals_processed"] == 7


def test_validate_career_strategy_layer_fail_closed() -> None:
    errs = validate_career_strategy_layer_dict({"schema": "bad"})
    assert "career_strategy_layer_schema" in errs
    assert "career_strategy_layer_schema_version" in errs


def test_validate_career_strategy_layer_requires_strategy_fields() -> None:
    payload = build_career_strategy_layer(
        run_id="rid-career",
        mode="guarded_pipeline",
        summary={"quality": {"validation_ready": True}},
        review={"status": "completed_review_pass"},
        promotion_package={"proposed_stage": "senior"},
        capability_growth={"metrics": {"capability_growth_rate": 0.8}},
        transfer_learning={"metrics": {"transfer_efficiency_score": 0.75}},
        error_reduction={"metrics": {"error_reduction_rate": 0.7}},
        scalability_strategy={"scores": {"overall_scaling_score": 0.7}},
    )
    payload["strategy"].pop("priority")
    payload["strategy"]["recommended_actions"] = [""]
    errs = validate_career_strategy_layer_dict(payload)
    assert "career_strategy_layer_priority" in errs
    assert "career_strategy_layer_recommended_actions_item" in errs


def test_validate_career_strategy_layer_rejects_status_priority_mismatch() -> None:
    payload = build_career_strategy_layer(
        run_id="rid-career",
        mode="guarded_pipeline",
        summary={"quality": {"validation_ready": True}},
        review={"status": "completed_review_pass"},
        promotion_package={"proposed_stage": "senior"},
        capability_growth={"metrics": {"capability_growth_rate": 0.9}},
        transfer_learning={"metrics": {"transfer_efficiency_score": 0.9}},
        error_reduction={"metrics": {"error_reduction_rate": 0.9}},
        scalability_strategy={"scores": {"overall_scaling_score": 0.9}},
    )
    payload["strategy"]["priority"] = "stabilize"
    errs = validate_career_strategy_layer_dict(payload)
    assert "career_strategy_layer_status_priority_mismatch" in errs


def test_validate_career_strategy_layer_rejects_risk_readiness_mismatch() -> None:
    payload = build_career_strategy_layer(
        run_id="rid-career",
        mode="guarded_pipeline",
        summary={"quality": {"validation_ready": True}},
        review={"status": "completed_review_pass"},
        promotion_package={"proposed_stage": "senior"},
        capability_growth={"metrics": {"capability_growth_rate": 0.8}},
        transfer_learning={"metrics": {"transfer_efficiency_score": 0.8}},
        error_reduction={"metrics": {"error_reduction_rate": 0.8}},
        scalability_strategy={"scores": {"overall_scaling_score": 0.8}},
    )
    payload["strategy"]["risk_score"] = 0.0
    errs = validate_career_strategy_layer_dict(payload)
    assert "career_strategy_layer_risk_readiness_mismatch" in errs


def test_build_career_strategy_layer_fail_closed_for_non_numeric_metrics() -> None:
    payload = build_career_strategy_layer(
        run_id="rid-career",
        mode="guarded_pipeline",
        summary={"quality": {"validation_ready": True}},
        review={"status": "completed_review_pass"},
        promotion_package={"proposed_stage": "senior"},
        capability_growth={"metrics": {"capability_growth_rate": "bad"}},
        transfer_learning={"metrics": {"transfer_efficiency_score": None}},
        error_reduction={"metrics": {"error_reduction_rate": object()}},
        scalability_strategy={"scores": {"overall_scaling_score": True}},
    )
    assert payload["status"] == "hold"
    assert abs(payload["strategy"]["career_signal_score"]) < 1e-9


def test_build_career_strategy_layer_treats_truthy_validation_ready_as_not_ready() -> None:
    payload = build_career_strategy_layer(
        run_id="rid-career",
        mode="guarded_pipeline",
        summary={"quality": {"validation_ready": "yes"}},
        review={"status": "completed_review_pass"},
        promotion_package={"proposed_stage": "senior"},
        capability_growth={"metrics": {"capability_growth_rate": 1.0}},
        transfer_learning={"metrics": {"transfer_efficiency_score": 1.0}},
        error_reduction={"metrics": {"error_reduction_rate": 1.0}},
        scalability_strategy={"scores": {"overall_scaling_score": 1.0}},
    )
    assert payload["status"] == "watchlist"


def test_validate_career_strategy_layer_rejects_status_readiness_mismatch() -> None:
    payload = build_career_strategy_layer(
        run_id="rid-career",
        mode="guarded_pipeline",
        summary={"quality": {"validation_ready": True}},
        review={"status": "completed_review_pass"},
        promotion_package={"proposed_stage": "senior"},
        capability_growth={"metrics": {"capability_growth_rate": 0.9}},
        transfer_learning={"metrics": {"transfer_efficiency_score": 0.9}},
        error_reduction={"metrics": {"error_reduction_rate": 0.9}},
        scalability_strategy={"scores": {"overall_scaling_score": 0.9}},
    )
    payload["status"] = "hold"
    errs = validate_career_strategy_layer_dict(payload)
    assert "career_strategy_layer_status_readiness_mismatch" in errs


def test_build_career_strategy_layer_fail_closed_for_non_finite_metrics() -> None:
    payload = build_career_strategy_layer(
        run_id="rid-career-non-finite",
        mode="guarded_pipeline",
        summary={"quality": {"validation_ready": True}},
        review={"status": "completed_review_pass"},
        promotion_package={"proposed_stage": "senior"},
        capability_growth={"metrics": {"capability_growth_rate": math.nan}},
        transfer_learning={"metrics": {"transfer_efficiency_score": math.inf}},
        error_reduction={"metrics": {"error_reduction_rate": -math.inf}},
        scalability_strategy={"scores": {"overall_scaling_score": 0.9}},
    )
    assert payload["strategy"]["career_signal_score"] < 0.3


def test_validate_career_strategy_layer_rejects_non_finite_strategy_scores() -> None:
    payload = build_career_strategy_layer(
        run_id="rid-career-non-finite-contract",
        mode="guarded_pipeline",
        summary={"quality": {"validation_ready": True}},
        review={"status": "completed_review_pass"},
        promotion_package={"proposed_stage": "senior"},
        capability_growth={"metrics": {"capability_growth_rate": 0.8}},
        transfer_learning={"metrics": {"transfer_efficiency_score": 0.8}},
        error_reduction={"metrics": {"error_reduction_rate": 0.8}},
        scalability_strategy={"scores": {"overall_scaling_score": 0.8}},
    )
    payload["strategy"]["career_signal_score"] = math.nan
    errs = validate_career_strategy_layer_dict(payload)
    assert "career_strategy_layer_score_finite:career_signal_score" in errs


def test_validate_career_strategy_layer_rejects_noncanonical_evidence_ref() -> None:
    payload = build_career_strategy_layer(
        run_id="rid-career-evidence",
        mode="guarded_pipeline",
        summary={"quality": {"validation_ready": True}},
        review={"status": "completed_review_pass"},
        promotion_package={"proposed_stage": "senior"},
        capability_growth={"metrics": {"capability_growth_rate": 0.8}},
        transfer_learning={"metrics": {"transfer_efficiency_score": 0.8}},
        error_reduction={"metrics": {"error_reduction_rate": 0.8}},
        scalability_strategy={"scores": {"overall_scaling_score": 0.8}},
    )
    payload["evidence"]["career_strategy_ref"] = "strategy/career_strategy.json"
    errs = validate_career_strategy_layer_dict(payload)
    assert "career_strategy_layer_evidence_career_strategy_ref" in errs


def test_execute_career_strategy_runtime_detects_missing_sources() -> None:
    execution = execute_career_strategy_runtime(
        summary={},
        review={},
        promotion_package={},
        capability_growth={},
        transfer_learning={"metrics": {}},
        error_reduction={},
        scalability_strategy={},
    )
    assert execution["signals_processed"] == 7
    assert execution["has_proposed_stage"] is False
    assert execution["missing_signal_sources"] == [
        "summary",
        "review",
        "promotion_package",
        "capability_growth",
        "error_reduction",
        "scalability_strategy",
    ]

