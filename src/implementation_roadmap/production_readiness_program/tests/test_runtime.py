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

