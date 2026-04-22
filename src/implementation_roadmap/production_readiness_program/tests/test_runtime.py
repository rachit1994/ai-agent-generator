from __future__ import annotations

from implementation_roadmap.production_readiness_program import (
    build_production_readiness_program,
    validate_production_readiness_program_dict,
)


def test_build_production_readiness_program_is_deterministic() -> None:
    summary = {"runId": "run-readiness", "mode": "guarded_pipeline", "balanced_gates": {"validation_ready": True}}
    review = {"status": "completed_review_pass"}
    hard_stops = [{"id": "HS01", "passed": True}]
    artifacts = [{"path": "summary.json", "present": True}]
    one = build_production_readiness_program(
        run_id="run-readiness",
        mode="guarded_pipeline",
        summary=summary,
        review=review,
        hard_stops=hard_stops,
        artifact_paths=artifacts,
    )
    two = build_production_readiness_program(
        run_id="run-readiness",
        mode="guarded_pipeline",
        summary=summary,
        review=review,
        hard_stops=hard_stops,
        artifact_paths=artifacts,
    )
    assert one == two
    assert validate_production_readiness_program_dict(one) == []


def test_validate_production_readiness_program_fail_closed() -> None:
    errs = validate_production_readiness_program_dict({"schema": "bad"})
    assert "production_readiness_program_schema" in errs
    assert "production_readiness_program_schema_version" in errs


def test_production_readiness_runtime_rejects_truthy_non_boolean_checks() -> None:
    payload = build_production_readiness_program(
        run_id="run-readiness",
        mode="guarded_pipeline",
        summary={"runId": "run-readiness", "mode": "guarded_pipeline", "balanced_gates": {"validation_ready": True}},
        review={"status": "completed_review_pass"},
        hard_stops=[{"id": "HS01", "passed": "true"}],
        artifact_paths=[{"path": "summary.json", "present": "yes"}],
    )
    assert payload["checks"]["hard_stops_passed"] is False
    assert payload["checks"]["required_artifacts_present"] is False
    assert payload["status"] == "not_ready"
    assert validate_production_readiness_program_dict(payload) == []


def test_validate_production_readiness_rejects_status_checks_mismatch() -> None:
    payload = build_production_readiness_program(
        run_id="run-readiness",
        mode="guarded_pipeline",
        summary={"runId": "run-readiness", "mode": "guarded_pipeline", "balanced_gates": {"validation_ready": True}},
        review={"status": "completed_review_pass"},
        hard_stops=[{"id": "HS01", "passed": True}],
        artifact_paths=[{"path": "summary.json", "present": True}],
    )
    payload["status"] = "not_ready"
    errs = validate_production_readiness_program_dict(payload)
    assert "production_readiness_program_status_checks_mismatch" in errs


def test_production_readiness_runtime_treats_truthy_validation_ready_as_not_ready() -> None:
    payload = build_production_readiness_program(
        run_id="run-readiness",
        mode="guarded_pipeline",
        summary={"runId": "run-readiness", "mode": "guarded_pipeline", "balanced_gates": {"validation_ready": "true"}},
        review={"status": "completed_review_pass"},
        hard_stops=[{"id": "HS01", "passed": True}],
        artifact_paths=[{"path": "summary.json", "present": True}],
    )
    assert payload["checks"]["balanced_gates_ready"] is False
    assert payload["status"] == "not_ready"


def test_validate_production_readiness_rejects_policy_bundle_mismatch() -> None:
    payload = build_production_readiness_program(
        run_id="run-readiness",
        mode="guarded_pipeline",
        summary={"runId": "run-readiness", "mode": "guarded_pipeline", "balanced_gates": {"validation_ready": True}},
        review={"status": "completed_review_pass"},
        hard_stops=[{"id": "HS01", "passed": True}],
        artifact_paths=[{"path": "summary.json", "present": True}],
    )
    payload["checks"]["policy_bundle_valid"] = False
    errs = validate_production_readiness_program_dict(payload)
    assert "production_readiness_program_policy_bundle_mismatch" in errs


def test_production_readiness_runtime_requires_non_empty_hard_stops() -> None:
    payload = build_production_readiness_program(
        run_id="run-readiness",
        mode="guarded_pipeline",
        summary={"runId": "run-readiness", "mode": "guarded_pipeline", "balanced_gates": {"validation_ready": True}},
        review={"status": "completed_review_pass"},
        hard_stops=[],
        artifact_paths=[{"path": "summary.json", "present": True}],
    )
    assert payload["checks"]["hard_stops_passed"] is False
    assert payload["status"] == "not_ready"


def test_production_readiness_runtime_requires_non_empty_artifact_paths() -> None:
    payload = build_production_readiness_program(
        run_id="run-readiness",
        mode="guarded_pipeline",
        summary={"runId": "run-readiness", "mode": "guarded_pipeline", "balanced_gates": {"validation_ready": True}},
        review={"status": "completed_review_pass"},
        hard_stops=[{"id": "HS01", "passed": True}],
        artifact_paths=[],
    )
    assert payload["checks"]["required_artifacts_present"] is False
    assert payload["checks"]["policy_bundle_valid"] is False
    assert payload["status"] == "not_ready"


def test_validate_production_readiness_rejects_unknown_mode() -> None:
    payload = build_production_readiness_program(
        run_id="run-readiness",
        mode="guarded_pipeline",
        summary={"runId": "run-readiness", "mode": "guarded_pipeline", "balanced_gates": {"validation_ready": True}},
        review={"status": "completed_review_pass"},
        hard_stops=[{"id": "HS01", "passed": True}],
        artifact_paths=[{"path": "summary.json", "present": True}],
    )
    payload["mode"] = "unknown_mode"
    errs = validate_production_readiness_program_dict(payload)
    assert "production_readiness_program_mode" in errs


def test_validate_production_readiness_rejects_invalid_evidence_refs() -> None:
    payload = build_production_readiness_program(
        run_id="run-readiness",
        mode="guarded_pipeline",
        summary={"runId": "run-readiness", "mode": "guarded_pipeline", "balanced_gates": {"validation_ready": True}},
        review={"status": "completed_review_pass"},
        hard_stops=[{"id": "HS01", "passed": True}],
        artifact_paths=[{"path": "summary.json", "present": True}],
    )
    payload["evidence"]["summary_ref"] = "../summary.json"
    payload["evidence"]["review_ref"] = ""
    errs = validate_production_readiness_program_dict(payload)
    assert "production_readiness_program_evidence_ref:summary_ref" in errs
    assert "production_readiness_program_evidence_ref:review_ref" in errs

