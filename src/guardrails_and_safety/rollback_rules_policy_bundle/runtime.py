"""Deterministic rollback-rules policy-bundle evidence derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    ROLLBACK_RULES_POLICY_BUNDLE_CONTRACT,
    ROLLBACK_RULES_POLICY_BUNDLE_SCHEMA_VERSION,
)


def build_rollback_rules_policy_bundle(
    *,
    run_id: str,
    rollback_record: dict[str, Any],
) -> dict[str, Any]:
    record_present = bool(rollback_record)
    schema_valid = rollback_record.get("schema_version") == "1.0" if isinstance(rollback_record, dict) else False
    status = rollback_record.get("status") if isinstance(rollback_record, dict) else None
    prev_sha = rollback_record.get("previous_policy_sha256") if isinstance(rollback_record, dict) else None
    curr_sha = rollback_record.get("current_policy_sha256") if isinstance(rollback_record, dict) else None
    paths_touched = rollback_record.get("paths_touched") if isinstance(rollback_record, dict) else []
    if not isinstance(paths_touched, list):
        paths_touched = []
    atomic_sha_change = (
        status != "rolled_back_atomic"
        or (
            isinstance(prev_sha, str)
            and isinstance(curr_sha, str)
            and prev_sha.strip()
            and curr_sha.strip()
            and prev_sha != curr_sha
        )
    )
    paths_touched_valid = status != "rolled_back_atomic" or len([p for p in paths_touched if isinstance(p, str) and p.strip()]) > 0
    derived_status = "invalid"
    if status == "none":
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
            "policy_bundle_rollback_ref": "program/policy_bundle_rollback.json",
            "rollback_rules_policy_bundle_ref": "program/rollback_rules_policy_bundle.json",
        },
    }
