"""Contracts for production identity-and-authorization artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PRODUCTION_IDENTITY_AUTHORIZATION_CONTRACT = "sde.production_identity_authorization.v1"
PRODUCTION_IDENTITY_AUTHORIZATION_SCHEMA_VERSION = "1.0"
PRODUCTION_IDENTITY_AUTHORIZATION_VALID_STATUSES = ("enforced", "degraded", "missing")
PRODUCTION_IDENTITY_AUTHORIZATION_REQUIRED_CONTROL_KEYS = (
    "permission_matrix_present",
    "high_risk_approvals_valid",
    "high_risk_dual_control_valid",
    "strategy_self_approval_guarded",
)
PRODUCTION_IDENTITY_AUTHORIZATION_REQUIRED_EVIDENCE_KEYS = (
    "permission_matrix_ref",
    "action_audit_ref",
    "strategy_proposal_ref",
)
PRODUCTION_IDENTITY_AUTHORIZATION_ERROR_PREFIX = "production_identity_authorization_contract:"
_COVERAGE_ENFORCED_EPSILON = 1e-9


def _append_evidence_errors(evidence: Any, errs: list[str]) -> None:
    if not isinstance(evidence, dict):
        errs.append("production_identity_authorization_evidence")
        return
    for key in PRODUCTION_IDENTITY_AUTHORIZATION_REQUIRED_EVIDENCE_KEYS:
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"production_identity_authorization_evidence_ref:{key}")


def _append_status_mismatch_error(status: Any, coverage: Any, errs: list[str]) -> None:
    if errs or not isinstance(coverage, (int, float)) or isinstance(coverage, bool):
        return
    derived_status = "missing"
    normalized_coverage = float(coverage)
    if abs(normalized_coverage - 1.0) <= _COVERAGE_ENFORCED_EPSILON:
        derived_status = "enforced"
    elif normalized_coverage >= 0.5:
        derived_status = "degraded"
    if status != derived_status:
        errs.append("production_identity_authorization_status_coverage_mismatch")


def _append_status_controls_mismatch_error(status: Any, controls: Any, errs: list[str]) -> None:
    if not isinstance(controls, dict) or status not in PRODUCTION_IDENTITY_AUTHORIZATION_VALID_STATUSES:
        return
    values = [controls.get(key) for key in PRODUCTION_IDENTITY_AUTHORIZATION_REQUIRED_CONTROL_KEYS]
    if any(not isinstance(value, bool) for value in values):
        return
    all_true = all(values)
    any_true = any(values)
    if status == "enforced" and not all_true:
        errs.append("production_identity_authorization_status_controls_mismatch")
    if status == "missing" and any_true:
        errs.append("production_identity_authorization_status_controls_mismatch")


def _append_core_field_errors(body: dict[str, Any], errs: list[str]) -> tuple[Any, Any, Any]:
    if body.get("schema") != PRODUCTION_IDENTITY_AUTHORIZATION_CONTRACT:
        errs.append("production_identity_authorization_schema")
    if body.get("schema_version") != PRODUCTION_IDENTITY_AUTHORIZATION_SCHEMA_VERSION:
        errs.append("production_identity_authorization_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("production_identity_authorization_run_id")
    status = body.get("status")
    if status not in PRODUCTION_IDENTITY_AUTHORIZATION_VALID_STATUSES:
        errs.append("production_identity_authorization_status")
    controls = body.get("controls")
    return status, controls, body.get("coverage")


def validate_production_identity_authorization_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["production_identity_authorization_not_object"]
    errs: list[str] = []
    status, controls, coverage = _append_core_field_errors(body, errs)
    if not isinstance(controls, dict):
        errs.append("production_identity_authorization_controls")
    else:
        for key in PRODUCTION_IDENTITY_AUTHORIZATION_REQUIRED_CONTROL_KEYS:
            if not isinstance(controls.get(key), bool):
                errs.append(f"production_identity_authorization_control_type:{key}")
    if isinstance(coverage, bool) or not isinstance(coverage, (int, float)):
        errs.append("production_identity_authorization_coverage_type")
    elif float(coverage) < 0.0 or float(coverage) > 1.0:
        errs.append("production_identity_authorization_coverage_range")
    _append_evidence_errors(body.get("evidence"), errs)
    _append_status_mismatch_error(status, coverage, errs)
    _append_status_controls_mismatch_error(status, controls, errs)
    return errs


def validate_production_identity_authorization_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["production_identity_authorization_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["production_identity_authorization_json"]
    return validate_production_identity_authorization_dict(body)
