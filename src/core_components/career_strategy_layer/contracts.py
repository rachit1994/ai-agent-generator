"""Contracts for career strategy layer artifacts."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

CAREER_STRATEGY_LAYER_CONTRACT = "sde.career_strategy_layer.v1"
CAREER_STRATEGY_LAYER_SCHEMA_VERSION = "1.0"
_RISK_SCORE_TOLERANCE = 1e-4
_CANONICAL_EVIDENCE_REFS = {
    "summary_ref": "summary.json",
    "review_ref": "review.json",
    "promotion_package_ref": "lifecycle/promotion_package.json",
    "career_strategy_ref": "strategy/career_strategy_layer.json",
}


def _validate_execution(execution: Any) -> list[str]:
    if not isinstance(execution, dict):
        return ["career_strategy_layer_execution"]
    errs: list[str] = []
    signals_processed = execution.get("signals_processed")
    if isinstance(signals_processed, bool) or not isinstance(signals_processed, int) or signals_processed < 0:
        errs.append("career_strategy_layer_execution_type:signals_processed")
    if not isinstance(execution.get("missing_signal_sources"), list):
        errs.append("career_strategy_layer_execution_type:missing_signal_sources")
    if not isinstance(execution.get("has_proposed_stage"), bool):
        errs.append("career_strategy_layer_execution_type:has_proposed_stage")
    return errs


def _validate_score_fields(strategy: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    for key in ("career_signal_score", "readiness_score", "risk_score"):
        value = strategy.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errs.append(f"career_strategy_layer_score_type:{key}")
            continue
        num = float(value)
        if not math.isfinite(num):
            errs.append(f"career_strategy_layer_score_finite:{key}")
            continue
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


def _validate_core_fields(body: dict[str, Any]) -> tuple[list[str], Any]:
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
    focus = body.get("focus")
    if focus not in ("promotion", "stabilization"):
        errs.append("career_strategy_layer_focus")
    horizon = body.get("horizon")
    if not isinstance(horizon, str) or not horizon.strip():
        errs.append("career_strategy_layer_horizon")
    return errs, status


def _validate_evidence(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return ["career_strategy_layer_evidence"]
    errs: list[str] = []
    for key, expected in _CANONICAL_EVIDENCE_REFS.items():
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"career_strategy_layer_evidence_{key}")
            continue
        normalized = value.strip()
        if normalized.startswith("/") or ".." in normalized.split("/") or normalized != expected:
            errs.append(f"career_strategy_layer_evidence_{key}")
    return errs


def validate_career_strategy_layer_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["career_strategy_layer_not_object"]
    errs, status = _validate_core_fields(body)
    errs.extend(_validate_execution(body.get("execution")))
    errs.extend(_validate_evidence(body.get("evidence")))
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

