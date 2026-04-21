"""Contracts for identity/authz plane artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

IDENTITY_AUTHZ_PLANE_CONTRACT = "sde.identity_authz_plane.v1"
IDENTITY_AUTHZ_PLANE_SCHEMA_VERSION = "1.0"


def validate_identity_authz_plane_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["identity_authz_plane_not_object"]
    errs: list[str] = []
    if body.get("schema") != IDENTITY_AUTHZ_PLANE_CONTRACT:
        errs.append("identity_authz_plane_schema")
    if body.get("schema_version") != IDENTITY_AUTHZ_PLANE_SCHEMA_VERSION:
        errs.append("identity_authz_plane_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("identity_authz_plane_run_id")
    status = body.get("status")
    if status not in ("enforced", "degraded", "missing"):
        errs.append("identity_authz_plane_status")
    controls = body.get("controls")
    if not isinstance(controls, dict):
        errs.append("identity_authz_plane_controls")
    else:
        for key in (
            "permission_matrix_present",
            "lease_bound_audit",
            "high_risk_tokens_valid",
        ):
            if not isinstance(controls.get(key), bool):
                errs.append(f"identity_authz_plane_control_type:{key}")
    coverage = body.get("coverage")
    if isinstance(coverage, bool) or not isinstance(coverage, (int, float)):
        errs.append("identity_authz_plane_coverage_type")
    elif float(coverage) < 0.0 or float(coverage) > 1.0:
        errs.append("identity_authz_plane_coverage_range")
    return errs


def validate_identity_authz_plane_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["identity_authz_plane_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["identity_authz_plane_json"]
    return validate_identity_authz_plane_dict(body)
