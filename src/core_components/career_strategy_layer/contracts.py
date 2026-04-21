"""Contracts for career strategy layer artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CAREER_STRATEGY_LAYER_CONTRACT = "sde.career_strategy_layer.v1"
CAREER_STRATEGY_LAYER_SCHEMA_VERSION = "1.0"
_RISK_SCORE_TOLERANCE = 1e-4


def _validate_score_fields(strategy: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    for key in ("career_signal_score", "readiness_score", "risk_score"):
        value = strategy.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errs.append(f"career_strategy_layer_score_type:{key}")
            continue
        num = float(value)
        if num < 0.0 or num > 1.0:
            errs.append(f"career_strategy_layer_score_range:{key}")
    return errs


def _validate_strategy_fields(strategy: dict[str, Any]) -> list[str]:
    errs = _validate_score_fields(strategy)
    if strategy.get("priority") not in ("advance", "stabilize"):
        errs.append("career_strategy_layer_priority")
    recommended_actions = strategy.get("recommended_actions")
    if not isinstance(recommended_actions, list) or not recommended_actions:
        errs.append("career_strategy_layer_recommended_actions")
        return errs
    for action in recommended_actions:
        if not isinstance(action, str) or not action.strip():
            errs.append("career_strategy_layer_recommended_actions_item")
            break
    return errs


def _validate_status_strategy_semantics(status: Any, strategy: Any) -> list[str]:
    if status not in ("ready", "watchlist", "hold") or not isinstance(strategy, dict):
        return []
    readiness_score = strategy.get("readiness_score")
    risk_score = strategy.get("risk_score")
    priority = strategy.get("priority")
    if (
        isinstance(readiness_score, bool)
        or not isinstance(readiness_score, (int, float))
        or isinstance(risk_score, bool)
        or not isinstance(risk_score, (int, float))
        or priority not in ("advance", "stabilize")
    ):
        return []
    readiness = float(readiness_score)
    risk = float(risk_score)
    errs: list[str] = []
    if abs((1.0 - readiness) - risk) > _RISK_SCORE_TOLERANCE:
        errs.append("career_strategy_layer_risk_readiness_mismatch")
    if status == "ready" and priority != "advance":
        errs.append("career_strategy_layer_status_priority_mismatch")
    if status in ("watchlist", "hold") and priority != "stabilize":
        errs.append("career_strategy_layer_status_priority_mismatch")
    errs.extend(_validate_status_readiness_semantics(status, readiness))
    return errs


def _validate_status_readiness_semantics(status: Any, readiness: float) -> list[str]:
    if status == "ready" and readiness < 0.75:
        return ["career_strategy_layer_status_readiness_mismatch"]
    if status == "hold" and readiness >= 0.55:
        return ["career_strategy_layer_status_readiness_mismatch"]
    if status == "watchlist" and (readiness < 0.55 or readiness >= 0.75):
        return ["career_strategy_layer_status_readiness_mismatch"]
    return []


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
    errs.extend(_validate_strategy_fields(strategy))
    if not errs:
        errs.extend(_validate_status_strategy_semantics(status, strategy))
    return errs


def validate_career_strategy_layer_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["career_strategy_layer_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["career_strategy_layer_json"]
    return validate_career_strategy_layer_dict(body)

