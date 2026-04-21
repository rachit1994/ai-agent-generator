"""Contracts for runtime memory-architecture artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MEMORY_ARCHITECTURE_IN_RUNTIME_CONTRACT = "sde.memory_architecture_in_runtime.v1"
MEMORY_ARCHITECTURE_IN_RUNTIME_SCHEMA_VERSION = "1.0"


def validate_memory_architecture_in_runtime_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["memory_architecture_in_runtime_not_object"]
    errs: list[str] = []
    if body.get("schema") != MEMORY_ARCHITECTURE_IN_RUNTIME_CONTRACT:
        errs.append("memory_architecture_in_runtime_schema")
    if body.get("schema_version") != MEMORY_ARCHITECTURE_IN_RUNTIME_SCHEMA_VERSION:
        errs.append("memory_architecture_in_runtime_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("memory_architecture_in_runtime_run_id")
    status = body.get("status")
    if status not in ("healthy", "degraded", "missing"):
        errs.append("memory_architecture_in_runtime_status")
    metrics = body.get("metrics")
    if not isinstance(metrics, dict):
        errs.append("memory_architecture_in_runtime_metrics")
    else:
        for key in ("retrieval_coverage", "quality_signal", "quarantine_rate", "health_score"):
            value = metrics.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                errs.append(f"memory_architecture_in_runtime_metric_type:{key}")
                continue
            numeric = float(value)
            if numeric < 0.0 or numeric > 1.0:
                errs.append(f"memory_architecture_in_runtime_metric_range:{key}")
    return errs


def validate_memory_architecture_in_runtime_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["memory_architecture_in_runtime_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["memory_architecture_in_runtime_json"]
    return validate_memory_architecture_in_runtime_dict(body)
