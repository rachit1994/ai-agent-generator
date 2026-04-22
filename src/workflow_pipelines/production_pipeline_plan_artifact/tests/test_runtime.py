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


def test_build_production_pipeline_plan_artifact_treats_truthy_non_boolean_checks_as_false() -> None:
    payload = build_production_pipeline_plan_artifact(
        run_id="rid-plan-artifact",
        mode="guarded_pipeline",
        program_manifest={
            "project_plan": "true",
            "progress": "true",
            "work_batch": "true",
            "discovery": "true",
            "verification_bundle": "true",
        },
        project_plan={"steps": [{"step_id": "step_planner"}]},
    )
    assert payload["status"] == "partial"
    assert payload["checks"]["project_plan_present"] is False


def test_validate_production_pipeline_plan_artifact_rejects_status_checks_mismatch() -> None:
    payload = build_production_pipeline_plan_artifact(
        run_id="rid-plan-artifact",
        mode="guarded_pipeline",
        program_manifest={
            "project_plan": True,
            "progress": True,
            "work_batch": True,
            "discovery": True,
            "verification_bundle": True,
        },
        project_plan={"steps": [{"step_id": "step_planner"}]},
    )
    payload["status"] = "partial"
    errs = validate_production_pipeline_plan_artifact_dict(payload)
    assert "production_pipeline_plan_artifact_status_checks_mismatch" in errs


def test_validate_production_pipeline_plan_artifact_rejects_invalid_evidence_refs() -> None:
    payload = build_production_pipeline_plan_artifact(
        run_id="rid-plan-artifact",
        mode="guarded_pipeline",
        program_manifest={
            "project_plan": True,
            "progress": True,
            "work_batch": True,
            "discovery": True,
            "verification_bundle": True,
        },
        project_plan={"steps": [{"step_id": "step_planner"}]},
    )
    payload["evidence"]["project_plan_ref"] = "../program/project_plan.json"
    errs = validate_production_pipeline_plan_artifact_dict(payload)
    assert "production_pipeline_plan_artifact_evidence_ref:project_plan_ref" in errs


def test_validate_production_pipeline_plan_artifact_rejects_checked_artifacts_mismatch() -> None:
    payload = build_production_pipeline_plan_artifact(
        run_id="rid-plan-artifact",
        mode="guarded_pipeline",
        program_manifest={
            "project_plan": True,
            "progress": True,
            "work_batch": True,
            "discovery": True,
            "verification_bundle": True,
        },
        project_plan={"steps": [{"step_id": "step_planner"}]},
    )
    payload["metrics"]["checked_program_artifacts"] = 4
    errs = validate_production_pipeline_plan_artifact_dict(payload)
    assert "production_pipeline_plan_artifact_checked_program_artifacts_mismatch" in errs
