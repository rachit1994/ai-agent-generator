"""Contracts for full build order progression artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

FULL_BUILD_ORDER_PROGRESSION_CONTRACT = "sde.full_build_order_progression.v1"
FULL_BUILD_ORDER_PROGRESSION_SCHEMA_VERSION = "1.0"
_ALLOWED_MODES = {"baseline", "guarded_pipeline", "phased_pipeline"}
_ALLOWED_STATUS = {"ordered", "out_of_order", "incomplete"}


def validate_full_build_order_progression_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["full_build_order_progression_not_object"]
    errs: list[str] = []
    if body.get("schema") != FULL_BUILD_ORDER_PROGRESSION_CONTRACT:
        errs.append("full_build_order_progression_schema")
    if body.get("schema_version") != FULL_BUILD_ORDER_PROGRESSION_SCHEMA_VERSION:
        errs.append("full_build_order_progression_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("full_build_order_progression_run_id")
    mode = body.get("mode")
    if mode not in _ALLOWED_MODES:
        errs.append("full_build_order_progression_mode")
    status = body.get("status")
    if status not in _ALLOWED_STATUS:
        errs.append("full_build_order_progression_status")
    sequence = body.get("stage_sequence")
    if not isinstance(sequence, list) or any(not isinstance(row, str) or not row.strip() for row in sequence):
        errs.append("full_build_order_progression_stage_sequence")
    checks = body.get("checks")
    if not isinstance(checks, dict):
        errs.append("full_build_order_progression_checks")
    else:
        for key in (
            "all_stages_known",
            "starts_with_allowed_entry_stage",
            "ends_with_finalize",
            "monotonic_progression",
            "required_stages_present",
        ):
            if not isinstance(checks.get(key), bool):
                errs.append(f"full_build_order_progression_check_type:{key}")
    summary = body.get("summary")
    if not isinstance(summary, dict):
        errs.append("full_build_order_progression_summary")
    else:
        score = summary.get("order_score")
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            errs.append("full_build_order_progression_order_score_type")
        elif float(score) < 0.0 or float(score) > 1.0:
            errs.append("full_build_order_progression_order_score_range")
    return errs


def validate_full_build_order_progression_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["full_build_order_progression_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["full_build_order_progression_json"]
    return validate_full_build_order_progression_dict(body)

