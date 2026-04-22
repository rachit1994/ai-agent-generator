from __future__ import annotations

import json

import pytest

from core_components.identity_and_authorization_plane import build_identity_authz_plane
from production_architecture.identity_and_authorization import (
    PRODUCTION_IDENTITY_AUTHORIZATION_ERROR_PREFIX,
    PRODUCTION_IDENTITY_AUTHORIZATION_REQUIRED_CONTROL_KEYS,
    PRODUCTION_IDENTITY_AUTHORIZATION_REQUIRED_EVIDENCE_KEYS,
    PRODUCTION_IDENTITY_AUTHORIZATION_VALID_STATUSES,
    build_production_identity_authorization,
    validate_production_identity_authorization_dict,
)


def test_build_production_identity_authorization_is_deterministic() -> None:
    payload_one = build_production_identity_authorization(
        run_id="rid-prod-identity",
        permission_matrix={"roles": {"operator": ["read"]}},
        action_audit_lines=[
            '{"risk":"high","approval_token_id":"tok-1","approval_token_expires_at":"2026-01-01T00:00:00Z"}'
        ],
        strategy_proposal={"requires_promotion_package": True, "applied_autonomy": True},
    )
    payload_two = build_production_identity_authorization(
        run_id="rid-prod-identity",
        permission_matrix={"roles": {"operator": ["read"]}},
        action_audit_lines=[
            '{"risk":"high","approval_token_id":"tok-1","approval_token_expires_at":"2026-01-01T00:00:00Z"}'
        ],
        strategy_proposal={"requires_promotion_package": True, "applied_autonomy": True},
    )
    assert payload_one == payload_two
    assert validate_production_identity_authorization_dict(payload_one) == []


def test_build_production_identity_authorization_is_byte_serialization_deterministic() -> None:
    payload_one = build_production_identity_authorization(
        run_id="rid-prod-identity",
        permission_matrix={"roles": {"operator": ["read"]}},
        action_audit_lines=[
            '{"risk":"high","approval_token_id":"tok-1","approval_token_expires_at":"2026-01-01T00:00:00Z"}'
        ],
        strategy_proposal={"requires_promotion_package": True, "applied_autonomy": True},
    )
    payload_two = build_production_identity_authorization(
        run_id="rid-prod-identity",
        permission_matrix={"roles": {"operator": ["read"]}},
        action_audit_lines=[
            '{"risk":"high","approval_token_id":"tok-1","approval_token_expires_at":"2026-01-01T00:00:00Z"}'
        ],
        strategy_proposal={"requires_promotion_package": True, "applied_autonomy": True},
    )
    first_bytes = json.dumps(payload_one, sort_keys=True, separators=(",", ":")).encode("utf-8")
    second_bytes = json.dumps(payload_two, sort_keys=True, separators=(",", ":")).encode("utf-8")
    assert first_bytes == second_bytes


def test_validate_production_identity_authorization_fail_closed() -> None:
    errs = validate_production_identity_authorization_dict({"schema": "bad"})
    assert "production_identity_authorization_schema" in errs
    assert "production_identity_authorization_schema_version" in errs
    assert validate_production_identity_authorization_dict([]) == [
        "production_identity_authorization_not_object"
    ]


def _valid_payload() -> dict[str, object]:
    return build_production_identity_authorization(
        run_id="rid",
        permission_matrix={"roles": {"operator": ["read"]}},
        action_audit_lines=['{"risk":"high","approval_token_id":"tok","approval_token_expires_at":"2026"}'],
        strategy_proposal={"requires_promotion_package": True, "applied_autonomy": True},
    )


