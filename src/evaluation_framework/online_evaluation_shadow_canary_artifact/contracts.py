"""Contracts for online evaluation shadow/canary artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ONLINE_EVALUATION_SHADOW_CANARY_CONTRACT = "sde.online_evaluation_shadow_canary.v1"
ONLINE_EVALUATION_SHADOW_CANARY_SCHEMA_VERSION = "1.0"


def validate_online_evaluation_shadow_canary_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["online_evaluation_shadow_canary_not_object"]
    errs: list[str] = []
    if body.get("schema") != ONLINE_EVALUATION_SHADOW_CANARY_CONTRACT:
        errs.append("online_evaluation_shadow_canary_schema")
    if body.get("schema_version") != ONLINE_EVALUATION_SHADOW_CANARY_SCHEMA_VERSION:
        errs.append("online_evaluation_shadow_canary_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("online_evaluation_shadow_canary_run_id")
    decision = body.get("decision")
    if decision not in ("promote", "hold"):
        errs.append("online_evaluation_shadow_canary_decision")
    metrics = body.get("metrics")
    if not isinstance(metrics, dict):
        errs.append("online_evaluation_shadow_canary_metrics")
    else:
        latency = metrics.get("latency_p95_ms")
        if isinstance(latency, bool) or not isinstance(latency, (int, float)):
            errs.append("online_evaluation_shadow_canary_latency_type")
        elif float(latency) < 0.0:
            errs.append("online_evaluation_shadow_canary_latency_range")
        pass_rate = metrics.get("finalize_pass_rate")
        if isinstance(pass_rate, bool) or not isinstance(pass_rate, (int, float)):
            errs.append("online_evaluation_shadow_canary_pass_rate_type")
        elif float(pass_rate) < 0.0 or float(pass_rate) > 1.0:
            errs.append("online_evaluation_shadow_canary_pass_rate_range")
    return errs


def validate_online_evaluation_shadow_canary_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["online_evaluation_shadow_canary_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["online_evaluation_shadow_canary_json"]
    return validate_online_evaluation_shadow_canary_dict(body)
