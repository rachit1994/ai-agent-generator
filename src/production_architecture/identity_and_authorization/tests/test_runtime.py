from __future__ import annotations

from production_architecture.identity_and_authorization import (
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


def test_validate_production_identity_authorization_fail_closed() -> None:
    errs = validate_production_identity_authorization_dict({"schema": "bad"})
    assert "production_identity_authorization_schema" in errs
    assert "production_identity_authorization_schema_version" in errs
