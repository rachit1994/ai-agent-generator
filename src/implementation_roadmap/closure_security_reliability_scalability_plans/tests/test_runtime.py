from __future__ import annotations

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

