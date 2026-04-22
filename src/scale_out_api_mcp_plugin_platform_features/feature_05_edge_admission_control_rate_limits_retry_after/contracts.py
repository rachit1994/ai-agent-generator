"""Contracts for feature 05 edge admission control."""

from __future__ import annotations

from typing import Any

EDGE_ADMISSION_SCHEMA = "sde.scale.feature_05.edge_admission.v1"
EDGE_ADMISSION_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "policy_ref": "data/edge_admission/policy.json",
    "counters_ref": "data/edge_admission/counters.json",
    "traffic_ref": "data/edge_admission/traffic_sample.json",
    "history_ref": "data/edge_admission/trend_history.jsonl",
    "events_ref": "data/edge_admission/admission_events.jsonl",
}


def _validate_execution(body: dict[str, Any]) -> list[str]:
    execution = body.get("execution")
    if not isinstance(execution, dict):
        return ["edge_admission_execution"]
    errors: list[str] = []
    if not isinstance(execution.get("events_processed"), int):
        errors.append("edge_admission_execution_field:events_processed")
    for field in ("retry_after_violations", "scope_violations"):
        if not isinstance(execution.get(field), list):
            errors.append(f"edge_admission_execution_field:{field}")
    if not isinstance(execution.get("counter_coherent"), bool):
        errors.append("edge_admission_execution_field:counter_coherent")
    return errors


def validate_edge_admission_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["edge_admission_not_object"]
    errors: list[str] = []
    if body.get("schema") != EDGE_ADMISSION_SCHEMA:
        errors.append("edge_admission_schema")
    if body.get("schema_version") != EDGE_ADMISSION_SCHEMA_VERSION:
        errors.append("edge_admission_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("edge_admission_mode")
    if body.get("status") not in _STATUSES:
        errors.append("edge_admission_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("edge_admission_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("edge_admission_failed_gates")
    errors.extend(_validate_execution(body))
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "edge_admission_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"edge_admission_evidence_ref:{key}")
    return errors

