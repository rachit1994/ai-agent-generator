"""Contracts for learning-service artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

LEARNING_SERVICE_CONTRACT = "sde.learning_service.v1"
LEARNING_SERVICE_SCHEMA_VERSION = "1.0"


def validate_learning_service_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["learning_service_not_object"]
    errs: list[str] = []
    if body.get("schema") != LEARNING_SERVICE_CONTRACT:
        errs.append("learning_service_schema")
    if body.get("schema_version") != LEARNING_SERVICE_SCHEMA_VERSION:
        errs.append("learning_service_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("learning_service_run_id")
    mode = body.get("mode")
    if mode not in ("guarded_pipeline", "phased_pipeline", "baseline"):
        errs.append("learning_service_mode")
    status = body.get("status")
    if status not in ("healthy", "degraded", "insufficient_signal"):
        errs.append("learning_service_status")
    metrics = body.get("metrics")
    if not isinstance(metrics, dict):
        errs.append("learning_service_metrics")
    else:
        for key in ("reflection_count", "canary_count", "finalize_rows"):
            value = metrics.get(key)
            if isinstance(value, bool) or not isinstance(value, int):
                errs.append(f"learning_service_metric_type:{key}")
            elif value < 0:
                errs.append(f"learning_service_metric_range:{key}")
        health = metrics.get("health_score")
        if isinstance(health, bool) or not isinstance(health, (int, float)):
            errs.append("learning_service_health_score_type")
        elif float(health) < 0.0 or float(health) > 1.0:
            errs.append("learning_service_health_score_range")
    return errs


def validate_learning_service_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["learning_service_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["learning_service_json"]
    return validate_learning_service_dict(body)