def test_production_identity_authorization_constants_are_pinned() -> None:
    assert PRODUCTION_IDENTITY_AUTHORIZATION_VALID_STATUSES == ("enforced", "degraded", "missing")
    assert PRODUCTION_IDENTITY_AUTHORIZATION_ERROR_PREFIX == "production_identity_authorization_contract:"
    assert PRODUCTION_IDENTITY_AUTHORIZATION_REQUIRED_CONTROL_KEYS == (
        "permission_matrix_present",
        "high_risk_approvals_valid",
        "high_risk_dual_control_valid",
        "strategy_self_approval_guarded",
    )
    assert PRODUCTION_IDENTITY_AUTHORIZATION_REQUIRED_EVIDENCE_KEYS == (
        "permission_matrix_ref",
        "action_audit_ref",
        "strategy_proposal_ref",
    )


def test_validate_production_identity_authorization_rejects_bool_coverage() -> None:
    payload = _valid_payload()
    payload["coverage"] = False
    assert "production_identity_authorization_coverage_type" in validate_production_identity_authorization_dict(
        payload
    )


def test_validate_production_identity_authorization_rejects_missing_control_key() -> None:
    payload = _valid_payload()
    del payload["controls"]["strategy_self_approval_guarded"]  # type: ignore[index]
    assert "production_identity_authorization_control_type:strategy_self_approval_guarded" in (
        validate_production_identity_authorization_dict(payload)
    )


def test_validate_production_identity_authorization_rejects_missing_evidence_ref() -> None:
    payload = _valid_payload()
    del payload["evidence"]["strategy_proposal_ref"]  # type: ignore[index]
    assert "production_identity_authorization_evidence_ref:strategy_proposal_ref" in (
        validate_production_identity_authorization_dict(payload)
    )


def test_validate_production_identity_authorization_rejects_status_coverage_mismatch() -> None:
    payload = build_production_identity_authorization(
        run_id="rid",
        permission_matrix={"roles": {"operator": ["read"]}},
        action_audit_lines=[
            '{"risk":"high","approval_token_id":"tok","approval_token_expires_at":"2026","actor_id":"agent-1","approver_id":"human-1"}'
        ],
        strategy_proposal={"requires_promotion_package": True, "applied_autonomy": True},
    )
    payload["status"] = "enforced"
    payload["coverage"] = 0.75
    payload["controls"]["high_risk_dual_control_valid"] = False  # type: ignore[index]
    errs = validate_production_identity_authorization_dict(payload)
    assert "production_identity_authorization_status_coverage_mismatch" in errs


def test_validate_production_identity_authorization_rejects_status_controls_mismatch() -> None:
    payload = _valid_payload()
    payload["status"] = "enforced"
    payload["controls"]["high_risk_dual_control_valid"] = False  # type: ignore[index]
    assert "production_identity_authorization_status_controls_mismatch" in (
        validate_production_identity_authorization_dict(payload)
    )


def test_validate_production_identity_authorization_rejects_unknown_status() -> None:
    payload = _valid_payload()
    payload["status"] = "unknown"
    assert "production_identity_authorization_status" in validate_production_identity_authorization_dict(payload)


@pytest.mark.parametrize("coverage", [-0.1, 1.1])
def test_validate_production_identity_authorization_rejects_coverage_out_of_range(
    coverage: float,
) -> None:
    payload = _valid_payload()
    payload["coverage"] = coverage
    assert "production_identity_authorization_coverage_range" in validate_production_identity_authorization_dict(
        payload
    )


@pytest.mark.parametrize("run_id", ["", "   "])
def test_validate_production_identity_authorization_rejects_empty_or_whitespace_run_id(
    run_id: str,
) -> None:
    payload = _valid_payload()
    payload["run_id"] = run_id
    assert "production_identity_authorization_run_id" in validate_production_identity_authorization_dict(payload)


def test_validate_production_identity_authorization_rejects_non_dict_controls() -> None:
    payload = _valid_payload()
    payload["controls"] = []
    assert "production_identity_authorization_controls" in validate_production_identity_authorization_dict(payload)


def test_validate_production_identity_authorization_rejects_non_dict_evidence() -> None:
    payload = _valid_payload()
    payload["evidence"] = []
    assert "production_identity_authorization_evidence" in validate_production_identity_authorization_dict(payload)


