"""Contracts for dual-control runtime evidence artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DUAL_CONTROL_CONTRACT = "sde.dual_control.v1"
DUAL_CONTROL_SCHEMA_VERSION = "1.0"


def validate_dual_control_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["dual_control_not_object"]
    errs: list[str] = []
    if body.get("schema") != DUAL_CONTROL_CONTRACT:
        errs.append("dual_control_schema")
    if body.get("schema_version") != DUAL_CONTROL_SCHEMA_VERSION:
        errs.append("dual_control_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("dual_control_run_id")
    status = body.get("status")
    if status not in ("validated", "missing_required_ack", "invalid_ack"):
        errs.append("dual_control_status")
    metrics = body.get("metrics")
    if not isinstance(metrics, dict):
        errs.append("dual_control_metrics")
    else:
        for key in ("doc_review_passed", "dual_required", "ack_present", "ack_valid", "distinct_actors"):
            if not isinstance(metrics.get(key), bool):
                errs.append(f"dual_control_metric_type:{key}")
    return errs


def validate_dual_control_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["dual_control_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["dual_control_json"]
    return validate_dual_control_dict(body)
