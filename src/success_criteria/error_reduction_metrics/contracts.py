"""Contracts for error reduction metrics artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ERROR_REDUCTION_METRICS_CONTRACT = "sde.error_reduction_metrics.v1"
ERROR_REDUCTION_METRICS_SCHEMA_VERSION = "1.0"


def validate_error_reduction_metrics_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["error_reduction_metrics_not_object"]
    errs: list[str] = []
    if body.get("schema") != ERROR_REDUCTION_METRICS_CONTRACT:
        errs.append("error_reduction_metrics_schema")
    if body.get("schema_version") != ERROR_REDUCTION_METRICS_SCHEMA_VERSION:
        errs.append("error_reduction_metrics_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("error_reduction_metrics_run_id")
    metrics = body.get("metrics")
    if not isinstance(metrics, dict):
        errs.append("error_reduction_metrics_metrics")
        return errs
    required = (
        "baseline_error_count",
        "candidate_error_count",
        "resolved_error_count",
        "error_reduction_rate",
        "net_error_delta",
    )
    for key in required:
        value = metrics.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errs.append(f"error_reduction_metrics_metric_type:{key}")
            continue
        if key.endswith("_rate"):
            num = float(value)
            if num < 0.0 or num > 1.0:
                errs.append(f"error_reduction_metrics_metric_range:{key}")
    return errs


def validate_error_reduction_metrics_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["error_reduction_metrics_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["error_reduction_metrics_json"]
    return validate_error_reduction_metrics_dict(body)

