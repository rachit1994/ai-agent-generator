"""Contracts for feature 21 artifact keying parity gate."""

from __future__ import annotations

from typing import Any

ARTIFACT_KEY_PARITY_SCHEMA = "sde.scale.feature_21.artifact_key_parity.v1"
ARTIFACT_KEY_PARITY_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "local_index_ref": "data/artifact_key_parity/local_index.json",
    "object_index_ref": "data/artifact_key_parity/object_index.json",
    "migration_ref": "data/artifact_key_parity/migration_state.json",
    "history_ref": "data/artifact_key_parity/trend_history.jsonl",
    "reconciliation_ref": "data/artifact_key_parity/reconciliation_details.json",
}


def _validate_reconciliation(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["artifact_key_parity_reconciliation"]
    errors: list[str] = []
    errors.extend(_validate_reconciliation_counts(payload.get("counts")))
    errors.extend(_validate_reconciliation_drift(payload.get("drift")))
    if not isinstance(payload.get("parity_ok"), bool):
        errors.append("artifact_key_parity_reconciliation_parity_ok")
    return errors


def _validate_reconciliation_counts(counts: Any) -> list[str]:
    if not isinstance(counts, dict):
        return ["artifact_key_parity_reconciliation_counts"]
    errors: list[str] = []
    for key in ("local_artifacts", "object_artifacts", "shared_artifacts"):
        if not isinstance(counts.get(key), int):
            errors.append(f"artifact_key_parity_reconciliation_count:{key}")
    return errors


def _validate_reconciliation_drift(drift: Any) -> list[str]:
    if not isinstance(drift, dict):
        return ["artifact_key_parity_reconciliation_drift"]
    errors: list[str] = []
    for key in (
        "missing_in_object",
        "missing_in_local",
        "key_mismatches",
        "checksum_mismatches",
        "canonical_key_violations",
        "migration_failures",
    ):
        if not isinstance(drift.get(key), list):
            errors.append(f"artifact_key_parity_reconciliation_drift:{key}")
    if not isinstance(drift.get("collisions_detected"), bool):
        errors.append("artifact_key_parity_reconciliation_drift:collisions_detected")
    return errors


def _validate_top_level(body: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if body.get("schema") != ARTIFACT_KEY_PARITY_SCHEMA:
        errors.append("artifact_key_parity_schema")
    if body.get("schema_version") != ARTIFACT_KEY_PARITY_SCHEMA_VERSION:
        errors.append("artifact_key_parity_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("artifact_key_parity_mode")
    if body.get("status") not in _STATUSES:
        errors.append("artifact_key_parity_status")
    if not isinstance(body.get("run_id"), str) or not body["run_id"].strip():
        errors.append("artifact_key_parity_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("artifact_key_parity_failed_gates")
    return errors


def validate_artifact_key_parity_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["artifact_key_parity_not_object"]
    errors = _validate_top_level(body)
    errors.extend(_validate_reconciliation(body.get("reconciliation")))
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "artifact_key_parity_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"artifact_key_parity_evidence_ref:{key}")
    return errors

