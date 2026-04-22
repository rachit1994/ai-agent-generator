from __future__ import annotations

import json

import pytest

from core_components.identity_and_authorization_plane import (
    IDENTITY_AUTHZ_PLANE_ERROR_PREFIX,
    IDENTITY_AUTHZ_PLANE_REQUIRED_CONTROL_KEYS,
    IDENTITY_AUTHZ_PLANE_REQUIRED_EVIDENCE_KEYS,
    IDENTITY_AUTHZ_PLANE_VALID_STATUSES,
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


def test_build_identity_authz_plane_is_byte_serialization_deterministic() -> None:
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
    one_bytes = json.dumps(one, sort_keys=True, separators=(",", ":")).encode("utf-8")
    two_bytes = json.dumps(two, sort_keys=True, separators=(",", ":")).encode("utf-8")
    assert one_bytes == two_bytes


def test_validate_identity_authz_plane_fail_closed() -> None:
    errs = validate_identity_authz_plane_dict({"schema": "bad"})
    assert "identity_authz_plane_schema" in errs
    assert "identity_authz_plane_schema_version" in errs
    assert validate_identity_authz_plane_dict([]) == ["identity_authz_plane_not_object"]


def _valid_payload() -> dict[str, object]:
    return build_identity_authz_plane(
        run_id="rid",
        permission_matrix={"roles": [{"name": "implementor"}]},
        action_audit_lines=['{"risk":"high","lease_id":"l1","approval_token_id":"tok","approval_token_expires_at":"2026"}'],
        lease_table={"leases": [{"lease_id": "l1", "active": True}]},
    )


def test_identity_authz_plane_constants_are_pinned() -> None:
    assert IDENTITY_AUTHZ_PLANE_VALID_STATUSES == ("enforced", "degraded", "missing")
    assert IDENTITY_AUTHZ_PLANE_ERROR_PREFIX == "identity_authz_plane_contract:"
    assert IDENTITY_AUTHZ_PLANE_REQUIRED_CONTROL_KEYS == (
        "permission_matrix_present",
        "lease_bound_audit",
        "high_risk_tokens_valid",
        "authenticated_actor_audit",
        "risk_scope_fields_present",
    )
    assert IDENTITY_AUTHZ_PLANE_REQUIRED_EVIDENCE_KEYS == (
        "permission_matrix_ref",
        "action_audit_ref",
        "lease_table_ref",
    )


def test_validate_identity_authz_plane_rejects_bool_coverage() -> None:
    payload = _valid_payload()
    payload["coverage"] = True
    assert "identity_authz_plane_coverage_type" in validate_identity_authz_plane_dict(payload)


@pytest.mark.parametrize("coverage", [-0.1, 1.5])
def test_validate_identity_authz_plane_rejects_out_of_range_coverage(coverage: float) -> None:
    payload = _valid_payload()
    payload["coverage"] = coverage
    assert "identity_authz_plane_coverage_range" in validate_identity_authz_plane_dict(payload)


def test_validate_identity_authz_plane_rejects_missing_control_key() -> None:
    payload = _valid_payload()
    del payload["controls"]["lease_bound_audit"]  # type: ignore[index]
    assert "identity_authz_plane_control_type:lease_bound_audit" in validate_identity_authz_plane_dict(payload)


def test_validate_identity_authz_plane_rejects_missing_evidence_ref() -> None:
    payload = _valid_payload()
    del payload["evidence"]["lease_table_ref"]  # type: ignore[index]
    assert "identity_authz_plane_evidence_ref:lease_table_ref" in validate_identity_authz_plane_dict(payload)


def test_validate_identity_authz_plane_rejects_status_coverage_mismatch() -> None:
    payload = _valid_payload()
    payload["status"] = "enforced"
    payload["coverage"] = 0.66
    assert "identity_authz_plane_status_coverage_mismatch" in validate_identity_authz_plane_dict(payload)


def test_validate_identity_authz_plane_rejects_status_controls_mismatch() -> None:
    payload = _valid_payload()
    payload["status"] = "enforced"
    payload["controls"]["lease_bound_audit"] = False  # type: ignore[index]
    assert "identity_authz_plane_status_controls_mismatch" in validate_identity_authz_plane_dict(payload)


def test_validate_identity_authz_plane_rejects_unknown_status() -> None:
    payload = _valid_payload()
    payload["status"] = "unknown"
    assert "identity_authz_plane_status" in validate_identity_authz_plane_dict(payload)


@pytest.mark.parametrize("run_id", ["", "   "])
def test_validate_identity_authz_plane_rejects_empty_or_whitespace_run_id(run_id: str) -> None:
    payload = _valid_payload()
    payload["run_id"] = run_id
    assert "identity_authz_plane_run_id" in validate_identity_authz_plane_dict(payload)


def test_validate_identity_authz_plane_rejects_non_dict_controls() -> None:
    payload = _valid_payload()
    payload["controls"] = []
    assert "identity_authz_plane_controls" in validate_identity_authz_plane_dict(payload)


def test_validate_identity_authz_plane_rejects_non_dict_evidence() -> None:
    payload = _valid_payload()
    payload["evidence"] = []
    assert "identity_authz_plane_evidence" in validate_identity_authz_plane_dict(payload)


def test_build_identity_authz_plane_unknown_lease_fails_control() -> None:
    payload = build_identity_authz_plane(
        run_id="rid",
        permission_matrix={"roles": [{"name": "implementor"}]},
        action_audit_lines=['{"risk":"low","lease_id":"unknown"}'],
        lease_table={"leases": [{"lease_id": "l1", "active": True}]},
    )
    assert payload["controls"]["lease_bound_audit"] is False  # type: ignore[index]


def test_build_identity_authz_plane_missing_actor_id_fails_control() -> None:
    payload = build_identity_authz_plane(
        run_id="rid",
        permission_matrix={"roles": [{"name": "implementor"}]},
        action_audit_lines=['{"risk":"low","lease_id":"l1","role":"implementor","lifecycle_stage":"junior"}'],
        lease_table={"leases": [{"lease_id": "l1", "active": True}]},
    )
    assert payload["controls"]["authenticated_actor_audit"] is False  # type: ignore[index]


def test_build_identity_authz_plane_missing_risk_scope_fields_fails_control() -> None:
    payload = build_identity_authz_plane(
        run_id="rid",
        permission_matrix={"roles": [{"name": "implementor"}]},
        action_audit_lines=['{"risk":"low","lease_id":"l1","actor_id":"agent-1"}'],
        lease_table={"leases": [{"lease_id": "l1", "active": True}]},
    )
    assert payload["controls"]["risk_scope_fields_present"] is False  # type: ignore[index]


@pytest.mark.parametrize(
    "line",
    [
        '{"risk":"high","lease_id":"l1","approval_token_expires_at":"2026"}',
        '{"risk":"high","lease_id":"l1","approval_token_id":"tok"}',
    ],
)
def test_build_identity_authz_plane_high_risk_requires_token_fields(line: str) -> None:
    payload = build_identity_authz_plane(
        run_id="rid",
        permission_matrix={"roles": [{"name": "implementor"}]},
        action_audit_lines=[line],
        lease_table={"leases": [{"lease_id": "l1", "active": True}]},
    )
    assert payload["controls"]["high_risk_tokens_valid"] is False  # type: ignore[index]


def test_build_identity_authz_plane_missing_action_audit_fail_closes_controls() -> None:
    payload = build_identity_authz_plane(
        run_id="rid",
        permission_matrix={"roles": [{"name": "implementor"}]},
        action_audit_lines=[],
        lease_table={"leases": [{"lease_id": "l1", "active": True}]},
    )
    assert payload["controls"]["permission_matrix_present"] is False  # type: ignore[index]
    assert payload["controls"]["lease_bound_audit"] is False  # type: ignore[index]
    assert payload["controls"]["high_risk_tokens_valid"] is False  # type: ignore[index]
    assert payload["controls"]["authenticated_actor_audit"] is False  # type: ignore[index]
    assert payload["controls"]["risk_scope_fields_present"] is False  # type: ignore[index]
    assert payload["status"] == "missing"
