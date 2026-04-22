"""Deterministic identity/authz plane derivation."""

from __future__ import annotations

import json
from typing import Any

from .contracts import IDENTITY_AUTHZ_PLANE_CONTRACT, IDENTITY_AUTHZ_PLANE_SCHEMA_VERSION

_STATUS_EPSILON = 1e-9


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _active_leases(lease_table: dict[str, Any]) -> set[str]:
    if not isinstance(lease_table, dict):
        return set()
    leases = lease_table.get("leases")
    if not isinstance(leases, list):
        return set()
    out: set[str] = set()
    for row in leases:
        if not isinstance(row, dict):
            continue
        lease_id = row.get("lease_id")
        if bool(row.get("active")) and _has_text(lease_id):
            out.add(lease_id.strip())
    return out


def _initial_controls(permission_matrix: dict[str, Any]) -> dict[str, bool]:
    return {
        "permission_matrix_present": isinstance(permission_matrix, dict) and bool(permission_matrix.get("roles")),
        "lease_bound_audit": True,
        "high_risk_tokens_valid": True,
        "authenticated_actor_audit": True,
        "risk_scope_fields_present": True,
    }


def _mark_invalid_row_controls(controls: dict[str, bool]) -> None:
    controls["lease_bound_audit"] = False
    controls["high_risk_tokens_valid"] = False
    controls["authenticated_actor_audit"] = False
    controls["risk_scope_fields_present"] = False


def _apply_row_controls(row: dict[str, Any], controls: dict[str, bool], active_leases: set[str]) -> None:
    lease_id = row.get("lease_id")
    if not _has_text(lease_id) or lease_id.strip() not in active_leases:
        controls["lease_bound_audit"] = False
    if not _has_text(row.get("actor_id")):
        controls["authenticated_actor_audit"] = False

    risk = str(row.get("risk", "")).strip().lower()
    if risk not in {"low", "medium", "high"}:
        controls["risk_scope_fields_present"] = False
    if not _has_text(row.get("role")) or not _has_text(row.get("lifecycle_stage")):
        controls["risk_scope_fields_present"] = False

    if risk == "high":
        if not _has_text(row.get("approval_token_id")) or not _has_text(row.get("approval_token_expires_at")):
            controls["high_risk_tokens_valid"] = False


def _status_from_coverage(coverage: float) -> str:
    if abs(coverage - 1.0) <= _STATUS_EPSILON:
        return "enforced"
    if coverage >= 0.5:
        return "degraded"
    return "missing"


def execute_identity_authz_runtime(
    *,
    action_audit_lines: list[str],
    lease_table: dict[str, Any],
) -> dict[str, Any]:
    active_leases = _active_leases(lease_table)
    malformed_audit_rows = 0
    unknown_lease_rows = 0
    for line in action_audit_lines:
        if not isinstance(line, str) or not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            malformed_audit_rows += 1
            continue
        if not isinstance(row, dict):
            malformed_audit_rows += 1
            continue
        lease_id = row.get("lease_id")
        if not _has_text(lease_id) or lease_id.strip() not in active_leases:
            unknown_lease_rows += 1
    return {
        "audit_rows_processed": len(action_audit_lines),
        "active_leases": len(active_leases),
        "malformed_audit_rows": malformed_audit_rows,
        "unknown_lease_rows": unknown_lease_rows,
    }


def build_identity_authz_plane(
    *,
    run_id: str,
    permission_matrix: dict[str, Any],
    action_audit_lines: list[str],
    lease_table: dict[str, Any],
) -> dict[str, Any]:
    execution = execute_identity_authz_runtime(
        action_audit_lines=action_audit_lines, lease_table=lease_table
    )
    controls = _initial_controls(permission_matrix)
    active_leases = _active_leases(lease_table)
    if not action_audit_lines:
        controls["permission_matrix_present"] = False
        controls["lease_bound_audit"] = False
        controls["high_risk_tokens_valid"] = False
        controls["authenticated_actor_audit"] = False
        controls["risk_scope_fields_present"] = False
    for line in action_audit_lines:
        if not isinstance(line, str) or not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            controls["lease_bound_audit"] = False
            controls["high_risk_tokens_valid"] = False
            continue
        if not isinstance(row, dict):
            _mark_invalid_row_controls(controls)
            continue
        _apply_row_controls(row, controls, active_leases)
    coverage = _clamp01(sum(1 for value in controls.values() if value) / len(controls))
    status = _status_from_coverage(coverage)
    return {
        "schema": IDENTITY_AUTHZ_PLANE_CONTRACT,
        "schema_version": IDENTITY_AUTHZ_PLANE_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "execution": execution,
        "coverage": coverage,
        "controls": controls,
        "evidence": {
            "permission_matrix_ref": "iam/permission_matrix.json",
            "action_audit_ref": "iam/action_audit.jsonl",
            "lease_table_ref": "coordination/lease_table.json",
            "identity_authz_plane_ref": "iam/identity_authz_plane.json",
        },
    }
