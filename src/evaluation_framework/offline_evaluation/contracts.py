"""Contracts for offline-evaluation runtime artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

OFFLINE_EVALUATION_RUNTIME_CONTRACT = "sde.offline_evaluation_runtime.v1"
OFFLINE_EVALUATION_RUNTIME_SCHEMA_VERSION = "1.0"


def validate_offline_evaluation_runtime_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["offline_evaluation_runtime_not_object"]
    errs: list[str] = []
    if body.get("schema") != OFFLINE_EVALUATION_RUNTIME_CONTRACT:
        errs.append("offline_evaluation_runtime_schema")
    if body.get("schema_version") != OFFLINE_EVALUATION_RUNTIME_SCHEMA_VERSION:
        errs.append("offline_evaluation_runtime_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("offline_evaluation_runtime_run_id")
    status = body.get("status")
    if status not in ("ready", "degraded"):
        errs.append("offline_evaluation_runtime_status")
    checks = body.get("checks")
    if not isinstance(checks, dict):
        errs.append("offline_evaluation_runtime_checks")
    else:
        for key in ("suite_contract_valid", "summary_present", "traces_present", "checkpoint_finished"):
            if not isinstance(checks.get(key), bool):
                errs.append(f"offline_evaluation_runtime_check_type:{key}")
    return errs


def validate_offline_evaluation_runtime_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["offline_evaluation_runtime_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["offline_evaluation_runtime_json"]
    return validate_offline_evaluation_runtime_dict(body)
