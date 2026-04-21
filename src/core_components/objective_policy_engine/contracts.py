"""Contracts for objective policy engine artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

OBJECTIVE_POLICY_ENGINE_CONTRACT = "sde.objective_policy_engine.v1"
OBJECTIVE_POLICY_ENGINE_SCHEMA_VERSION = "1.0"
_ALLOWED_MODES = {"baseline", "guarded_pipeline", "phased_pipeline"}
_ALLOWED_DECISIONS = {"allow", "defer", "deny"}


def _validate_scores(scores: Any) -> list[str]:
    if not isinstance(scores, dict):
        return ["objective_policy_engine_scores"]
    errs: list[str] = []
    for key in ("reliability", "delivery", "governance", "composite"):
        value = scores.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errs.append(f"objective_policy_engine_score_type:{key}")
            continue
        numeric = float(value)
        if numeric < 0.0 or numeric > 100.0:
            errs.append(f"objective_policy_engine_score_range:{key}")
    return errs


def _validate_policy(policy: Any) -> list[str]:
    if not isinstance(policy, dict):
        return ["objective_policy_engine_policy"]
    errs: list[str] = []
    decision = policy.get("decision")
    if decision not in _ALLOWED_DECISIONS:
        errs.append("objective_policy_engine_decision")
    for key in ("reason", "next_step"):
        value = policy.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"objective_policy_engine_policy_{key}")
    return errs


def validate_objective_policy_engine_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["objective_policy_engine_not_object"]
    errs: list[str] = []
    if body.get("schema") != OBJECTIVE_POLICY_ENGINE_CONTRACT:
        errs.append("objective_policy_engine_schema")
    if body.get("schema_version") != OBJECTIVE_POLICY_ENGINE_SCHEMA_VERSION:
        errs.append("objective_policy_engine_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("objective_policy_engine_run_id")
    mode = body.get("mode")
    if mode not in _ALLOWED_MODES:
        errs.append("objective_policy_engine_mode")
    errs.extend(_validate_scores(body.get("scores")))
    errs.extend(_validate_policy(body.get("policy")))
    return errs


def validate_objective_policy_engine_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["objective_policy_engine_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["objective_policy_engine_json"]
    return validate_objective_policy_engine_dict(body)
