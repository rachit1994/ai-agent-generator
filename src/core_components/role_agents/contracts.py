"""Contracts for role-agents artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROLE_AGENTS_CONTRACT = "sde.role_agents.v1"
ROLE_AGENTS_SCHEMA_VERSION = "1.0"
_DRIFT_THRESHOLD = 0.35
_FLOAT_TOLERANCE = 1e-9


def validate_role_agents_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["role_agents_not_object"]
    errs = _validate_core_fields(body)
    role_scores = body.get("role_scores")
    errs.extend(_validate_role_scores(role_scores))
    status = body.get("status")
    errs.extend(_validate_status(status))
    if not errs and isinstance(role_scores, dict):
        errs.extend(_validate_status_semantics(status, role_scores))
    return errs


def _validate_core_fields(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    if body.get("schema") != ROLE_AGENTS_CONTRACT:
        errs.append("role_agents_schema")
    if body.get("schema_version") != ROLE_AGENTS_SCHEMA_VERSION:
        errs.append("role_agents_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("role_agents_run_id")
    return errs


def _validate_role_scores(role_scores: Any) -> list[str]:
    if not isinstance(role_scores, dict):
        return ["role_agents_role_scores"]
    errs: list[str] = []
    for key in ("planner", "implementor", "verifier"):
        value = role_scores.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errs.append(f"role_agents_score_type:{key}")
            continue
        numeric = float(value)
        if numeric < 0.0 or numeric > 1.0:
            errs.append(f"role_agents_score_range:{key}")
    return errs


def _validate_status(status: Any) -> list[str]:
    if status not in ("balanced", "drifted", "insufficient_signal"):
        return ["role_agents_status"]
    return []


def _validate_status_semantics(status: Any, role_scores: dict[str, Any]) -> list[str]:
    scores = _coerce_scores(role_scores)
    if status not in ("balanced", "drifted", "insufficient_signal") or scores is None:
        return []
    spread = max(scores) - min(scores)
    errs: list[str] = []
    errs.extend(_validate_drifted_status(status, spread))
    errs.extend(_validate_balanced_status(status, spread))
    errs.extend(_validate_insufficient_signal_status(status, scores))
    return errs


def _coerce_scores(role_scores: dict[str, Any]) -> tuple[float, float, float] | None:
    planner = role_scores.get("planner")
    implementor = role_scores.get("implementor")
    verifier = role_scores.get("verifier")
    if isinstance(planner, bool) or not isinstance(planner, (int, float)):
        return None
    if isinstance(implementor, bool) or not isinstance(implementor, (int, float)):
        return None
    if isinstance(verifier, bool) or not isinstance(verifier, (int, float)):
        return None
    return float(planner), float(implementor), float(verifier)


def _validate_drifted_status(status: Any, spread: float) -> list[str]:
    if status == "drifted" and spread <= _DRIFT_THRESHOLD + _FLOAT_TOLERANCE:
        return ["role_agents_status_semantics:drifted"]
    return []


def _validate_balanced_status(status: Any, spread: float) -> list[str]:
    if status == "balanced" and spread > _DRIFT_THRESHOLD + _FLOAT_TOLERANCE:
        return ["role_agents_status_semantics:balanced"]
    return []


def _validate_insufficient_signal_status(status: Any, scores: tuple[float, float, float]) -> list[str]:
    planner, implementor, _ = scores
    if status == "insufficient_signal" and (
        abs(planner) > _FLOAT_TOLERANCE or abs(implementor) > _FLOAT_TOLERANCE
    ):
        return ["role_agents_status_semantics:insufficient_signal"]
    return []


def validate_role_agents_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["role_agents_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["role_agents_json"]
    return validate_role_agents_dict(body)
