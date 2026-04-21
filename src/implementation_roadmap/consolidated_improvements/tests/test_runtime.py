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

