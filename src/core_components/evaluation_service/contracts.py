"""Contracts for core evaluation-service runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

EVALUATION_SERVICE_CONTRACT = "sde.evaluation_service.v1"
EVALUATION_SERVICE_SCHEMA_VERSION = "1.0"


def _validate_metrics(metrics: Any) -> tuple[list[str], bool | None]:
    if not isinstance(metrics, dict):
        return (["evaluation_service_metrics"], None)
    errs: list[str] = []
    values: list[bool] = []
    for key in ("has_online_eval", "has_promotion_eval", "summary_has_metrics", "all_checks_passed"):
        value = metrics.get(key)
        if not isinstance(value, bool):
            errs.append(f"evaluation_service_metric_type:{key}")
            continue
        values.append(value)
    if errs:
        return (errs, None)
    has_online_eval, has_promotion_eval, summary_has_metrics, all_checks_passed = values
    expected_all_checks_passed = has_online_eval and has_promotion_eval and summary_has_metrics
    if all_checks_passed != expected_all_checks_passed:
        errs.append("evaluation_service_all_checks_passed_mismatch")
        return (errs, None)
    return ([], all_checks_passed)


def validate_evaluation_service_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["evaluation_service_not_object"]
    errs: list[str] = []
    if body.get("schema") != EVALUATION_SERVICE_CONTRACT:
        errs.append("evaluation_service_schema")
    if body.get("schema_version") != EVALUATION_SERVICE_SCHEMA_VERSION:
        errs.append("evaluation_service_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("evaluation_service_run_id")
    status = body.get("status")
    if status not in ("ready", "degraded"):
        errs.append("evaluation_service_status")
    metric_errs, all_checks_passed = _validate_metrics(body.get("metrics"))
    errs.extend(metric_errs)
    if all_checks_passed is not None and status in ("ready", "degraded"):
        expected_status = "ready" if all_checks_passed else "degraded"
        if status != expected_status:
            errs.append("evaluation_service_status_metrics_mismatch")
    return errs


def validate_evaluation_service_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["evaluation_service_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["evaluation_service_json"]
    return validate_evaluation_service_dict(body)
