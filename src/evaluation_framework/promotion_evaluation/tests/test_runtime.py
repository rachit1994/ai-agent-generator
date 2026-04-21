from __future__ import annotations

from evaluation_framework.promotion_evaluation import (
    build_promotion_evaluation,
    validate_promotion_evaluation_dict,
)


def test_build_promotion_evaluation_is_deterministic() -> None:
    events = [{"stage": "finalize", "score": {"passed": True}}]
    one = build_promotion_evaluation(
        run_id="rid-promotion-eval",
        promotion_package={"readiness": {"score": 0.9}},
        review={"status": "completed_review_pass"},
        events=events,
    )
    two = build_promotion_evaluation(
        run_id="rid-promotion-eval",
        promotion_package={"readiness": {"score": 0.9}},
        review={"status": "completed_review_pass"},
        events=events,
    )
    assert one == two
    assert validate_promotion_evaluation_dict(one) == []


def test_validate_promotion_evaluation_fail_closed() -> None:
    errs = validate_promotion_evaluation_dict({"schema": "bad"})
    assert "promotion_evaluation_schema" in errs
    assert "promotion_evaluation_schema_version" in errs
