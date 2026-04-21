from __future__ import annotations

from core_components.career_strategy_layer import (
    build_career_strategy_layer,
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


def test_validate_career_strategy_layer_fail_closed() -> None:
    errs = validate_career_strategy_layer_dict({"schema": "bad"})
    assert "career_strategy_layer_schema" in errs
    assert "career_strategy_layer_schema_version" in errs

