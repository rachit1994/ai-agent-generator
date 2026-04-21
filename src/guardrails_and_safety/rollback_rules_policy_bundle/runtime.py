"""Deterministic rollback-rules policy-bundle evidence derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    POLICY_BUNDLE_ROLLBACK_REF,
    ROLLBACK_RULES_POLICY_BUNDLE_CONTRACT,
    ROLLBACK_RULES_POLICY_BUNDLE_REF,
    ROLLBACK_RULES_POLICY_BUNDLE_SCHEMA_VERSION,
)


def _sha256_hex(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    lowered = value.lower()
    for c in lowered:
        if c in "0123456789abcdef":
            continue
        return False
    return True


def build_rollback_rules_policy_bundle(
    *,
    run_id: str,
    rollback_record: dict[str, Any],
) -> dict[str, Any]:
    record_present = bool(rollback_record)
    status = rollback_record.get("status") if isinstance(rollback_record, dict) else "none"
    schema_valid = bool(
        not record_present
        or (
            isinstance(rollback_record, dict)
            and rollback_record.get("schema_version") == "1.0"
            and status in ("none", "rolled_back_atomic")
        )
    )
    prev_sha = rollback_record.get("previous_policy_sha256") if isinstance(rollback_record, dict) else None
    curr_sha = rollback_record.get("current_policy_sha256") if isinstance(rollback_record, dict) else None
    paths_touched = rollback_record.get("paths_touched") if isinstance(rollback_record, dict) else []
    if not isinstance(paths_touched, list):
        paths_touched = []
    atomic_sha_change = (
        status != "rolled_back_atomic"
        or (
            _sha256_hex(prev_sha)
            and _sha256_hex(curr_sha)
            and prev_sha != curr_sha
        )
    )
    normalized_paths = [p.strip() for p in paths_touched if isinstance(p, str) and p.strip()]
    paths_touched_valid = status != "rolled_back_atomic" or (
        len(normalized_paths) > 0 and len(set(normalized_paths)) == len(normalized_paths)
    )
    derived_status = "invalid"
    if not record_present:
        derived_status = "none"
    elif status == "none" and schema_valid:
        derived_status = "none"
    elif status == "rolled_back_atomic" and schema_valid and atomic_sha_change and paths_touched_valid:
        derived_status = "rolled_back_atomic"
    checks = {
        "record_present": record_present,
        "schema_valid": schema_valid,
        "atomic_sha_change": atomic_sha_change,
        "paths_touched_valid": paths_touched_valid,
    }
    return {
        "schema": ROLLBACK_RULES_POLICY_BUNDLE_CONTRACT,
        "schema_version": ROLLBACK_RULES_POLICY_BUNDLE_SCHEMA_VERSION,
        "run_id": run_id,
        "status": derived_status,
        "rollback_checks": checks,
        "evidence": {
            "policy_bundle_rollback_ref": POLICY_BUNDLE_ROLLBACK_REF,
            "rollback_rules_policy_bundle_ref": ROLLBACK_RULES_POLICY_BUNDLE_REF,
        },
    }
