"""Contracts for retry/repeat-profile runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RETRY_REPEAT_PROFILE_RUNTIME_CONTRACT = "sde.retry_repeat_profile_runtime.v1"
RETRY_REPEAT_PROFILE_RUNTIME_SCHEMA_VERSION = "1.0"


def validate_retry_repeat_profile_runtime_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["retry_repeat_profile_runtime_not_object"]
    errs: list[str] = []
    if body.get("schema") != RETRY_REPEAT_PROFILE_RUNTIME_CONTRACT:
        errs.append("retry_repeat_profile_runtime_schema")
    if body.get("schema_version") != RETRY_REPEAT_PROFILE_RUNTIME_SCHEMA_VERSION:
        errs.append("retry_repeat_profile_runtime_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("retry_repeat_profile_runtime_run_id")
    repeat = body.get("repeat")
    if isinstance(repeat, bool) or not isinstance(repeat, int) or repeat < 1:
        errs.append("retry_repeat_profile_runtime_repeat")
    status = body.get("status")
    if status not in ("single", "repeat_ok", "repeat_degraded"):
        errs.append("retry_repeat_profile_runtime_status")
    metrics = body.get("metrics")
    if not isinstance(metrics, dict):
        errs.append("retry_repeat_profile_runtime_metrics")
    else:
        for key in ("all_runs_no_pipeline_error", "validation_ready_all"):
            if not isinstance(metrics.get(key), bool):
                errs.append(f"retry_repeat_profile_runtime_metric_type:{key}")
        attempt_count = metrics.get("attempt_count")
        if isinstance(attempt_count, bool) or not isinstance(attempt_count, int) or attempt_count < 1:
            errs.append("retry_repeat_profile_runtime_attempt_count")
    return errs


def validate_retry_repeat_profile_runtime_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["retry_repeat_profile_runtime_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["retry_repeat_profile_runtime_json"]
    return validate_retry_repeat_profile_runtime_dict(body)
