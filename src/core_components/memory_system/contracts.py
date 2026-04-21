"""Contracts for memory-system artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MEMORY_SYSTEM_CONTRACT = "sde.memory_system.v1"
MEMORY_SYSTEM_SCHEMA_VERSION = "1.0"


def validate_memory_system_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["memory_system_not_object"]
    errs: list[str] = []
    if body.get("schema") != MEMORY_SYSTEM_CONTRACT:
        errs.append("memory_system_schema")
    if body.get("schema_version") != MEMORY_SYSTEM_SCHEMA_VERSION:
        errs.append("memory_system_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("memory_system_run_id")
    status = body.get("status")
    if status not in ("healthy", "degraded", "missing"):
        errs.append("memory_system_status")
    metrics = body.get("metrics")
    if not isinstance(metrics, dict):
        errs.append("memory_system_metrics")
    else:
        for key in ("retrieval_chunks", "quarantine_rows"):
            value = metrics.get(key)
            if isinstance(value, bool) or not isinstance(value, int):
                errs.append(f"memory_system_metric_type:{key}")
            elif value < 0:
                errs.append(f"memory_system_metric_range:{key}")
        quality_score = metrics.get("quality_score")
        if isinstance(quality_score, bool) or not isinstance(quality_score, (int, float)):
            errs.append("memory_system_quality_score_type")
        elif float(quality_score) < 0.0 or float(quality_score) > 1.0:
            errs.append("memory_system_quality_score_range")
    return errs


def validate_memory_system_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["memory_system_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["memory_system_json"]
    return validate_memory_system_dict(body)
