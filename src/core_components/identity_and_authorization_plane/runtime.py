"""Deterministic identity/authz plane derivation."""

from __future__ import annotations

import json
from typing import Any

from .contracts import IDENTITY_AUTHZ_PLANE_CONTRACT, IDENTITY_AUTHZ_PLANE_SCHEMA_VERSION


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def build_identity_authz_plane(
    *,
    run_id: str,
    permission_matrix: dict[str, Any],
    action_audit_lines: list[str],
    lease_table: dict[str, Any],
) -> dict[str, Any]:
    permission_matrix_present = isinstance(permission_matrix, dict) and bool(permission_matrix.get("roles"))
    active_leases: set[str] = set()
    if isinstance(lease_table, dict):
        leases = lease_table.get("leases")
        if isinstance(leases, list):
            for row in leases:
                if not isinstance(row, dict):
                    continue
                if bool(row.get("active")) and isinstance(row.get("lease_id"), str) and row.get("lease_id").strip():
                    active_leases.add(row.get("lease_id").strip())
    lease_bound_audit = True
    high_risk_tokens_valid = True
    for line in action_audit_lines:
        if not isinstance(line, str) or not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            lease_bound_audit = False
            high_risk_tokens_valid = False
            continue
        if not isinstance(row, dict):
            lease_bound_audit = False
            high_risk_tokens_valid = False
            continue
        lease_id = row.get("lease_id")
        if not isinstance(lease_id, str) or lease_id.strip() not in active_leases:
            lease_bound_audit = False
        if str(row.get("risk", "")).lower() == "high":
            token_id = row.get("approval_token_id")
            token_exp = row.get("approval_token_expires_at")
            if not isinstance(token_id, str) or not token_id.strip():
                high_risk_tokens_valid = False
            if not isinstance(token_exp, str) or not token_exp.strip():
                high_risk_tokens_valid = False
    controls = {
        "permission_matrix_present": permission_matrix_present,
        "lease_bound_audit": lease_bound_audit,
        "high_risk_tokens_valid": high_risk_tokens_valid,
    }
    coverage = _clamp01(sum(1 for value in controls.values() if value) / len(controls))
    status = "enforced" if coverage == 1.0 else ("degraded" if coverage >= 0.5 else "missing")
    return {
        "schema": IDENTITY_AUTHZ_PLANE_CONTRACT,
        "schema_version": IDENTITY_AUTHZ_PLANE_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "coverage": coverage,
        "controls": controls,
        "evidence": {
            "permission_matrix_ref": "iam/permission_matrix.json",
            "action_audit_ref": "iam/action_audit.jsonl",
            "lease_table_ref": "coordination/lease_table.json",
            "identity_authz_plane_ref": "iam/identity_authz_plane.json",
        },
    }
