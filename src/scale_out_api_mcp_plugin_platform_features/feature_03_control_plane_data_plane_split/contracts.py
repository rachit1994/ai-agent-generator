"""Contracts for feature 03 control/data plane split."""

from __future__ import annotations

from typing import Any

PLANE_SPLIT_SCHEMA = "sde.scale.feature_03.plane_split.v1"
PLANE_SPLIT_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "control_ref": "data/plane_split/control_plane.json",
    "data_ref": "data/plane_split/data_plane.json",
    "boundary_ref": "data/plane_split/boundary_contract.json",
    "history_ref": "data/plane_split/trend_history.jsonl",
    "events_ref": "data/plane_split/plane_events.jsonl",
}


def _validate_execution(body: dict[str, Any]) -> list[str]:
    execution = body.get("execution")
    if not isinstance(execution, dict):
        return ["plane_split_execution"]
    errors: list[str] = []
    int_fields = ("events_processed",)
    for field in int_fields:
        if not isinstance(execution.get(field), int):
            errors.append(f"plane_split_execution_field:{field}")
    list_fields = ("route_violations", "dependency_violations", "ownership_violations")
    for field in list_fields:
        if not isinstance(execution.get(field), list):
            errors.append(f"plane_split_execution_field:{field}")
    if not isinstance(execution.get("rollback_ready"), bool):
        errors.append("plane_split_execution_field:rollback_ready")
    return errors


def validate_plane_split_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["plane_split_not_object"]
    errors: list[str] = []
    if body.get("schema") != PLANE_SPLIT_SCHEMA:
        errors.append("plane_split_schema")
    if body.get("schema_version") != PLANE_SPLIT_SCHEMA_VERSION:
        errors.append("plane_split_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("plane_split_mode")
    if body.get("status") not in _STATUSES:
        errors.append("plane_split_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("plane_split_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("plane_split_failed_gates")
    errors.extend(_validate_execution(body))
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "plane_split_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"plane_split_evidence_ref:{key}")
    return errors

