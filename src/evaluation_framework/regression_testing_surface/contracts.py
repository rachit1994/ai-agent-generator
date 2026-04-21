"""Contracts for regression-testing-surface runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REGRESSION_TESTING_SURFACE_CONTRACT = "sde.regression_testing_surface.v1"
REGRESSION_TESTING_SURFACE_SCHEMA_VERSION = "1.0"


def validate_regression_testing_surface_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["regression_testing_surface_not_object"]
    errs: list[str] = []
    if body.get("schema") != REGRESSION_TESTING_SURFACE_CONTRACT:
        errs.append("regression_testing_surface_schema")
    if body.get("schema_version") != REGRESSION_TESTING_SURFACE_SCHEMA_VERSION:
        errs.append("regression_testing_surface_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("regression_testing_surface_run_id")
    status = body.get("status")
    if status not in ("ready", "degraded"):
        errs.append("regression_testing_surface_status")
    metrics = body.get("metrics")
    if not isinstance(metrics, dict):
        errs.append("regression_testing_surface_metrics")
    else:
        for key in ("anchor_validation_passed", "has_promotion_eval", "has_online_eval", "has_eval_summary"):
            if not isinstance(metrics.get(key), bool):
                errs.append(f"regression_testing_surface_metric_type:{key}")
    return errs


def validate_regression_testing_surface_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["regression_testing_surface_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["regression_testing_surface_json"]
    return validate_regression_testing_surface_dict(body)
