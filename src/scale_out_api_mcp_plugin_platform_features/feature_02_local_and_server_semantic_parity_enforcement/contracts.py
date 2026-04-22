"""Contracts for feature 02 semantic parity enforcement."""

from __future__ import annotations

from typing import Any

SEMANTIC_PARITY_SCHEMA = "sde.scale.feature_02.semantic_parity.v1"
SEMANTIC_PARITY_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "parity_matrix_ref": "data/semantic_parity/parity_matrix.json",
    "local_ref": "data/semantic_parity/local_runtime.json",
    "server_ref": "data/semantic_parity/server_runtime.json",
    "history_ref": "data/semantic_parity/trend_history.jsonl",
}


def validate_semantic_parity_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["semantic_parity_not_object"]
    errors: list[str] = []
    if body.get("schema") != SEMANTIC_PARITY_SCHEMA:
        errors.append("semantic_parity_schema")
    if body.get("schema_version") != SEMANTIC_PARITY_SCHEMA_VERSION:
        errors.append("semantic_parity_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("semantic_parity_mode")
    if body.get("status") not in _STATUSES:
        errors.append("semantic_parity_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("semantic_parity_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("semantic_parity_failed_gates")
    if not isinstance(body.get("drift"), dict):
        errors.append("semantic_parity_drift")
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        errors.append("semantic_parity_evidence")
        return errors
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"semantic_parity_evidence_ref:{key}")
    return errors

