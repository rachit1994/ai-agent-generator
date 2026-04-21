"""Write deterministic production identity-and-authorization artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from production_architecture.identity_and_authorization import (
    build_production_identity_authorization,
    validate_production_identity_authorization_dict,
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


def write_production_identity_authorization_artifact(
    *,
    output_dir: Path,
    run_id: str,
) -> dict[str, Any]:
    payload = build_production_identity_authorization(
        run_id=run_id,
        permission_matrix=_read_json_or_empty(output_dir / "iam" / "permission_matrix.json"),
        action_audit_lines=_read_lines(output_dir / "iam" / "action_audit.jsonl"),
        strategy_proposal=_read_json_or_empty(output_dir / "strategy" / "proposal.json"),
    )
    errs = validate_production_identity_authorization_dict(payload)
    if errs:
        raise ValueError(f"production_identity_authorization_contract:{','.join(errs)}")
    ensure_dir(output_dir / "iam")
    write_json(output_dir / "iam" / "production_identity_authorization.json", payload)
    return payload
