"""Write deterministic identity/authz plane artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core_components.identity_and_authorization_plane import (
    build_identity_authz_plane,
    validate_identity_authz_plane_dict,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    body = json.loads(path.read_text(encoding="utf-8"))
    return body if isinstance(body, dict) else {}


def _read_lines(path: Path) -> list[str]:
    if not path.is_file():
        return []
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_identity_authz_plane_artifact(
    *,
    output_dir: Path,
    run_id: str,
) -> dict[str, Any]:
    payload = build_identity_authz_plane(
        run_id=run_id,
        permission_matrix=_read_json_or_empty(output_dir / "iam" / "permission_matrix.json"),
        action_audit_lines=_read_lines(output_dir / "iam" / "action_audit.jsonl"),
        lease_table=_read_json_or_empty(output_dir / "coordination" / "lease_table.json"),
    )
    errs = validate_identity_authz_plane_dict(payload)
    if errs:
        raise ValueError(f"identity_authz_plane_contract:{','.join(errs)}")
    ensure_dir(output_dir / "iam")
    write_json(output_dir / "iam" / "identity_authz_plane.json", payload)
    return payload
