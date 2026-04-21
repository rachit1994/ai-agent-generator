"""Contracts for risk-budgets permission-matrix runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RISK_BUDGETS_PERMISSION_MATRIX_CONTRACT = "sde.risk_budgets_permission_matrix.v1"
RISK_BUDGETS_PERMISSION_MATRIX_SCHEMA_VERSION = "1.0"


def _validate_checks(checks: Any) -> tuple[list[str], bool | None]:
    if not isinstance(checks, dict):
        return (["risk_budgets_permission_matrix_checks"], None)
    errs: list[str] = []
    values: list[bool] = []
    for key in ("balanced_gates_present", "validation_ready", "hard_stops_all_pass"):
        value = checks.get(key)
        if not isinstance(value, bool):
            errs.append(f"risk_budgets_permission_matrix_check_type:{key}")
            continue
        values.append(value)
    if errs:
        return (errs, None)
    return ([], all(values))


def _validate_counts(counts: Any) -> tuple[list[str], int | None]:
    if not isinstance(counts, dict):
        return (["risk_budgets_permission_matrix_counts"], None)
    hard_stop_count = counts.get("hard_stop_count")
    if isinstance(hard_stop_count, bool) or not isinstance(hard_stop_count, int):
        return (["risk_budgets_permission_matrix_count_type:hard_stop_count"], None)
    if hard_stop_count < 0:
        return (["risk_budgets_permission_matrix_count_range:hard_stop_count"], None)
    return ([], hard_stop_count)


def _validate_counts_checks_coherence(
    checks: Any,
    hard_stop_count: int | None,
) -> list[str]:
    if not isinstance(checks, dict) or hard_stop_count is None:
        return []
    hard_stops_all_pass = checks.get("hard_stops_all_pass")
    if isinstance(hard_stops_all_pass, bool) and hard_stops_all_pass and hard_stop_count == 0:
        return ["risk_budgets_permission_matrix_counts_checks_mismatch"]
    return []


def _validate_status_checks_coherence(status: Any, expected_ready: bool | None) -> list[str]:
    if expected_ready is None or status not in ("ready", "degraded"):
        return []
    expected_status = "ready" if expected_ready else "degraded"
    if status != expected_status:
        return ["risk_budgets_permission_matrix_status_checks_mismatch"]
    return []


def validate_risk_budgets_permission_matrix_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["risk_budgets_permission_matrix_not_object"]
    errs: list[str] = []
    if body.get("schema") != RISK_BUDGETS_PERMISSION_MATRIX_CONTRACT:
        errs.append("risk_budgets_permission_matrix_schema")
    if body.get("schema_version") != RISK_BUDGETS_PERMISSION_MATRIX_SCHEMA_VERSION:
        errs.append("risk_budgets_permission_matrix_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("risk_budgets_permission_matrix_run_id")
    status = body.get("status")
    if status not in ("ready", "degraded"):
        errs.append("risk_budgets_permission_matrix_status")
    checks_errs, expected_ready = _validate_checks(body.get("checks"))
    errs.extend(checks_errs)
    count_errs, hard_stop_count = _validate_counts(body.get("counts"))
    errs.extend(count_errs)
    errs.extend(_validate_counts_checks_coherence(body.get("checks"), hard_stop_count))
    errs.extend(_validate_status_checks_coherence(status, expected_ready))
    return errs


def validate_risk_budgets_permission_matrix_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["risk_budgets_permission_matrix_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["risk_budgets_permission_matrix_json"]
    return validate_risk_budgets_permission_matrix_dict(body)
