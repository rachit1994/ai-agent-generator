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


def build_production_identity_authorization(
    *,
    run_id: str,
    permission_matrix: dict[str, Any],
    action_audit_lines: list[str],
    strategy_proposal: dict[str, Any],
) -> dict[str, Any]:
    permission_matrix_present = isinstance(permission_matrix, dict) and bool(permission_matrix.get("roles"))
    high_risk_approvals_valid = True
    for line in action_audit_lines:
        if not isinstance(line, str) or not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            high_risk_approvals_valid = False
            continue
        if not isinstance(row, dict):
            high_risk_approvals_valid = False
            continue
        if str(row.get("risk", "")).lower() != "high":
            continue
        token_id = row.get("approval_token_id")
        token_exp = row.get("approval_token_expires_at")
        if not isinstance(token_id, str) or not token_id.strip():
            high_risk_approvals_valid = False
        if not isinstance(token_exp, str) or not token_exp.strip():
            high_risk_approvals_valid = False
    requires_promotion = bool(strategy_proposal.get("requires_promotion_package")) if isinstance(strategy_proposal, dict) else False
    applied_autonomy = bool(strategy_proposal.get("applied_autonomy")) if isinstance(strategy_proposal, dict) else False
    strategy_guarded = (not applied_autonomy) or requires_promotion
    controls = {
        "permission_matrix_present": permission_matrix_present,
        "high_risk_approvals_valid": high_risk_approvals_valid,
        "strategy_self_approval_guarded": strategy_guarded,
    }
    coverage = _clamp01(sum(1 for ok in controls.values() if ok) / len(controls))
    status = "missing"
    if coverage >= 1.0:
        status = "enforced"
    elif coverage >= 0.5:
        status = "degraded"
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
