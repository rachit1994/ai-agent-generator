from __future__ import annotations

import math

import pytest

from implementation_roadmap.closure_security_reliability_scalability_plans import (
    build_closure_security_reliability_scalability_plans,
    validate_closure_security_reliability_scalability_plans_dict,
)


def test_build_closure_security_reliability_scalability_plans_is_deterministic() -> None:
    summary = {"quality": {"validation_ready": True}, "metrics": {"reliability": 0.9, "retryFrequency": 0.1}}
    review = {"status": "completed_review_pass"}
    readiness = {"status": "ready"}
    scalability = {"status": "scalable"}
    boundaries = {"status": "bounded"}
    storage = {"status": "consistent"}
    one = build_closure_security_reliability_scalability_plans(
        run_id="rid-csrs",
        mode="guarded_pipeline",
        summary=summary,
        review=review,
        readiness=readiness,
        scalability=scalability,
        boundaries=boundaries,
        storage=storage,
        policy_bundle_valid=True,
    )
    two = build_closure_security_reliability_scalability_plans(
        run_id="rid-csrs",
        mode="guarded_pipeline",
        summary=summary,
        review=review,
        readiness=readiness,
        scalability=scalability,
        boundaries=boundaries,
        storage=storage,
        policy_bundle_valid=True,
    )
    assert one == two
    assert validate_closure_security_reliability_scalability_plans_dict(one) == []


def test_validate_closure_security_reliability_scalability_plans_fail_closed() -> None:
    errs = validate_closure_security_reliability_scalability_plans_dict({"schema": "bad"})
    assert "closure_security_reliability_scalability_plans_schema" in errs
    assert "closure_security_reliability_scalability_plans_schema_version" in errs


def test_build_closure_security_reliability_scalability_plans_treats_truthy_validation_ready_as_blocked() -> None:
    payload = build_closure_security_reliability_scalability_plans(
        run_id="rid-csrs",
        mode="guarded_pipeline",
        summary={"quality": {"validation_ready": "true"}, "metrics": {"reliability": 0.9, "retryFrequency": 0.1}},
        review={"status": "completed_review_pass"},
        readiness={"status": "ready"},
        scalability={"status": "scalable"},
        boundaries={"status": "bounded"},
        storage={"status": "consistent"},
        policy_bundle_valid=True,
    )
    assert payload["plans"]["closure"]["status"] == "blocked"
    assert payload["plans"]["security"]["status"] == "blocked"


def test_validate_closure_security_reliability_scalability_plans_rejects_plan_status_ok_mismatch() -> None:
    payload = build_closure_security_reliability_scalability_plans(
        run_id="rid-csrs",
        mode="guarded_pipeline",
        summary={"quality": {"validation_ready": True}, "metrics": {"reliability": 0.9, "retryFrequency": 0.1}},
        review={"status": "completed_review_pass"},
        readiness={"status": "ready"},
        scalability={"status": "scalable"},
        boundaries={"status": "bounded"},
        storage={"status": "consistent"},
        policy_bundle_valid=True,
    )
    payload["plans"]["closure"]["status"] = "blocked"
    errs = validate_closure_security_reliability_scalability_plans_dict(payload)
    assert "closure_security_reliability_scalability_plans_plan_status_mismatch:closure" in errs


def test_build_closure_plans_fail_closed_on_non_numeric_metrics() -> None:
    payload = build_closure_security_reliability_scalability_plans(
        run_id="rid-csrs",
        mode="guarded_pipeline",
        summary={"quality": {"validation_ready": True}, "metrics": {"reliability": "bad", "retryFrequency": "bad"}},
        review={"status": "completed_review_pass"},
        readiness={"status": "ready"},
        scalability={"status": "scalable"},
        boundaries={"status": "bounded"},
        storage={"status": "consistent"},
        policy_bundle_valid=True,
    )
    assert payload["plans"]["reliability"]["ok"] is False
    assert payload["plans"]["reliability"]["status"] == "blocked"


def test_build_closure_plans_fail_closed_on_non_finite_metrics() -> None:
    payload = build_closure_security_reliability_scalability_plans(
        run_id="rid-csrs",
        mode="guarded_pipeline",
        summary={
            "quality": {"validation_ready": True},
            "metrics": {"reliability": math.nan, "retryFrequency": math.inf, "passRate": -math.inf},
        },
        review={"status": "completed_review_pass"},
        readiness={"status": "ready"},
        scalability={"status": "scalable"},
        boundaries={"status": "bounded"},
        storage={"status": "consistent"},
        policy_bundle_valid=True,
    )
    assert payload["plans"]["reliability"]["metrics"]["reliability"] == pytest.approx(0.0)
    assert payload["plans"]["reliability"]["metrics"]["retry_frequency"] == pytest.approx(1.0)
    assert payload["plans"]["reliability"]["metrics"]["pass_rate"] == pytest.approx(0.0)


def test_validate_closure_plans_rejects_top_level_status_summary_mismatch() -> None:
    payload = build_closure_security_reliability_scalability_plans(
        run_id="rid-csrs",
        mode="guarded_pipeline",
        summary={"quality": {"validation_ready": True}, "metrics": {"reliability": 0.9, "retryFrequency": 0.1}},
        review={"status": "completed_review_pass"},
        readiness={"status": "ready"},
        scalability={"status": "scalable"},
        boundaries={"status": "bounded"},
        storage={"status": "consistent"},
        policy_bundle_valid=True,
    )
    payload["status"] = "not_ready"
    payload["summary"]["plans_ready"] = 0
    payload["summary"]["plans_total"] = 3
    payload["summary"]["overall_score"] = 0.0
    errs = validate_closure_security_reliability_scalability_plans_dict(payload)
    assert "closure_security_reliability_scalability_plans_status_mismatch" in errs
    assert "closure_security_reliability_scalability_plans_summary_plans_ready_mismatch" in errs
    assert "closure_security_reliability_scalability_plans_summary_plans_total_mismatch" in errs
    assert "closure_security_reliability_scalability_plans_summary_overall_score_mismatch" in errs


def test_validate_closure_plans_rejects_invalid_evidence_refs() -> None:
    payload = build_closure_security_reliability_scalability_plans(
        run_id="rid-csrs",
        mode="guarded_pipeline",
        summary={"quality": {"validation_ready": True}, "metrics": {"reliability": 0.9, "retryFrequency": 0.1}},
        review={"status": "completed_review_pass"},
        readiness={"status": "ready"},
        scalability={"status": "scalable"},
        boundaries={"status": "bounded"},
        storage={"status": "consistent"},
        policy_bundle_valid=True,
    )
    payload["evidence"]["summary_ref"] = "../summary.json"
    payload["evidence"]["review_ref"] = "review.txt"
    errs = validate_closure_security_reliability_scalability_plans_dict(payload)
    assert "closure_security_reliability_scalability_plans_evidence_ref:summary_ref" in errs
    assert "closure_security_reliability_scalability_plans_evidence_ref:review_ref" in errs

