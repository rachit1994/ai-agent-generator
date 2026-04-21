"""Contracts for core-observability component runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

OBSERVABILITY_COMPONENT_CONTRACT = "sde.observability_component.v1"
OBSERVABILITY_COMPONENT_SCHEMA_VERSION = "1.0"


def validate_observability_component_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["observability_component_not_object"]
    errs: list[str] = []
    if body.get("schema") != OBSERVABILITY_COMPONENT_CONTRACT:
        errs.append("observability_component_schema")
    if body.get("schema_version") != OBSERVABILITY_COMPONENT_SCHEMA_VERSION:
        errs.append("observability_component_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("observability_component_run_id")
    status = body.get("status")
    if status not in ("ready", "degraded"):
        errs.append("observability_component_status")
    metrics = body.get("metrics")
    if not isinstance(metrics, dict):
        errs.append("observability_component_metrics")
    else:
        for key in (
            "has_production_observability",
            "has_run_log",
            "has_traces",
            "has_orchestration_log",
            "all_checks_passed",
        ):
            if not isinstance(metrics.get(key), bool):
                errs.append(f"observability_component_metric_type:{key}")
    return errs


def validate_observability_component_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["observability_component_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["observability_component_json"]
    return validate_observability_component_dict(body)
