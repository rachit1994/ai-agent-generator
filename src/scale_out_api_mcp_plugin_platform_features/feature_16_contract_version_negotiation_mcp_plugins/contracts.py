"""Contracts for feature 16 contract-version negotiation."""

from __future__ import annotations

from typing import Any

VERSION_NEGOTIATION_SCHEMA = "sde.scale.feature_16.version_negotiation.v1"
VERSION_NEGOTIATION_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "handshake_ref": "data/version_negotiation/handshake.json",
    "compatibility_ref": "data/version_negotiation/compatibility.json",
    "telemetry_ref": "data/version_negotiation/telemetry.json",
    "history_ref": "data/version_negotiation/trend_history.jsonl",
}


def validate_version_negotiation_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["version_negotiation_not_object"]
    errors: list[str] = []
    if body.get("schema") != VERSION_NEGOTIATION_SCHEMA:
        errors.append("version_negotiation_schema")
    if body.get("schema_version") != VERSION_NEGOTIATION_SCHEMA_VERSION:
        errors.append("version_negotiation_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("version_negotiation_mode")
    if body.get("status") not in _STATUSES:
        errors.append("version_negotiation_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("version_negotiation_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("version_negotiation_failed_gates")
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "version_negotiation_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"version_negotiation_evidence_ref:{key}")
    return errors

