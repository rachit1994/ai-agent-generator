"""Contracts for auditability artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

AUDITABILITY_CONTRACT = "sde.auditability.v1"
AUDITABILITY_SCHEMA_VERSION = "1.0"
_ALLOWED_MODES = {"baseline", "guarded_pipeline", "phased_pipeline"}
_ALLOWED_STATUS = {"verifiable", "degraded", "inconsistent"}
_EVIDENCE_REFS = {
    "replay_manifest_ref": "replay_manifest.json",
    "event_store_ref": "event_store/run_events.jsonl",
    "kill_switch_ref": "kill_switch_state.json",
    "review_ref": "review.json",
    "auditability_ref": "audit/auditability.json",
}


def _validate_execution(execution: Any) -> list[str]:
    if not isinstance(execution, dict):
        return ["auditability_execution"]
    errs: list[str] = []
    int_fields = ("events_processed", "hashed_event_count", "malformed_event_rows")
    for field in int_fields:
        value = execution.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            errs.append(f"auditability_execution_{field}")
    if not isinstance(execution.get("chain_mismatch"), bool):
        errs.append("auditability_execution_chain_mismatch")
    latest_hash = execution.get("latest_hash")
    if not isinstance(latest_hash, str) or not latest_hash.strip():
        errs.append("auditability_execution_latest_hash")
    return errs


def _validate_hash_chain(hash_chain: Any) -> list[str]:
    if not isinstance(hash_chain, dict):
        return ["auditability_hash_chain"]
    errs: list[str] = []
    for key in ("chain_root", "latest_hash"):
        value = hash_chain.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"auditability_hash_chain_{key}")
    event_count = hash_chain.get("event_count")
    if isinstance(event_count, bool) or not isinstance(event_count, int) or event_count < 0:
        errs.append("auditability_hash_chain_event_count")
    if not isinstance(hash_chain.get("hash_chain_valid"), bool):
        errs.append("auditability_hash_chain_valid")
    return errs


def _validate_integrity_operations(integrity_ops: Any) -> list[str]:
    if not isinstance(integrity_ops, dict):
        return ["auditability_integrity_operations"]
    errs: list[str] = []
    for key in ("periodic_check_supported", "last_check_passed"):
        if not isinstance(integrity_ops.get(key), bool):
            errs.append(f"auditability_integrity_operations_{key}")
    checks = integrity_ops.get("checks_performed")
    if isinstance(checks, bool) or not isinstance(checks, int) or checks < 0:
        errs.append("auditability_integrity_operations_checks_performed")
    return errs


def _validate_evidence(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return ["auditability_evidence"]
    errs: list[str] = []
    for key, expected_ref in _EVIDENCE_REFS.items():
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"auditability_evidence_{key}")
        elif value != expected_ref:
            errs.append(f"auditability_evidence_ref_mismatch:{key}")
    return errs


def _validate_status_semantics(body: dict[str, Any]) -> list[str]:
    status = body.get("status")
    hash_chain = body.get("hash_chain")
    integrity_ops = body.get("integrity_operations")
    if status not in _ALLOWED_STATUS or not isinstance(hash_chain, dict) or not isinstance(integrity_ops, dict):
        return []
    hash_chain_valid = hash_chain.get("hash_chain_valid")
    event_count = hash_chain.get("event_count")
    chain_root = hash_chain.get("chain_root")
    last_check_passed = integrity_ops.get("last_check_passed")
    if (
        not isinstance(hash_chain_valid, bool)
        or isinstance(event_count, bool)
        or not isinstance(event_count, int)
        or not isinstance(chain_root, str)
        or not isinstance(last_check_passed, bool)
    ):
        return []
    if status == "verifiable" and (not hash_chain_valid or not last_check_passed):
        return ["auditability_status_semantics_mismatch"]
    if status == "inconsistent" and event_count > 0 and chain_root != "missing":
        return ["auditability_status_semantics_mismatch"]
    return []


def validate_auditability_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["auditability_not_object"]
    errs: list[str] = []
    if body.get("schema") != AUDITABILITY_CONTRACT:
        errs.append("auditability_schema")
    if body.get("schema_version") != AUDITABILITY_SCHEMA_VERSION:
        errs.append("auditability_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("auditability_run_id")
    mode = body.get("mode")
    if mode not in _ALLOWED_MODES:
        errs.append("auditability_mode")
    status = body.get("status")
    if status not in _ALLOWED_STATUS:
        errs.append("auditability_status")
    errs.extend(_validate_execution(body.get("execution")))
    errs.extend(_validate_hash_chain(body.get("hash_chain")))
    errs.extend(_validate_integrity_operations(body.get("integrity_operations")))
    errs.extend(_validate_evidence(body.get("evidence")))
    if not errs:
        errs.extend(_validate_status_semantics(body))
    return errs


def validate_auditability_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["auditability_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["auditability_json"]
    return validate_auditability_dict(body)
