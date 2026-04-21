"""Contracts for career strategy layer artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CAREER_STRATEGY_LAYER_CONTRACT = "sde.career_strategy_layer.v1"
CAREER_STRATEGY_LAYER_SCHEMA_VERSION = "1.0"


def validate_career_strategy_layer_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["career_strategy_layer_not_object"]
    errs: list[str] = []
    if body.get("schema") != CAREER_STRATEGY_LAYER_CONTRACT:
        errs.append("career_strategy_layer_schema")
    if body.get("schema_version") != CAREER_STRATEGY_LAYER_SCHEMA_VERSION:
        errs.append("career_strategy_layer_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("career_strategy_layer_run_id")
    mode = body.get("mode")
    if not isinstance(mode, str) or not mode.strip():
        errs.append("career_strategy_layer_mode")
    status = body.get("status")
    if status not in ("ready", "watchlist", "hold"):
        errs.append("career_strategy_layer_status")
    strategy = body.get("strategy")
    if not isinstance(strategy, dict):
        errs.append("career_strategy_layer_strategy")
        return errs
    for key in ("career_signal_score", "readiness_score", "risk_score"):
        value = strategy.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errs.append(f"career_strategy_layer_score_type:{key}")
            continue
        num = float(value)
        if num < 0.0 or num > 1.0:
            errs.append(f"career_strategy_layer_score_range:{key}")
    return errs


def validate_career_strategy_layer_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["career_strategy_layer_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["career_strategy_layer_json"]
    return validate_career_strategy_layer_dict(body)

