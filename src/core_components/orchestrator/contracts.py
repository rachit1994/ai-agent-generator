"""Contracts for core-orchestrator runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ORCHESTRATOR_COMPONENT_CONTRACT = "sde.orchestrator_component.v1"
ORCHESTRATOR_COMPONENT_SCHEMA_VERSION = "1.0"


def validate_orchestrator_component_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["orchestrator_component_not_object"]
    errs: list[str] = []
    if body.get("schema") != ORCHESTRATOR_COMPONENT_CONTRACT:
        errs.append("orchestrator_component_schema")
    if body.get("schema_version") != ORCHESTRATOR_COMPONENT_SCHEMA_VERSION:
        errs.append("orchestrator_component_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("orchestrator_component_run_id")
    status = body.get("status")
    if status not in ("ready", "degraded"):
        errs.append("orchestrator_component_status")
    metrics = body.get("metrics")
    if not isinstance(metrics, dict):
        errs.append("orchestrator_component_metrics")
    else:
        for key in ("has_run_manifest", "has_run_manifest_runtime", "has_traces", "has_orchestration_log"):
            if not isinstance(metrics.get(key), bool):
                errs.append(f"orchestrator_component_metric_type:{key}")
    return errs


def validate_orchestrator_component_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["orchestrator_component_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["orchestrator_component_json"]
    return validate_orchestrator_component_dict(body)
