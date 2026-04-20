"""Optional ``program/policy_bundle_rollback.json`` contract (§11 rollback evidence)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

POLICY_ROLLBACK_SCHEMA = "1.0"


def _sha256_hex(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    lowered = value.lower()
    for c in lowered:
        if c in "0123456789abcdef":
            continue
        return False
    return True


def _errors_for_atomic_rollback(body: dict[str, Any]) -> list[str]:
    if not (_sha256_hex(body.get("previous_policy_sha256")) and _sha256_hex(body.get("current_policy_sha256"))):
        return ["policy_bundle_rollback_sha256_invalid"]
    paths = body.get("paths_touched")
    if not isinstance(paths, list) or len(paths) == 0:
        return ["policy_bundle_rollback_paths_touched_required"]
    for p in paths:
        if not isinstance(p, str) or not p.strip():
            return ["policy_bundle_rollback_paths_touched_invalid"]
    return []


def validate_policy_bundle_rollback(output_dir: Path) -> list[str]:
    """Return human-readable error codes; empty when file absent or contract satisfied."""
    path = output_dir / "program" / "policy_bundle_rollback.json"
    if not path.is_file():
        return []
    try:
        body: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["policy_bundle_rollback_invalid_json"]
    if body.get("schema_version") != POLICY_ROLLBACK_SCHEMA:
        return ["policy_bundle_rollback_schema_version"]
    st = body.get("status")
    if st == "none":
        return []
    if st == "rolled_back_atomic":
        return _errors_for_atomic_rollback(body)
    return ["policy_bundle_rollback_status_invalid"]
