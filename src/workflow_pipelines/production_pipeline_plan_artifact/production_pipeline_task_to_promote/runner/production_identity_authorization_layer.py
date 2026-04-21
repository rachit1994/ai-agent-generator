"""Write deterministic production identity-and-authorization artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from production_architecture.identity_and_authorization import (
    build_production_identity_authorization,
    validate_production_identity_authorization_dict,
)
from production_architecture.identity_and_authorization.contracts import (
    PRODUCTION_IDENTITY_AUTHORIZATION_ERROR_PREFIX,
)
from production_architecture.storage.storage.storage import ensure_dir, write_json


def _read_json_or_empty(path: Path, *, field: str) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{PRODUCTION_IDENTITY_AUTHORIZATION_ERROR_PREFIX}invalid_json:{field}") from exc
    if not isinstance(body, dict):
        raise ValueError(f"{PRODUCTION_IDENTITY_AUTHORIZATION_ERROR_PREFIX}json_not_object:{field}")
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
                f"{PRODUCTION_IDENTITY_AUTHORIZATION_ERROR_PREFIX}invalid_jsonl:{field}:{line_number}"
            ) from exc
        if not isinstance(row, dict):
            raise ValueError(
                f"{PRODUCTION_IDENTITY_AUTHORIZATION_ERROR_PREFIX}jsonl_not_object:{field}:{line_number}"
            )
    return lines


def write_production_identity_authorization_artifact(
    *,
    output_dir: Path,
    run_id: str,
) -> dict[str, Any]:
    payload = build_production_identity_authorization(
        run_id=run_id,
        permission_matrix=_read_json_or_empty(
            output_dir / "iam" / "permission_matrix.json",
            field="iam/permission_matrix.json",
        ),
        action_audit_lines=_read_lines(
            output_dir / "iam" / "action_audit.jsonl",
            field="iam/action_audit.jsonl",
        ),
        strategy_proposal=_read_json_or_empty(
            output_dir / "strategy" / "proposal.json",
            field="strategy/proposal.json",
        ),
    )
    errs = validate_production_identity_authorization_dict(payload)
    if errs:
        raise ValueError(f"{PRODUCTION_IDENTITY_AUTHORIZATION_ERROR_PREFIX}{','.join(errs)}")
    ensure_dir(output_dir / "iam")
    write_json(output_dir / "iam" / "production_identity_authorization.json", payload)
    return payload
