from __future__ import annotations

from implementation_roadmap.consolidated_improvements import (
    build_consolidated_improvements,
    validate_consolidated_improvements_dict,
)


def test_build_consolidated_improvements_is_deterministic() -> None:
    summary = {"quality": {"validation_ready": True}}
    review = {"status": "completed_review_pass", "artifact_manifest": [{"path": "a", "present": True}]}
    readiness = {"status": "ready"}
    scalability = {"status": "scalable"}
    boundaries = {"status": "bounded"}
    storage = {"status": "consistent"}
    learning = {
        "capability_growth_metrics": {"ok": True},
        "error_reduction_metrics": {"ok": True},
        "extended_binary_gates": {"ok": True},
        "transfer_learning_metrics": {"ok": True},
    }
    one = build_consolidated_improvements(
        run_id="rid-cons",
        mode="guarded_pipeline",
        summary=summary,
        review=review,
        readiness=readiness,
        scalability=scalability,
        boundaries=boundaries,
        storage=storage,
        learning_metrics=learning,
    )
    two = build_consolidated_improvements(
        run_id="rid-cons",
        mode="guarded_pipeline",
        summary=summary,
        review=review,
        readiness=readiness,
        scalability=scalability,
        boundaries=boundaries,
        storage=storage,
        learning_metrics=learning,
    )
    assert one == two
    assert validate_consolidated_improvements_dict(one) == []


def test_validate_consolidated_improvements_fail_closed() -> None:
    errs = validate_consolidated_improvements_dict({"schema": "bad"})
    assert "consolidated_improvements_schema" in errs
    assert "consolidated_improvements_schema_version" in errs


def test_build_consolidated_improvements_treats_truthy_non_boolean_inputs_as_not_ready() -> None:
    payload = build_consolidated_improvements(
        run_id="rid-cons",
        mode="guarded_pipeline",
        summary={"quality": {"validation_ready": "true"}},
        review={"status": "completed_review_pass", "artifact_manifest": [{"path": "a", "present": "true"}]},
        readiness={"status": "ready"},
        scalability={"status": "scalable"},
        boundaries={"status": "bounded"},
        storage={"status": "consistent"},
        learning_metrics={
            "capability_growth_metrics": {"ok": "true"},
            "error_reduction_metrics": {"ok": "true"},
            "extended_binary_gates": {"ok": "true"},
            "transfer_learning_metrics": {"ok": "true"},
        },
    )
    assert payload["status"] == "not_ready"
    assert payload["summary"]["validation_ready"] is False
    assert payload["summary"]["required_artifacts_present"] is False
    assert payload["improvements"]["capability_growth_metrics"]["ok"] is False


def test_validate_consolidated_improvements_rejects_status_summary_mismatch() -> None:
    payload = build_consolidated_improvements(
        run_id="rid-cons",
        mode="guarded_pipeline",
        summary={"quality": {"validation_ready": True}},
        review={"status": "completed_review_pass", "artifact_manifest": [{"path": "a", "present": True}]},
        readiness={"status": "ready"},
        scalability={"status": "scalable"},
        boundaries={"status": "bounded"},
        storage={"status": "consistent"},
        learning_metrics={
            "capability_growth_metrics": {"ok": True},
            "error_reduction_metrics": {"ok": True},
            "extended_binary_gates": {"ok": True},
            "transfer_learning_metrics": {"ok": True},
        },
    )
    payload["status"] = "not_ready"
    errs = validate_consolidated_improvements_dict(payload)
    assert "consolidated_improvements_status_summary_mismatch" in errs


def test_build_consolidated_improvements_requires_non_empty_artifact_manifest() -> None:
    payload = build_consolidated_improvements(
        run_id="rid-cons-empty-artifacts",
        mode="guarded_pipeline",
        summary={"quality": {"validation_ready": True}},
        review={"status": "completed_review_pass", "artifact_manifest": []},
        readiness={"status": "ready"},
        scalability={"status": "scalable"},
        boundaries={"status": "bounded"},
        storage={"status": "consistent"},
        learning_metrics={
            "capability_growth_metrics": {"ok": True},
            "error_reduction_metrics": {"ok": True},
            "extended_binary_gates": {"ok": True},
            "transfer_learning_metrics": {"ok": True},
        },
    )
    assert payload["status"] == "not_ready"
    assert payload["summary"]["required_artifacts_present"] is False

