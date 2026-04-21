"""HS29–HS32 multi-agent / IAM checks (V7 harness)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from guardrails_and_safety.autonomy_boundaries.autonomy_boundaries_tokens_expiry.contracts import (
    validate_high_risk_approval_token_row,
)
from guardrails_and_safety.risk_budgets_permission_matrix.time_and_budget.time_util import parse_iso_utc
from workflow_pipelines.strategy_overlay.strategy_overlay_contract import validate_strategy_proposal_dict

from .run_profile import is_coding_only


def _active_lease_ids(output_dir: Path) -> set[str]:
    path = output_dir / "coordination" / "lease_table.json"
    if not path.is_file():
        return set()
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    out: set[str] = set()
    for row in body.get("leases") or []:
        if isinstance(row, dict) and row.get("active") and row.get("lease_id"):
            out.add(str(row["lease_id"]))
    return out


def _permission_matrix_valid(output_dir: Path) -> bool:
    path = output_dir / "iam" / "permission_matrix.json"
    if not path.is_file():
        return False
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    if not isinstance(body, dict):
        return False
    if body.get("schema_version") != "1.0":
        return False
    roles = body.get("roles")
    if not isinstance(roles, list) or len(roles) == 0:
        return False
    for row in roles:
        if not isinstance(row, dict):
            return False
        name = row.get("name")
        if not isinstance(name, str) or not name.strip():
            return False
    return True


def _action_audit_line_valid(row: dict[str, Any], active_lease_ids: set[str]) -> bool:
    action = row.get("action")
    if not isinstance(action, str) or not action.strip():
        return False
    actor_id = row.get("actor_id")
    if not isinstance(actor_id, str) or not actor_id.strip():
        return False
    occurred_at = row.get("occurred_at")
    if not isinstance(occurred_at, str) or parse_iso_utc(occurred_at) is None:
        return False
    lease_id = row.get("lease_id")
    if not isinstance(lease_id, str) or not lease_id.strip():
        return False
    return lease_id in active_lease_ids


def _hs29_lease_audit(output_dir: Path) -> bool:
    active = _active_lease_ids(output_dir)
    if not active:
        return False
    if not _permission_matrix_valid(output_dir):
        return False
    path = output_dir / "iam" / "action_audit.jsonl"
    if not path.is_file():
        return False
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row: dict[str, Any] = json.loads(line)
        except json.JSONDecodeError:
            return False
        if not _action_audit_line_valid(row, active):
            return False
    return True


def _high_risk_approval_line_ok(row: dict[str, Any], now: datetime) -> bool:
    return validate_high_risk_approval_token_row(row, now_utc=now) == []


def _hs30_high_risk_approval(output_dir: Path) -> bool:
    if not _permission_matrix_valid(output_dir):
        return False
    path = output_dir / "iam" / "action_audit.jsonl"
    if not path.is_file():
        return False
    now = datetime.now(timezone.utc)
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            return False
        if not _high_risk_approval_line_ok(row, now):
            return False
    return True


def _hs31_shard_handoff(output_dir: Path) -> bool:
    path = output_dir / "orchestration" / "shard_map.json"
    if not path.is_file():
        return False
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    if body.get("single_shard") is True:
        return True
    return (output_dir / "orchestration" / "handoff_envelope.json").is_file()


def _hs32_strategy_self_approval(output_dir: Path) -> bool:
    path = output_dir / "strategy" / "proposal.json"
    if not path.is_file():
        return False
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return validate_strategy_proposal_dict(body) == []


def evaluate_organization_hard_stops(output_dir: Path) -> list[dict[str, Any]]:
    if is_coding_only(output_dir):
        return []
    if not (output_dir / "coordination" / "lease_table.json").is_file():
        return []
    return [
        {"id": "HS29", "passed": _hs29_lease_audit(output_dir), "evidence_ref": "coordination/lease_table.json"},
        {"id": "HS30", "passed": _hs30_high_risk_approval(output_dir), "evidence_ref": "iam/action_audit.jsonl"},
        {"id": "HS31", "passed": _hs31_shard_handoff(output_dir), "evidence_ref": "orchestration/shard_map.json"},
        {"id": "HS32", "passed": _hs32_strategy_self_approval(output_dir), "evidence_ref": "strategy/proposal.json"},
    ]
