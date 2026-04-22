from __future__ import annotations

import pytest

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


def test_build_promotion_evaluation_fails_closed_on_truthy_non_bool_passed() -> None:
    payload = build_promotion_evaluation(
        run_id="rid-promotion-eval",
        promotion_package={"readiness": {"score": 1.0}},
        review={"status": "completed_review_pass"},
        events=[{"stage": "finalize", "score": {"passed": "true"}}],
    )
    assert payload["signals"]["finalize_pass_rate"] == pytest.approx(0.0)
    assert payload["decision"] == "hold"


def test_validate_promotion_evaluation_rejects_decision_signal_mismatch() -> None:
    payload = build_promotion_evaluation(
        run_id="rid-promotion-eval",
        promotion_package={"readiness": {"score": 0.9}},
        review={"status": "completed_review_pass"},
        events=[{"stage": "finalize", "score": {"passed": True}}],
    )
    payload["confidence"] = 0.0
    payload["decision"] = "promote"
    errs = validate_promotion_evaluation_dict(payload)
    assert "promotion_evaluation_confidence_semantics" in errs
    assert "promotion_evaluation_decision_semantics" in errs


def test_validate_promotion_evaluation_rejects_noncanonical_evidence_ref() -> None:
    payload = build_promotion_evaluation(
        run_id="rid-promotion-eval",
        promotion_package={"readiness": {"score": 0.9}},
        review={"status": "completed_review_pass"},
        events=[{"stage": "finalize", "score": {"passed": True}}],
    )
    payload["evidence"]["promotion_evaluation_ref"] = "learning/other_promotion_evaluation.json"
    errs = validate_promotion_evaluation_dict(payload)
    assert "promotion_evaluation_evidence_ref:promotion_evaluation_ref" in errs


def test_validate_promotion_evaluation_rejects_unsafe_evidence_ref_path() -> None:
    payload = build_promotion_evaluation(
        run_id="rid-promotion-eval",
        promotion_package={"readiness": {"score": 0.9}},
        review={"status": "completed_review_pass"},
        events=[{"stage": "finalize", "score": {"passed": True}}],
    )
    payload["evidence"]["review_ref"] = "../review.json"
    errs = validate_promotion_evaluation_dict(payload)
    assert "promotion_evaluation_evidence_ref:review_ref" in errs
