"""Contracts for feature 12 plugin/runtime bulkheads by trust class."""

from __future__ import annotations

from typing import Any

BULKHEADS_SCHEMA = "sde.scale.feature_12.bulkheads.v1"
BULKHEADS_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "policy_ref": "data/trust_bulkheads/policy.json",
    "runtime_ref": "data/trust_bulkheads/runtime_state.json",
    "telemetry_ref": "data/trust_bulkheads/telemetry.json",
    "history_ref": "data/trust_bulkheads/trend_history.jsonl",
    "events_ref": "data/trust_bulkheads/bulkhead_events.jsonl",
}


def _validate_execution(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["bulkheads_execution"]
    errors: list[str] = []
    if not isinstance(payload.get("events_processed"), int):
        errors.append("bulkheads_execution:events_processed")
    errors.extend(_validate_usage_by_class(payload.get("usage_by_class")))
    for key in ("leakage_events", "quota_breaches", "pool_violations"):
        if not isinstance(payload.get(key), list):
            errors.append(f"bulkheads_execution:{key}")
    if not isinstance(payload.get("reclassifications_count"), int):
        errors.append("bulkheads_execution:reclassifications_count")
    for key in ("reclassification_safe", "telemetry_consistent"):
        if not isinstance(payload.get(key), bool):
            errors.append(f"bulkheads_execution:{key}")
    return errors


def _validate_usage_by_class(usage: Any) -> list[str]:
    if not isinstance(usage, dict):
        return ["bulkheads_execution:usage_by_class"]
    errors: list[str] = []
    for trust_class in ("trusted", "sandboxed", "untrusted"):
        if trust_class in usage and not isinstance(usage.get(trust_class), int):
            errors.append(f"bulkheads_execution:usage:{trust_class}")
    return errors


def validate_bulkheads_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["bulkheads_not_object"]
    errors: list[str] = []
    if body.get("schema") != BULKHEADS_SCHEMA:
        errors.append("bulkheads_schema")
    if body.get("schema_version") != BULKHEADS_SCHEMA_VERSION:
        errors.append("bulkheads_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("bulkheads_mode")
    if body.get("status") not in _STATUSES:
        errors.append("bulkheads_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("bulkheads_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("bulkheads_failed_gates")
    errors.extend(_validate_execution(body.get("execution")))
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "bulkheads_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"bulkheads_evidence_ref:{key}")
    return errors

