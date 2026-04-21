"""Contracts for transfer learning metrics artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

TRANSFER_LEARNING_METRICS_CONTRACT = "sde.transfer_learning_metrics.v1"
TRANSFER_LEARNING_METRICS_SCHEMA_VERSION = "1.0"


def validate_transfer_learning_metrics_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["transfer_learning_metrics_not_object"]
    errs: list[str] = []
    if body.get("schema") != TRANSFER_LEARNING_METRICS_CONTRACT:
        errs.append("transfer_learning_metrics_schema")
    if body.get("schema_version") != TRANSFER_LEARNING_METRICS_SCHEMA_VERSION:
        errs.append("transfer_learning_metrics_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("transfer_learning_metrics_run_id")
    metrics = body.get("metrics")
    if not isinstance(metrics, dict):
        errs.append("transfer_learning_metrics_metrics")
        return errs
    required = (
        "transfer_gain_rate",
        "negative_transfer_rate",
        "retained_success_rate",
        "net_transfer_points",
        "transfer_efficiency_score",
    )
    for key in required:
        value = metrics.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errs.append(f"transfer_learning_metrics_metric_type:{key}")
            continue
        if key.endswith("_rate") or key.endswith("_score"):
            if float(value) < 0.0 or float(value) > 1.0:
                errs.append(f"transfer_learning_metrics_metric_range:{key}")
    return errs


def validate_transfer_learning_metrics_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["transfer_learning_metrics_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["transfer_learning_metrics_json"]
    return validate_transfer_learning_metrics_dict(body)

