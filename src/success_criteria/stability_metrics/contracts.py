"""Contracts for stability-metrics artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

STABILITY_METRICS_CONTRACT = "sde.stability_metrics.v1"
STABILITY_METRICS_SCHEMA_VERSION = "1.0"


def validate_stability_metrics_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["stability_metrics_not_object"]
    errs: list[str] = []
    if body.get("schema") != STABILITY_METRICS_CONTRACT:
        errs.append("stability_metrics_schema")
    if body.get("schema_version") != STABILITY_METRICS_SCHEMA_VERSION:
        errs.append("stability_metrics_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("stability_metrics_run_id")
    metrics = body.get("metrics")
    if not isinstance(metrics, dict):
        errs.append("stability_metrics_metrics")
        return errs
    for key in ("finalize_pass_rate", "reliability_score", "retry_pressure", "stability_score"):
        value = metrics.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errs.append(f"stability_metrics_metric_type:{key}")
            continue
        numeric = float(value)
        if numeric < 0.0 or numeric > 1.0:
            errs.append(f"stability_metrics_metric_range:{key}")
    status = body.get("status")
    if status not in ("stable", "degraded", "unstable"):
        errs.append("stability_metrics_status")
    return errs


def validate_stability_metrics_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["stability_metrics_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["stability_metrics_json"]
    return validate_stability_metrics_dict(body)
