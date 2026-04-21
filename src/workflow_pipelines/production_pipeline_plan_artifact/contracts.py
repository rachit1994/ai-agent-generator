"""Contracts for production-pipeline-plan-artifact runtime."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PRODUCTION_PIPELINE_PLAN_ARTIFACT_CONTRACT = "sde.production_pipeline_plan_artifact.v1"
PRODUCTION_PIPELINE_PLAN_ARTIFACT_SCHEMA_VERSION = "1.0"


def _validate_checks(checks: Any) -> tuple[list[str], bool | None]:
    if not isinstance(checks, dict):
        return (["production_pipeline_plan_artifact_checks"], None)
    errs: list[str] = []
    values: list[bool] = []
    for key in (
        "project_plan_present",
        "progress_present",
        "work_batch_present",
        "discovery_present",
        "verification_bundle_present",
    ):
        value = checks.get(key)
        if not isinstance(value, bool):
            errs.append(f"production_pipeline_plan_artifact_check_type:{key}")
            continue
        values.append(value)
    if errs:
        return (errs, None)
    return ([], all(values))


def _validate_metrics_step_count(metrics: Any) -> tuple[list[str], int | None]:
    if not isinstance(metrics, dict):
        return (["production_pipeline_plan_artifact_metrics"], None)
    step_count_value = metrics.get("step_count")
    if isinstance(step_count_value, bool) or not isinstance(step_count_value, int):
        return (["production_pipeline_plan_artifact_step_count_type"], None)
    if step_count_value < 0:
        return (["production_pipeline_plan_artifact_step_count_range"], None)
    return ([], step_count_value)


def _validate_status_consistency(
    *,
    status: Any,
    checks_all_true: bool | None,
    step_count: int | None,
) -> list[str]:
    if checks_all_true is None or step_count is None or status not in ("ready", "partial"):
        return []
    expected_status = "ready" if (checks_all_true and step_count > 0) else "partial"
    if status != expected_status:
        return ["production_pipeline_plan_artifact_status_checks_mismatch"]
    return []


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
    check_errs, checks_all_true = _validate_checks(body.get("checks"))
    errs.extend(check_errs)
    metric_errs, step_count = _validate_metrics_step_count(body.get("metrics"))
    errs.extend(metric_errs)
    errs.extend(_validate_status_consistency(status=status, checks_all_true=checks_all_true, step_count=step_count))
    return errs


def validate_production_pipeline_plan_artifact_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["production_pipeline_plan_artifact_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["production_pipeline_plan_artifact_json"]
    return validate_production_pipeline_plan_artifact_dict(body)
