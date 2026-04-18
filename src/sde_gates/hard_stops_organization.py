"""HS29–HS32 multi-agent / IAM checks (V7 harness)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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


def _hs29_lease_audit(output_dir: Path) -> bool:
    active = _active_lease_ids(output_dir)
    if not active:
        return False
    path = output_dir / "iam" / "action_audit.jsonl"
    if not path.is_file():
        return True
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row: dict[str, Any] = json.loads(line)
        except json.JSONDecodeError:
            return False
        lid = row.get("lease_id")
        if lid and lid not in active:
            return False
    return True


def _hs30_high_risk_approval(output_dir: Path) -> bool:
    path = output_dir / "iam" / "action_audit.jsonl"
    if not path.is_file():
        return True
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            return False
        if str(row.get("risk", "")).lower() == "high" and not row.get("approval_token_id"):
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
    if body.get("applied_autonomy") is True:
        return bool(body.get("requires_promotion_package")) and bool(body.get("proposal_ref"))
    return True


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
