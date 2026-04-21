"""Contracts for identity/authz plane artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

IDENTITY_AUTHZ_PLANE_CONTRACT = "sde.identity_authz_plane.v1"
IDENTITY_AUTHZ_PLANE_SCHEMA_VERSION = "1.0"
IDENTITY_AUTHZ_PLANE_VALID_STATUSES = ("enforced", "degraded", "missing")
IDENTITY_AUTHZ_PLANE_REQUIRED_CONTROL_KEYS = (
    "permission_matrix_present",
    "lease_bound_audit",
    "high_risk_tokens_valid",
    "authenticated_actor_audit",
    "risk_scope_fields_present",
)
IDENTITY_AUTHZ_PLANE_REQUIRED_EVIDENCE_KEYS = (
    "permission_matrix_ref",
    "action_audit_ref",
    "lease_table_ref",
)
IDENTITY_AUTHZ_PLANE_ERROR_PREFIX = "identity_authz_plane_contract:"
_COVERAGE_ENFORCED_EPSILON = 1e-9


def _append_evidence_errors(evidence: Any, errs: list[str]) -> None:
    if not isinstance(evidence, dict):
        errs.append("identity_authz_plane_evidence")
        return
    for key in IDENTITY_AUTHZ_PLANE_REQUIRED_EVIDENCE_KEYS:
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"identity_authz_plane_evidence_ref:{key}")


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
        errs.append("identity_authz_plane_status_coverage_mismatch")


def _append_status_controls_mismatch_error(status: Any, controls: Any, errs: list[str]) -> None:
    if not isinstance(controls, dict) or status not in IDENTITY_AUTHZ_PLANE_VALID_STATUSES:
        return
    values = [controls.get(key) for key in IDENTITY_AUTHZ_PLANE_REQUIRED_CONTROL_KEYS]
    if any(not isinstance(value, bool) for value in values):
        return
    all_true = all(values)
    any_true = any(values)
    if status == "enforced" and not all_true:
        errs.append("identity_authz_plane_status_controls_mismatch")
    if status == "missing" and any_true:
        errs.append("identity_authz_plane_status_controls_mismatch")


def _append_core_field_errors(body: dict[str, Any], errs: list[str]) -> tuple[Any, Any, Any]:
    if body.get("schema") != IDENTITY_AUTHZ_PLANE_CONTRACT:
        errs.append("identity_authz_plane_schema")
    if body.get("schema_version") != IDENTITY_AUTHZ_PLANE_SCHEMA_VERSION:
        errs.append("identity_authz_plane_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("identity_authz_plane_run_id")
    status = body.get("status")
    if status not in IDENTITY_AUTHZ_PLANE_VALID_STATUSES:
        errs.append("identity_authz_plane_status")
    controls = body.get("controls")
    return status, controls, body.get("coverage")


def validate_identity_authz_plane_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["identity_authz_plane_not_object"]
    errs: list[str] = []
    status, controls, coverage = _append_core_field_errors(body, errs)
    if not isinstance(controls, dict):
        errs.append("identity_authz_plane_controls")
    else:
        for key in IDENTITY_AUTHZ_PLANE_REQUIRED_CONTROL_KEYS:
            if not isinstance(controls.get(key), bool):
                errs.append(f"identity_authz_plane_control_type:{key}")
    if isinstance(coverage, bool) or not isinstance(coverage, (int, float)):
        errs.append("identity_authz_plane_coverage_type")
    elif float(coverage) < 0.0 or float(coverage) > 1.0:
        errs.append("identity_authz_plane_coverage_range")
    _append_evidence_errors(body.get("evidence"), errs)
    _append_status_mismatch_error(status, coverage, errs)
    _append_status_controls_mismatch_error(status, controls, errs)
    return errs


def validate_identity_authz_plane_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["identity_authz_plane_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["identity_authz_plane_json"]
    return validate_identity_authz_plane_dict(body)
