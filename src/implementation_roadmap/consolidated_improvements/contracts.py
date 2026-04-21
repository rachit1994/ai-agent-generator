"""Contracts for consolidated improvements artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONSOLIDATED_IMPROVEMENTS_CONTRACT = "sde.consolidated_improvements.v1"
CONSOLIDATED_IMPROVEMENTS_SCHEMA_VERSION = "1.0"


def validate_consolidated_improvements_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["consolidated_improvements_not_object"]
    errs: list[str] = []
    if body.get("schema") != CONSOLIDATED_IMPROVEMENTS_CONTRACT:
        errs.append("consolidated_improvements_schema")
    if body.get("schema_version") != CONSOLIDATED_IMPROVEMENTS_SCHEMA_VERSION:
        errs.append("consolidated_improvements_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("consolidated_improvements_run_id")
    mode = body.get("mode")
    if not isinstance(mode, str) or not mode.strip():
        errs.append("consolidated_improvements_mode")
    status = body.get("status")
    if status not in ("ready", "not_ready"):
        errs.append("consolidated_improvements_status")
    summary = body.get("summary")
    if not isinstance(summary, dict):
        errs.append("consolidated_improvements_summary")
        return errs
    score = summary.get("consolidation_score")
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        errs.append("consolidated_improvements_consolidation_score_type")
    elif float(score) < 0.0 or float(score) > 1.0:
        errs.append("consolidated_improvements_consolidation_score_range")
    return errs


def validate_consolidated_improvements_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["consolidated_improvements_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["consolidated_improvements_json"]
    return validate_consolidated_improvements_dict(body)

