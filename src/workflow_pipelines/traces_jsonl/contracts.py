"""Contracts for traces JSONL event-row runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

TRACES_JSONL_EVENT_ROW_RUNTIME_CONTRACT = "sde.traces_jsonl_event_row_runtime.v1"
TRACES_JSONL_EVENT_ROW_RUNTIME_SCHEMA_VERSION = "1.0"


def validate_traces_jsonl_event_row_runtime_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["traces_jsonl_event_row_runtime_not_object"]
    errs: list[str] = []
    if body.get("schema") != TRACES_JSONL_EVENT_ROW_RUNTIME_CONTRACT:
        errs.append("traces_jsonl_event_row_runtime_schema")
    if body.get("schema_version") != TRACES_JSONL_EVENT_ROW_RUNTIME_SCHEMA_VERSION:
        errs.append("traces_jsonl_event_row_runtime_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("traces_jsonl_event_row_runtime_run_id")
    status = body.get("status")
    if status not in ("ready", "degraded"):
        errs.append("traces_jsonl_event_row_runtime_status")
    checks = body.get("checks")
    if not isinstance(checks, dict):
        errs.append("traces_jsonl_event_row_runtime_checks")
    else:
        for key in ("all_rows_valid", "run_id_consistent"):
            if not isinstance(checks.get(key), bool):
                errs.append(f"traces_jsonl_event_row_runtime_check_type:{key}")
    return errs


def validate_traces_jsonl_event_row_runtime_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["traces_jsonl_event_row_runtime_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["traces_jsonl_event_row_runtime_json"]
    return validate_traces_jsonl_event_row_runtime_dict(body)
