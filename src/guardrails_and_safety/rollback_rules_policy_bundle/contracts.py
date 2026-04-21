"""Contracts for rollback-rules policy-bundle evidence artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROLLBACK_RULES_POLICY_BUNDLE_CONTRACT = "sde.rollback_rules_policy_bundle.v1"
ROLLBACK_RULES_POLICY_BUNDLE_SCHEMA_VERSION = "1.0"
POLICY_BUNDLE_ROLLBACK_REF = "program/policy_bundle_rollback.json"
ROLLBACK_RULES_POLICY_BUNDLE_REF = "program/rollback_rules_policy_bundle.json"


def validate_rollback_rules_policy_bundle_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["rollback_rules_policy_bundle_not_object"]
    errs: list[str] = []
    if body.get("schema") != ROLLBACK_RULES_POLICY_BUNDLE_CONTRACT:
        errs.append("rollback_rules_policy_bundle_schema")
    if body.get("schema_version") != ROLLBACK_RULES_POLICY_BUNDLE_SCHEMA_VERSION:
        errs.append("rollback_rules_policy_bundle_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("rollback_rules_policy_bundle_run_id")
    status = body.get("status")
    if status not in ("none", "rolled_back_atomic", "invalid"):
        errs.append("rollback_rules_policy_bundle_status")
    rollback_checks = body.get("rollback_checks")
    if not isinstance(rollback_checks, dict):
        errs.append("rollback_rules_policy_bundle_checks")
    else:
        for key in ("record_present", "schema_valid", "atomic_sha_change", "paths_touched_valid"):
            if not isinstance(rollback_checks.get(key), bool):
                errs.append(f"rollback_rules_policy_bundle_check_type:{key}")
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        errs.append("rollback_rules_policy_bundle_evidence")
        evidence = {}
    if evidence.get("policy_bundle_rollback_ref") != POLICY_BUNDLE_ROLLBACK_REF:
        errs.append("rollback_rules_policy_bundle_evidence_policy_bundle_rollback_ref")
    if evidence.get("rollback_rules_policy_bundle_ref") != ROLLBACK_RULES_POLICY_BUNDLE_REF:
        errs.append("rollback_rules_policy_bundle_evidence_rollback_rules_policy_bundle_ref")
    return errs


def validate_rollback_rules_policy_bundle_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["rollback_rules_policy_bundle_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["rollback_rules_policy_bundle_json"]
    return validate_rollback_rules_policy_bundle_dict(body)
