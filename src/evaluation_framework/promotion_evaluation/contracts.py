"""Contracts for promotion-evaluation artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROMOTION_EVALUATION_CONTRACT = "sde.promotion_evaluation.v1"
PROMOTION_EVALUATION_SCHEMA_VERSION = "1.0"


def validate_promotion_evaluation_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["promotion_evaluation_not_object"]
    errs: list[str] = []
    if body.get("schema") != PROMOTION_EVALUATION_CONTRACT:
        errs.append("promotion_evaluation_schema")
    if body.get("schema_version") != PROMOTION_EVALUATION_SCHEMA_VERSION:
        errs.append("promotion_evaluation_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("promotion_evaluation_run_id")
    decision = body.get("decision")
    if decision not in ("promote", "hold"):
        errs.append("promotion_evaluation_decision")
    confidence = body.get("confidence")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        errs.append("promotion_evaluation_confidence_type")
    elif float(confidence) < 0.0 or float(confidence) > 1.0:
        errs.append("promotion_evaluation_confidence_range")
    return errs


def validate_promotion_evaluation_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["promotion_evaluation_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["promotion_evaluation_json"]
    return validate_promotion_evaluation_dict(body)
