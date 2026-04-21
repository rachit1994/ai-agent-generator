"""Contracts for local-runtime deterministic CLI spine artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

LOCAL_RUNTIME_SPINE_CONTRACT = "sde.local_runtime_spine.v1"
LOCAL_RUNTIME_SPINE_SCHEMA_VERSION = "1.0"


def validate_local_runtime_spine_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["local_runtime_spine_not_object"]
    errs: list[str] = []
    if body.get("schema") != LOCAL_RUNTIME_SPINE_CONTRACT:
        errs.append("local_runtime_spine_schema")
    if body.get("schema_version") != LOCAL_RUNTIME_SPINE_SCHEMA_VERSION:
        errs.append("local_runtime_spine_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("local_runtime_spine_run_id")
    mode = body.get("mode")
    if mode not in ("baseline", "guarded_pipeline", "phased_pipeline"):
        errs.append("local_runtime_spine_mode")
    status = body.get("status")
    if status not in ("ready", "degraded"):
        errs.append("local_runtime_spine_status")
    checks = body.get("checks")
    if not isinstance(checks, dict):
        errs.append("local_runtime_spine_checks")
    else:
        for key in ("has_run_manifest", "has_orchestration", "has_traces"):
            if not isinstance(checks.get(key), bool):
                errs.append(f"local_runtime_spine_check_type:{key}")
    return errs


def validate_local_runtime_spine_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["local_runtime_spine_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["local_runtime_spine_json"]
    return validate_local_runtime_spine_dict(body)
