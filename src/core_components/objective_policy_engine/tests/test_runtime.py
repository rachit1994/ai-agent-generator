from __future__ import annotations

from core_components.objective_policy_engine import (
    build_objective_policy_engine,
    execute_objective_policy_runtime,
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
    assert one["execution"]["signals_processed"] == 4


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


def test_build_objective_policy_engine_denies_with_rollback_validation_failure_reason() -> None:
    payload = build_objective_policy_engine(
        run_id="rid-objective-policy",
        mode="guarded_pipeline",
        summary={"balanced_gates": {"reliability": 95, "delivery": 95, "governance": 95, "composite": 95}},
        review={"status": "completed_review_pass"},
        cto={"hard_stops": [{"id": "HS01", "passed": True}]},
        policy_bundle_rollback_errors=["rollback_contract_error"],
    )
    assert payload["policy"]["decision"] == "deny"
    assert payload["policy"]["reason"] == "rollback_validation_failure"


def test_validate_objective_policy_engine_rejects_missing_evidence() -> None:
    payload = build_objective_policy_engine(
        run_id="rid-objective-policy",
        mode="guarded_pipeline",
        summary={"balanced_gates": {"reliability": 95, "delivery": 95, "governance": 95, "composite": 95}},
        review={"status": "completed_review_pass"},
        cto={"hard_stops": [{"id": "HS01", "passed": True}]},
        policy_bundle_rollback_errors=[],
    )
    payload["evidence"] = {}
    errs = validate_objective_policy_engine_dict(payload)
    assert "objective_policy_engine_evidence_ref:summary_ref" in errs
    assert "objective_policy_engine_evidence_ref:review_ref" in errs
    assert "objective_policy_engine_evidence_ref:policy_bundle_ref" in errs
    assert "objective_policy_engine_evidence_ref:objective_policy_ref" in errs


def test_validate_objective_policy_engine_rejects_non_object_evidence() -> None:
    payload = build_objective_policy_engine(
        run_id="rid-objective-policy",
        mode="guarded_pipeline",
        summary={"balanced_gates": {"reliability": 95, "delivery": 95, "governance": 95, "composite": 95}},
        review={"status": "completed_review_pass"},
        cto={"hard_stops": [{"id": "HS01", "passed": True}]},
        policy_bundle_rollback_errors=[],
    )
    payload["evidence"] = "bad"
    errs = validate_objective_policy_engine_dict(payload)
    assert "objective_policy_engine_evidence" in errs


def test_validate_objective_policy_engine_rejects_deny_reason_when_rollback_is_ok() -> None:
    payload = build_objective_policy_engine(
        run_id="rid-objective-policy",
        mode="guarded_pipeline",
        summary={"balanced_gates": {"reliability": 95, "delivery": 95, "governance": 95, "composite": 95}},
        review={"status": "completed_review_pass"},
        cto={"hard_stops": [{"id": "HS01", "passed": True}]},
        policy_bundle_rollback_errors=["rollback_contract_error"],
    )
    payload["context"]["rollback_errors"] = []
    errs = validate_objective_policy_engine_dict(payload)
    assert "objective_policy_engine_policy_context_mismatch" in errs


def test_validate_objective_policy_engine_rejects_unknown_deny_reason() -> None:
    payload = build_objective_policy_engine(
        run_id="rid-objective-policy",
        mode="guarded_pipeline",
        summary={"balanced_gates": {"reliability": 95, "delivery": 95, "governance": 95, "composite": 95}},
        review={"status": "completed_review_pass"},
        cto={"hard_stops": [{"id": "HS01", "passed": True}]},
        policy_bundle_rollback_errors=["rollback_contract_error"],
    )
    payload["policy"]["reason"] = "other_reason"
    errs = validate_objective_policy_engine_dict(payload)
    assert "objective_policy_engine_policy_reason_deny" in errs


def test_execute_objective_policy_runtime_detects_missing_sources() -> None:
    execution = execute_objective_policy_runtime(
        summary={},
        review={"status": "completed_review_pass"},
        cto={"hard_stops": ["bad-row"]},  # type: ignore[list-item]
        policy_bundle_rollback_errors=["err-1"],
    )
    assert execution["signals_processed"] == 4
    assert execution["hard_stop_rows_processed"] == 1
    assert execution["malformed_hard_stop_rows"] == 1
    assert execution["rollback_error_count"] == 1
    assert execution["missing_signal_sources"] == ["summary"]
