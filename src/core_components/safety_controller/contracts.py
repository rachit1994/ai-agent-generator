"""Contracts for safety-controller runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SAFETY_CONTROLLER_CONTRACT = "sde.safety_controller.v1"
SAFETY_CONTROLLER_SCHEMA_VERSION = "1.0"


def validate_safety_controller_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["safety_controller_not_object"]
    errs: list[str] = []
    if body.get("schema") != SAFETY_CONTROLLER_CONTRACT:
        errs.append("safety_controller_schema")
    if body.get("schema_version") != SAFETY_CONTROLLER_SCHEMA_VERSION:
        errs.append("safety_controller_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("safety_controller_run_id")
    status = body.get("status")
    if status not in ("allow", "block"):
        errs.append("safety_controller_status")
    metrics = body.get("metrics")
    if not isinstance(metrics, dict):
        errs.append("safety_controller_metrics")
    else:
        for key in ("hard_stop_failures", "validation_ready", "policy_bundle_valid"):
            if not isinstance(metrics.get(key), bool):
                errs.append(f"safety_controller_metric_type:{key}")
    return errs


def validate_safety_controller_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["safety_controller_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["safety_controller_json"]
    return validate_safety_controller_dict(body)
