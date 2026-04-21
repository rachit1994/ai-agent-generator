"""Contracts for production observability artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PRODUCTION_OBSERVABILITY_CONTRACT = "sde.production_observability.v1"
PRODUCTION_OBSERVABILITY_SCHEMA_VERSION = "1.0"


def validate_production_observability_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["production_observability_not_object"]
    errs: list[str] = []
    if body.get("schema") != PRODUCTION_OBSERVABILITY_CONTRACT:
        errs.append("production_observability_schema")
    if body.get("schema_version") != PRODUCTION_OBSERVABILITY_SCHEMA_VERSION:
        errs.append("production_observability_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("production_observability_run_id")
    mode = body.get("mode")
    if mode not in ("guarded_pipeline", "phased_pipeline", "baseline"):
        errs.append("production_observability_mode")
    status = body.get("status")
    if status not in ("healthy", "degraded", "missing"):
        errs.append("production_observability_status")
    metrics = body.get("metrics")
    if not isinstance(metrics, dict):
        errs.append("production_observability_metrics")
    else:
        for key in ("trace_rows", "orchestration_rows", "run_log_lines"):
            value = metrics.get(key)
            if isinstance(value, bool) or not isinstance(value, int):
                errs.append(f"production_observability_metric_type:{key}")
            elif value < 0:
                errs.append(f"production_observability_metric_range:{key}")
    return errs


def validate_production_observability_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["production_observability_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["production_observability_json"]
    return validate_production_observability_dict(body)
