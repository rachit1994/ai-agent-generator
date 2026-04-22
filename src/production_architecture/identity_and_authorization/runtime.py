"""Deterministic production identity-and-authorization derivation."""

from __future__ import annotations

import json
from typing import Any

from .contracts import (
    PRODUCTION_IDENTITY_AUTHORIZATION_CONTRACT,
    PRODUCTION_IDENTITY_AUTHORIZATION_SCHEMA_VERSION,
)


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _parse_audit_row(line: str) -> dict[str, Any] | None:
    try:
        row = json.loads(line)
    except json.JSONDecodeError:
        return None
    if not isinstance(row, dict):
        return None
    return row


def _apply_high_risk_controls(row: dict[str, Any], controls: dict[str, bool]) -> None:
    if str(row.get("risk", "")).lower() != "high":
        return
    if not _has_text(row.get("approval_token_id")) or not _has_text(row.get("approval_token_expires_at")):
        controls["high_risk_approvals_valid"] = False
    actor_id = row.get("actor_id")
    approver_id = row.get("approver_id")
    if not _has_text(actor_id) or not _has_text(approver_id):
        controls["high_risk_dual_control_valid"] = False
        return
    if actor_id.strip() == approver_id.strip():
        controls["high_risk_dual_control_valid"] = False


def _status_from_coverage(coverage: float) -> str:
    if coverage >= 1.0:
        return "enforced"
    if coverage >= 0.5:
        return "degraded"
    return "missing"


def _has_valid_roles(permission_matrix: dict[str, Any]) -> bool:
    roles = permission_matrix.get("roles")
    if isinstance(roles, list):
        return len(roles) > 0
    if isinstance(roles, dict):
        return len(roles) > 0
    return False


def _strategy_guarded(strategy_proposal: dict[str, Any]) -> bool:
    applied_autonomy = strategy_proposal.get("applied_autonomy")
    requires_promotion = strategy_proposal.get("requires_promotion_package")
    if not isinstance(applied_autonomy, bool) or not isinstance(requires_promotion, bool):
        return False
    return (not applied_autonomy) or requires_promotion


def build_production_identity_authorization(
    *,
    run_id: str,
    permission_matrix: dict[str, Any],
    action_audit_lines: list[str],
    strategy_proposal: dict[str, Any],
) -> dict[str, Any]:
    controls = {
        "permission_matrix_present": (
            isinstance(permission_matrix, dict) and _has_valid_roles(permission_matrix)
        ),
        "high_risk_approvals_valid": True,
        "high_risk_dual_control_valid": True,
    }
    for line in action_audit_lines:
        if not isinstance(line, str) or not line.strip():
            continue
        row = _parse_audit_row(line)
        if row is None:
            controls["high_risk_approvals_valid"] = False
            controls["high_risk_dual_control_valid"] = False
            continue
        _apply_high_risk_controls(row, controls)
    controls["strategy_self_approval_guarded"] = (
        _strategy_guarded(strategy_proposal) if isinstance(strategy_proposal, dict) else False
    )
    coverage = _clamp01(sum(1 for ok in controls.values() if ok) / len(controls))
    status = _status_from_coverage(coverage)
    return {
        "schema": PRODUCTION_IDENTITY_AUTHORIZATION_CONTRACT,
        "schema_version": PRODUCTION_IDENTITY_AUTHORIZATION_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "coverage": coverage,
        "controls": controls,
        "evidence": {
            "permission_matrix_ref": "iam/permission_matrix.json",
            "action_audit_ref": "iam/action_audit.jsonl",
            "strategy_proposal_ref": "strategy/proposal.json",
            "production_identity_authorization_ref": "iam/production_identity_authorization.json",
        },
    }
