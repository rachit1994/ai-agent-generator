"""Write deterministic identity/authz plane artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core_components.identity_and_authorization_plane import (
    build_identity_authz_plane,
    validate_identity_authz_plane_dict,
)
from core_components.identity_and_authorization_plane.contracts import IDENTITY_AUTHZ_PLANE_ERROR_PREFIX
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _read_json_or_empty(path: Path, *, field: str) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{IDENTITY_AUTHZ_PLANE_ERROR_PREFIX}invalid_json:{field}") from exc
    if not isinstance(body, dict):
        raise ValueError(f"{IDENTITY_AUTHZ_PLANE_ERROR_PREFIX}json_not_object:{field}")
    return body


def _read_lines(path: Path, *, field: str) -> list[str]:
    if not path.is_file():
        return []
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    for line_number, line in enumerate(lines, start=1):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"{IDENTITY_AUTHZ_PLANE_ERROR_PREFIX}invalid_jsonl:{field}:{line_number}"
            ) from exc
        if not isinstance(row, dict):
            raise ValueError(f"{IDENTITY_AUTHZ_PLANE_ERROR_PREFIX}jsonl_not_object:{field}:{line_number}")
    return lines


def write_identity_authz_plane_artifact(
    *,
    output_dir: Path,
    run_id: str,
) -> dict[str, Any]:
    payload = build_identity_authz_plane(
        run_id=run_id,
        permission_matrix=_read_json_or_empty(
            output_dir / "iam" / "permission_matrix.json",
            field="iam/permission_matrix.json",
        ),
        action_audit_lines=_read_lines(
            output_dir / "iam" / "action_audit.jsonl",
            field="iam/action_audit.jsonl",
        ),
        lease_table=_read_json_or_empty(
            output_dir / "coordination" / "lease_table.json",
            field="coordination/lease_table.json",
        ),
    )
    errs = validate_identity_authz_plane_dict(payload)
    if errs:
        raise ValueError(f"{IDENTITY_AUTHZ_PLANE_ERROR_PREFIX}{','.join(errs)}")
    ensure_dir(output_dir / "iam")
    write_json(output_dir / "iam" / "identity_authz_plane.json", payload)
    return payload
