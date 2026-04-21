from __future__ import annotations

from workflow_pipelines.production_pipeline_plan_artifact import (
    build_production_pipeline_plan_artifact,
    validate_production_pipeline_plan_artifact_dict,
)


def test_build_production_pipeline_plan_artifact_is_deterministic() -> None:
    manifest = {
        "project_plan": True,
        "progress": True,
        "work_batch": True,
        "discovery": True,
        "verification_bundle": True,
    }
    plan = {"steps": [{"step_id": "step_planner"}]}
    one = build_production_pipeline_plan_artifact(
        run_id="rid-plan-artifact",
        mode="guarded_pipeline",
        program_manifest=manifest,
        project_plan=plan,
    )
    two = build_production_pipeline_plan_artifact(
        run_id="rid-plan-artifact",
        mode="guarded_pipeline",
        program_manifest=manifest,
        project_plan=plan,
    )
    assert one == two
    assert validate_production_pipeline_plan_artifact_dict(one) == []


def test_validate_production_pipeline_plan_artifact_fail_closed() -> None:
    errs = validate_production_pipeline_plan_artifact_dict({"schema": "bad"})
    assert "production_pipeline_plan_artifact_schema" in errs
    assert "production_pipeline_plan_artifact_schema_version" in errs
