"""Contracts for capability growth metrics artifacts."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

CAPABILITY_GROWTH_METRICS_CONTRACT = "sde.capability_growth_metrics.v1"
CAPABILITY_GROWTH_METRICS_SCHEMA_VERSION = "1.0"


def validate_capability_growth_metrics_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["capability_growth_metrics_not_object"]
    errs: list[str] = []
    if body.get("schema") != CAPABILITY_GROWTH_METRICS_CONTRACT:
        errs.append("capability_growth_metrics_schema")
    if body.get("schema_version") != CAPABILITY_GROWTH_METRICS_SCHEMA_VERSION:
        errs.append("capability_growth_metrics_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("capability_growth_metrics_run_id")
    metrics = body.get("metrics")
    if not isinstance(metrics, dict):
        errs.append("capability_growth_metrics_metrics")
        return errs
    required = (
        "capability_growth_rate",
        "capability_stability_rate",
        "promotion_readiness_delta",
        "growth_confidence",
    )
    for key in required:
        value = metrics.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errs.append(f"capability_growth_metrics_metric_type:{key}")
            continue
        num = float(value)
        if not math.isfinite(num):
            errs.append(f"capability_growth_metrics_metric_non_finite:{key}")
            continue
        if key == "promotion_readiness_delta":
            if num < -1.0 or num > 1.0:
                errs.append(f"capability_growth_metrics_metric_range:{key}")
        elif num < 0.0 or num > 1.0:
            errs.append(f"capability_growth_metrics_metric_range:{key}")
    return errs


def validate_capability_growth_metrics_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["capability_growth_metrics_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["capability_growth_metrics_json"]
    return validate_capability_growth_metrics_dict(body)

