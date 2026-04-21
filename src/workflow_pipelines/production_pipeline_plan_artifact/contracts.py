"""Contracts for production-pipeline-plan-artifact runtime."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PRODUCTION_PIPELINE_PLAN_ARTIFACT_CONTRACT = "sde.production_pipeline_plan_artifact.v1"
PRODUCTION_PIPELINE_PLAN_ARTIFACT_SCHEMA_VERSION = "1.0"


def validate_production_pipeline_plan_artifact_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["production_pipeline_plan_artifact_not_object"]
    errs: list[str] = []
    if body.get("schema") != PRODUCTION_PIPELINE_PLAN_ARTIFACT_CONTRACT:
        errs.append("production_pipeline_plan_artifact_schema")
    if body.get("schema_version") != PRODUCTION_PIPELINE_PLAN_ARTIFACT_SCHEMA_VERSION:
        errs.append("production_pipeline_plan_artifact_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("production_pipeline_plan_artifact_run_id")
    mode = body.get("mode")
    if mode not in ("guarded_pipeline", "phased_pipeline", "baseline"):
        errs.append("production_pipeline_plan_artifact_mode")
    status = body.get("status")
    if status not in ("ready", "partial"):
        errs.append("production_pipeline_plan_artifact_status")
    checks = body.get("checks")
    if not isinstance(checks, dict):
        errs.append("production_pipeline_plan_artifact_checks")
    else:
        for key in (
            "project_plan_present",
            "progress_present",
            "work_batch_present",
            "discovery_present",
            "verification_bundle_present",
        ):
            if not isinstance(checks.get(key), bool):
                errs.append(f"production_pipeline_plan_artifact_check_type:{key}")
    return errs


def validate_production_pipeline_plan_artifact_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["production_pipeline_plan_artifact_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["production_pipeline_plan_artifact_json"]
    return validate_production_pipeline_plan_artifact_dict(body)
