"""Contracts for traces JSONL event-row runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

TRACES_JSONL_EVENT_ROW_RUNTIME_CONTRACT = "sde.traces_jsonl_event_row_runtime.v1"
TRACES_JSONL_EVENT_ROW_RUNTIME_SCHEMA_VERSION = "1.0"


def _validate_top_level(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    if body.get("schema") != TRACES_JSONL_EVENT_ROW_RUNTIME_CONTRACT:
        errs.append("traces_jsonl_event_row_runtime_schema")
    if body.get("schema_version") != TRACES_JSONL_EVENT_ROW_RUNTIME_SCHEMA_VERSION:
        errs.append("traces_jsonl_event_row_runtime_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("traces_jsonl_event_row_runtime_run_id")
    if body.get("status") not in ("ready", "degraded"):
        errs.append("traces_jsonl_event_row_runtime_status")
    return errs


def _validate_checks(status: Any, checks: Any) -> list[str]:
    if not isinstance(checks, dict):
        return ["traces_jsonl_event_row_runtime_checks"]
    errs: list[str] = []
    for key in ("all_rows_valid", "run_id_consistent"):
        if not isinstance(checks.get(key), bool):
            errs.append(f"traces_jsonl_event_row_runtime_check_type:{key}")
    if errs:
        return errs
    expected_status = (
        "ready"
        if checks.get("all_rows_valid") is True and checks.get("run_id_consistent") is True
        else "degraded"
    )
    if status != expected_status:
        errs.append("traces_jsonl_event_row_runtime_status_checks_mismatch")
    return errs


def _validate_counts(status: Any, checks: Any, counts: Any) -> list[str]:
    if not isinstance(counts, dict):
        return ["traces_jsonl_event_row_runtime_counts"]
    row_count = counts.get("row_count")
    if isinstance(row_count, bool) or not isinstance(row_count, int):
        return ["traces_jsonl_event_row_runtime_row_count_type"]
    if row_count < 0:
        return ["traces_jsonl_event_row_runtime_row_count_range"]
    if (
        status == "ready"
        and isinstance(checks, dict)
        and checks.get("all_rows_valid") is True
        and checks.get("run_id_consistent") is True
        and row_count == 0
    ):
        return ["traces_jsonl_event_row_runtime_status_counts_mismatch"]
    return []


def validate_traces_jsonl_event_row_runtime_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["traces_jsonl_event_row_runtime_not_object"]
    errs = _validate_top_level(body)
    status = body.get("status")
    checks = body.get("checks")
    errs.extend(_validate_checks(status, checks))
    errs.extend(_validate_counts(status, checks, body.get("counts")))
    return errs


def validate_traces_jsonl_event_row_runtime_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["traces_jsonl_event_row_runtime_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["traces_jsonl_event_row_runtime_json"]
    return validate_traces_jsonl_event_row_runtime_dict(body)
