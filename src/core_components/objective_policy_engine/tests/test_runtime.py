from __future__ import annotations

from core_components.objective_policy_engine import (
    build_objective_policy_engine,
    validate_objective_policy_engine_dict,
)


def test_build_objective_policy_engine_is_deterministic() -> None:
    summary = {"balanced_gates": {"reliability": 95, "delivery": 92, "governance": 97, "composite": 94}}
    review = {"status": "completed_review_pass"}
    cto = {"hard_stops": [{"id": "HS01", "passed": True}]}
    one = build_objective_policy_engine(
        run_id="rid-objective-policy",
        mode="guarded_pipeline",
        summary=summary,
        review=review,
        cto=cto,
        policy_bundle_rollback_errors=[],
    )
    two = build_objective_policy_engine(
        run_id="rid-objective-policy",
        mode="guarded_pipeline",
        summary=summary,
        review=review,
        cto=cto,
        policy_bundle_rollback_errors=[],
    )
    assert one == two
    assert validate_objective_policy_engine_dict(one) == []


def test_validate_objective_policy_engine_fail_closed() -> None:
    errs = validate_objective_policy_engine_dict({"schema": "bad"})
    assert "objective_policy_engine_schema" in errs
    assert "objective_policy_engine_schema_version" in errs


def test_build_objective_policy_engine_treats_truthy_non_boolean_hard_stop_as_failed() -> None:
    payload = build_objective_policy_engine(
        run_id="rid-objective-policy",
        mode="guarded_pipeline",
        summary={"balanced_gates": {}},
        review={"status": "completed_review_pass"},
        cto={"hard_stops": [{"id": "HS01", "passed": "true"}]},
        policy_bundle_rollback_errors=[],
    )
    assert payload["policy"]["decision"] == "deny"
    assert payload["context"]["failed_hard_stop_count"] == 1


def test_build_objective_policy_engine_denies_when_composite_score_below_release_floor() -> None:
    payload = build_objective_policy_engine(
        run_id="rid-objective-policy",
        mode="guarded_pipeline",
        summary={"balanced_gates": {"reliability": 90, "delivery": 88, "governance": 91, "composite": 64}},
        review={"status": "completed_review_pass"},
        cto={"hard_stops": [{"id": "HS01", "passed": True}]},
        policy_bundle_rollback_errors=[],
    )
    assert payload["policy"]["decision"] == "deny"
    assert payload["policy"]["reason"] == "score_floor_failure"


def test_validate_objective_policy_engine_rejects_policy_context_mismatch() -> None:
    payload = build_objective_policy_engine(
        run_id="rid-objective-policy",
        mode="guarded_pipeline",
        summary={"balanced_gates": {"reliability": 95, "delivery": 95, "governance": 95, "composite": 95}},
        review={"status": "completed_review_pass"},
        cto={"hard_stops": [{"id": "HS01", "passed": True}]},
        policy_bundle_rollback_errors=[],
    )
    payload["policy"]["decision"] = "allow"
    payload["context"]["failed_hard_stop_count"] = 1
    errs = validate_objective_policy_engine_dict(payload)
    assert "objective_policy_engine_policy_context_mismatch" in errs
