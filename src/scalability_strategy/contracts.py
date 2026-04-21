"""Contracts for scalability strategy artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SCALABILITY_STRATEGY_CONTRACT = "sde.scalability_strategy.v1"
SCALABILITY_STRATEGY_SCHEMA_VERSION = "1.0"


def validate_scalability_strategy_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["scalability_strategy_not_object"]
    errs: list[str] = []
    if body.get("schema") != SCALABILITY_STRATEGY_CONTRACT:
        errs.append("scalability_strategy_schema")
    if body.get("schema_version") != SCALABILITY_STRATEGY_SCHEMA_VERSION:
        errs.append("scalability_strategy_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("scalability_strategy_run_id")
    mode = body.get("mode")
    if not isinstance(mode, str) or not mode.strip():
        errs.append("scalability_strategy_mode")
    status = body.get("status")
    if status not in ("scalable", "constrained"):
        errs.append("scalability_strategy_status")
    scores = body.get("scores")
    if not isinstance(scores, dict):
        errs.append("scalability_strategy_scores")
        return errs
    required = (
        "event_scaling_score",
        "memory_scaling_score",
        "replay_scaling_score",
        "multi_agent_scaling_score",
        "overall_scaling_score",
    )
    for key in required:
        value = scores.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errs.append(f"scalability_strategy_score_type:{key}")
            continue
        num = float(value)
        if num < 0.0 or num > 1.0:
            errs.append(f"scalability_strategy_score_range:{key}")
    return errs


def validate_scalability_strategy_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["scalability_strategy_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["scalability_strategy_json"]
    return validate_scalability_strategy_dict(body)

