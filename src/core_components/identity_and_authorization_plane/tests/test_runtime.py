from __future__ import annotations

from core_components.identity_and_authorization_plane import (
    build_identity_authz_plane,
    validate_identity_authz_plane_dict,
)


def test_build_identity_authz_plane_is_deterministic() -> None:
    permission_matrix = {"schema_version": "1.0", "roles": [{"name": "implementor"}]}
    lease_table = {"leases": [{"lease_id": "lease-default", "active": True}]}
    audit_lines = [
        '{"action":"artifact_write","risk":"low","lease_id":"lease-default","actor_id":"orchestrator","occurred_at":"2026-01-01T00:00:00Z"}'
    ]
    one = build_identity_authz_plane(
        run_id="rid-identity-authz",
        permission_matrix=permission_matrix,
        action_audit_lines=audit_lines,
        lease_table=lease_table,
    )
    two = build_identity_authz_plane(
        run_id="rid-identity-authz",
        permission_matrix=permission_matrix,
        action_audit_lines=audit_lines,
        lease_table=lease_table,
    )
    assert one == two
    assert validate_identity_authz_plane_dict(one) == []


def test_validate_identity_authz_plane_fail_closed() -> None:
    errs = validate_identity_authz_plane_dict({"schema": "bad"})
    assert "identity_authz_plane_schema" in errs
    assert "identity_authz_plane_schema_version" in errs