@pytest.mark.parametrize(
    "line",
    [
        '{"risk":"high","approval_token_expires_at":"2026"}',
        '{"risk":"high","approval_token_id":"tok"}',
    ],
)
def test_build_production_identity_authorization_high_risk_requires_tokens(line: str) -> None:
    payload = build_production_identity_authorization(
        run_id="rid",
        permission_matrix={"roles": {"operator": ["read"]}},
        action_audit_lines=[line],
        strategy_proposal={"requires_promotion_package": True, "applied_autonomy": True},
    )
    assert payload["controls"]["high_risk_approvals_valid"] is False  # type: ignore[index]


def test_build_production_identity_authorization_self_approval_guard_is_enforced() -> None:
    payload = build_production_identity_authorization(
        run_id="rid",
        permission_matrix={"roles": {"operator": ["read"]}},
        action_audit_lines=[],
        strategy_proposal={"requires_promotion_package": False, "applied_autonomy": True},
    )
    assert payload["controls"]["strategy_self_approval_guarded"] is False  # type: ignore[index]


@pytest.mark.parametrize(
    "line",
    [
        '{"risk":"high","approval_token_id":"tok","approval_token_expires_at":"2026","actor_id":"agent-1"}',
        '{"risk":"high","approval_token_id":"tok","approval_token_expires_at":"2026","approver_id":"human-1"}',
        '{"risk":"high","approval_token_id":"tok","approval_token_expires_at":"2026","actor_id":"agent-1","approver_id":"agent-1"}',
    ],
)
def test_build_production_identity_authorization_high_risk_requires_dual_control(line: str) -> None:
    payload = build_production_identity_authorization(
        run_id="rid",
        permission_matrix={"roles": {"operator": ["read"]}},
        action_audit_lines=[line],
        strategy_proposal={"requires_promotion_package": True, "applied_autonomy": True},
    )
    assert payload["controls"]["high_risk_dual_control_valid"] is False  # type: ignore[index]


def test_cross_plane_high_risk_missing_token_degrades_both_planes() -> None:
    audit_lines = ['{"risk":"high","lease_id":"l1","approval_token_expires_at":"2026"}']
    core_payload = build_identity_authz_plane(
        run_id="rid",
        permission_matrix={"roles": [{"name": "implementor"}]},
        action_audit_lines=audit_lines,
        lease_table={"leases": [{"lease_id": "l1", "active": True}]},
    )
    prod_payload = build_production_identity_authorization(
        run_id="rid",
        permission_matrix={"roles": {"operator": ["read"]}},
        action_audit_lines=audit_lines,
        strategy_proposal={"requires_promotion_package": True, "applied_autonomy": True},
    )
    assert core_payload["status"] != "enforced"
    assert prod_payload["status"] != "enforced"


def test_validate_production_identity_authorization_rejects_coverage_controls_mismatch() -> None:
    payload = _valid_payload()
    payload["coverage"] = 0.75
    payload["controls"]["high_risk_approvals_valid"] = False  # type: ignore[index]
    payload["controls"]["high_risk_dual_control_valid"] = False  # type: ignore[index]
    errs = validate_production_identity_authorization_dict(payload)
    assert "production_identity_authorization_coverage_controls_mismatch" in errs


def test_build_production_identity_authorization_missing_strategy_proposal_fails_guard() -> None:
    payload = build_production_identity_authorization(
        run_id="rid",
        permission_matrix={"roles": {"operator": ["read"]}},
        action_audit_lines=[],
        strategy_proposal={},
    )
    assert payload["controls"]["strategy_self_approval_guarded"] is False  # type: ignore[index]


@pytest.mark.parametrize("roles", ["operator", 42, True])
def test_build_production_identity_authorization_rejects_invalid_roles_shape(roles: object) -> None:
    payload = build_production_identity_authorization(
        run_id="rid",
        permission_matrix={"roles": roles},
        action_audit_lines=[],
        strategy_proposal={"requires_promotion_package": True, "applied_autonomy": False},
    )
    assert payload["controls"]["permission_matrix_present"] is False  # type: ignore[index]
