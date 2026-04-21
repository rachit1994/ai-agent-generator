"""Contracts for event-store semantics artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

EVENT_STORE_SEMANTICS_CONTRACT = "sde.event_store_semantics.v1"
EVENT_STORE_SEMANTICS_SCHEMA_VERSION = "1.0"


def validate_event_store_semantics_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["event_store_semantics_not_object"]
    errs: list[str] = []
    if body.get("schema") != EVENT_STORE_SEMANTICS_CONTRACT:
        errs.append("event_store_semantics_schema")
    if body.get("schema_version") != EVENT_STORE_SEMANTICS_SCHEMA_VERSION:
        errs.append("event_store_semantics_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("event_store_semantics_run_id")
    status = body.get("status")
    if status not in ("aligned", "partial", "broken"):
        errs.append("event_store_semantics_status")
    metrics = body.get("metrics")
    if not isinstance(metrics, dict):
        errs.append("event_store_semantics_metrics")
    else:
        for key in ("event_count", "trace_count"):
            value = metrics.get(key)
            if isinstance(value, bool) or not isinstance(value, int):
                errs.append(f"event_store_semantics_metric_type:{key}")
            elif value < 0:
                errs.append(f"event_store_semantics_metric_range:{key}")
        coverage = metrics.get("coverage")
        if isinstance(coverage, bool) or not isinstance(coverage, (int, float)):
            errs.append("event_store_semantics_coverage_type")
        elif float(coverage) < 0.0 or float(coverage) > 1.0:
            errs.append("event_store_semantics_coverage_range")
    return errs


def validate_event_store_semantics_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["event_store_semantics_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["event_store_semantics_json"]
    return validate_event_store_semantics_dict(body)
