"""Contracts for production identity-and-authorization artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PRODUCTION_IDENTITY_AUTHORIZATION_CONTRACT = "sde.production_identity_authorization.v1"
PRODUCTION_IDENTITY_AUTHORIZATION_SCHEMA_VERSION = "1.0"


def validate_production_identity_authorization_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["production_identity_authorization_not_object"]
    errs: list[str] = []
    if body.get("schema") != PRODUCTION_IDENTITY_AUTHORIZATION_CONTRACT:
        errs.append("production_identity_authorization_schema")
    if body.get("schema_version") != PRODUCTION_IDENTITY_AUTHORIZATION_SCHEMA_VERSION:
        errs.append("production_identity_authorization_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("production_identity_authorization_run_id")
    status = body.get("status")
    if status not in ("enforced", "degraded", "missing"):
        errs.append("production_identity_authorization_status")
    controls = body.get("controls")
    if not isinstance(controls, dict):
        errs.append("production_identity_authorization_controls")
    else:
        for key in (
            "permission_matrix_present",
            "high_risk_approvals_valid",
            "strategy_self_approval_guarded",
        ):
            if not isinstance(controls.get(key), bool):
                errs.append(f"production_identity_authorization_control_type:{key}")
    coverage = body.get("coverage")
    if isinstance(coverage, bool) or not isinstance(coverage, (int, float)):
        errs.append("production_identity_authorization_coverage_type")
    elif float(coverage) < 0.0 or float(coverage) > 1.0:
        errs.append("production_identity_authorization_coverage_range")
    return errs


def validate_production_identity_authorization_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["production_identity_authorization_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["production_identity_authorization_json"]
    return validate_production_identity_authorization_dict(body)
