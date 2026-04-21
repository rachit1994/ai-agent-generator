"""Contracts for orchestration stage-event runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ORCHESTRATION_STAGE_EVENT_RUNTIME_CONTRACT = "sde.orchestration_stage_event_runtime.v1"
ORCHESTRATION_STAGE_EVENT_RUNTIME_SCHEMA_VERSION = "1.0"


def validate_orchestration_stage_event_runtime_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["orchestration_stage_event_runtime_not_object"]
    errs: list[str] = []
    if body.get("schema") != ORCHESTRATION_STAGE_EVENT_RUNTIME_CONTRACT:
        errs.append("orchestration_stage_event_runtime_schema")
    if body.get("schema_version") != ORCHESTRATION_STAGE_EVENT_RUNTIME_SCHEMA_VERSION:
        errs.append("orchestration_stage_event_runtime_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("orchestration_stage_event_runtime_run_id")
    status = body.get("status")
    if status not in ("ready", "degraded"):
        errs.append("orchestration_stage_event_runtime_status")
    checks = body.get("checks")
    if not isinstance(checks, dict):
        errs.append("orchestration_stage_event_runtime_checks")
    else:
        for key in ("has_stage_event_lines", "all_stage_event_lines_valid"):
            if not isinstance(checks.get(key), bool):
                errs.append(f"orchestration_stage_event_runtime_check_type:{key}")
    return errs


def validate_orchestration_stage_event_runtime_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["orchestration_stage_event_runtime_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["orchestration_stage_event_runtime_json"]
    return validate_orchestration_stage_event_runtime_dict(body)
