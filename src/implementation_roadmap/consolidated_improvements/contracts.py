"""Contracts for consolidated improvements artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONSOLIDATED_IMPROVEMENTS_CONTRACT = "sde.consolidated_improvements.v1"
CONSOLIDATED_IMPROVEMENTS_SCHEMA_VERSION = "1.0"


def _validate_summary_score(summary: dict[str, Any]) -> list[str]:
    score = summary.get("consolidation_score")
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        return ["consolidated_improvements_consolidation_score_type"]
    if float(score) < 0.0 or float(score) > 1.0:
        return ["consolidated_improvements_consolidation_score_range"]
    return []


def _validate_summary_booleans(summary: dict[str, Any]) -> tuple[list[str], dict[str, bool] | None]:
    errs: list[str] = []
    values: dict[str, bool] = {}
    for key in ("validation_ready", "review_passed", "required_artifacts_present"):
        value = summary.get(key)
        if not isinstance(value, bool):
            errs.append(f"consolidated_improvements_summary_bool_type:{key}")
            continue
        values[key] = value
    if errs:
        return (errs, None)
    return ([], values)


def _validate_summary_counts(summary: dict[str, Any]) -> tuple[list[str], tuple[int, int] | None]:
    errs: list[str] = []
    improvements_passed = summary.get("improvements_passed")
    improvements_total = summary.get("improvements_total")
    if isinstance(improvements_passed, bool) or not isinstance(improvements_passed, int):
        errs.append("consolidated_improvements_improvements_passed_type")
    if isinstance(improvements_total, bool) or not isinstance(improvements_total, int):
        errs.append("consolidated_improvements_improvements_total_type")
    if errs:
        return (errs, None)
    if improvements_passed < 0 or improvements_total < 0 or improvements_passed > improvements_total:
        return (["consolidated_improvements_improvements_counts_range"], None)
    return ([], (improvements_passed, improvements_total))


def _validate_status_summary_consistency(
    *,
    status: str,
    bools: dict[str, bool],
    counts: tuple[int, int],
) -> list[str]:
    improvements_passed, improvements_total = counts
    expected_ready = (
        bools["validation_ready"]
        and bools["review_passed"]
        and bools["required_artifacts_present"]
        and improvements_passed == improvements_total
    )
    expected_status = "ready" if expected_ready else "not_ready"
    if status in ("ready", "not_ready") and status != expected_status:
        return ["consolidated_improvements_status_summary_mismatch"]
    return []


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
    errs.extend(_validate_summary_score(summary))
    bool_errs, bools = _validate_summary_booleans(summary)
    errs.extend(bool_errs)
    count_errs, counts = _validate_summary_counts(summary)
    errs.extend(count_errs)
    if bools is not None and counts is not None:
        errs.extend(_validate_status_summary_consistency(status=status, bools=bools, counts=counts))
    return errs


def validate_consolidated_improvements_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["consolidated_improvements_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["consolidated_improvements_json"]
    return validate_consolidated_improvements_dict(body)

