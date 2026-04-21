"""Contracts for role-agents artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROLE_AGENTS_CONTRACT = "sde.role_agents.v1"
ROLE_AGENTS_SCHEMA_VERSION = "1.0"


def validate_role_agents_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["role_agents_not_object"]
    errs: list[str] = []
    if body.get("schema") != ROLE_AGENTS_CONTRACT:
        errs.append("role_agents_schema")
    if body.get("schema_version") != ROLE_AGENTS_SCHEMA_VERSION:
        errs.append("role_agents_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("role_agents_run_id")
    role_scores = body.get("role_scores")
    if not isinstance(role_scores, dict):
        errs.append("role_agents_role_scores")
    else:
        for key in ("planner", "implementor", "verifier"):
            value = role_scores.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                errs.append(f"role_agents_score_type:{key}")
                continue
            numeric = float(value)
            if numeric < 0.0 or numeric > 1.0:
                errs.append(f"role_agents_score_range:{key}")
    status = body.get("status")
    if status not in ("balanced", "drifted", "insufficient_signal"):
        errs.append("role_agents_status")
    return errs


def validate_role_agents_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["role_agents_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["role_agents_json"]
    return validate_role_agents_dict(body)
