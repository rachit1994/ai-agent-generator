"""Contracts for feature 24 incident runbooks gate."""

from __future__ import annotations

from typing import Any

INCIDENT_RUNBOOKS_SCHEMA = "sde.scale.feature_24.incident_runbooks.v1"
INCIDENT_RUNBOOKS_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "runbooks_ref": "data/incident_runbooks/runbooks.json",
    "ops_ref": "data/incident_runbooks/operations.json",
    "drills_ref": "data/incident_runbooks/drills.json",
    "history_ref": "data/incident_runbooks/trend_history.jsonl",
}


def validate_incident_runbooks_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["incident_runbooks_not_object"]
    errors: list[str] = []
    if body.get("schema") != INCIDENT_RUNBOOKS_SCHEMA:
        errors.append("incident_runbooks_schema")
    if body.get("schema_version") != INCIDENT_RUNBOOKS_SCHEMA_VERSION:
        errors.append("incident_runbooks_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("incident_runbooks_mode")
    if body.get("status") not in _STATUSES:
        errors.append("incident_runbooks_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("incident_runbooks_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("incident_runbooks_failed_gates")
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "incident_runbooks_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"incident_runbooks_evidence_ref:{key}")
    return errors

