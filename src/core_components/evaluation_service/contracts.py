"""Contracts for core evaluation-service runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

EVALUATION_SERVICE_CONTRACT = "sde.evaluation_service.v1"
EVALUATION_SERVICE_SCHEMA_VERSION = "1.0"


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
    metrics = body.get("metrics")
    if not isinstance(metrics, dict):
        errs.append("evaluation_service_metrics")
    else:
        for key in ("has_online_eval", "has_promotion_eval", "summary_has_metrics", "all_checks_passed"):
            if not isinstance(metrics.get(key), bool):
                errs.append(f"evaluation_service_metric_type:{key}")
    return errs


def validate_evaluation_service_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["evaluation_service_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["evaluation_service_json"]
    return validate_evaluation_service_dict(body)
