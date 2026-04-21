"""Contracts for risk-budgets permission-matrix runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

RISK_BUDGETS_PERMISSION_MATRIX_CONTRACT = "sde.risk_budgets_permission_matrix.v1"
RISK_BUDGETS_PERMISSION_MATRIX_SCHEMA_VERSION = "1.0"


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
    checks = body.get("checks")
    if not isinstance(checks, dict):
        errs.append("risk_budgets_permission_matrix_checks")
    else:
        for key in ("balanced_gates_present", "validation_ready", "hard_stops_all_pass"):
            if not isinstance(checks.get(key), bool):
                errs.append(f"risk_budgets_permission_matrix_check_type:{key}")
    return errs


def validate_risk_budgets_permission_matrix_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["risk_budgets_permission_matrix_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["risk_budgets_permission_matrix_json"]
    return validate_risk_budgets_permission_matrix_dict(body)
