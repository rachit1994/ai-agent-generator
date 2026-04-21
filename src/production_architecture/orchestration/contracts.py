"""Contracts for production orchestration artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PRODUCTION_ORCHESTRATION_CONTRACT = "sde.production_orchestration.v1"
PRODUCTION_ORCHESTRATION_SCHEMA_VERSION = "1.0"


def validate_production_orchestration_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["production_orchestration_not_object"]
    errs: list[str] = []
    if body.get("schema") != PRODUCTION_ORCHESTRATION_CONTRACT:
        errs.append("production_orchestration_schema")
    if body.get("schema_version") != PRODUCTION_ORCHESTRATION_SCHEMA_VERSION:
        errs.append("production_orchestration_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("production_orchestration_run_id")
    status = body.get("status")
    if status not in ("healthy", "degraded", "missing"):
        errs.append("production_orchestration_status")
    metrics = body.get("metrics")
    if not isinstance(metrics, dict):
        errs.append("production_orchestration_metrics")
    else:
        for key in ("lease_count", "active_lease_count", "shard_count"):
            value = metrics.get(key)
            if isinstance(value, bool) or not isinstance(value, int):
                errs.append(f"production_orchestration_metric_type:{key}")
            elif value < 0:
                errs.append(f"production_orchestration_metric_range:{key}")
    return errs


def validate_production_orchestration_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["production_orchestration_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["production_orchestration_json"]
    return validate_production_orchestration_dict(body)
