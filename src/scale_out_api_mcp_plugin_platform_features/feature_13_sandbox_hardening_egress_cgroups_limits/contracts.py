"""Contracts for feature 13 sandbox hardening."""

from __future__ import annotations

from typing import Any

SANDBOX_HARDENING_SCHEMA = "sde.scale.feature_13.sandbox_hardening.v1"
SANDBOX_HARDENING_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "policy_ref": "data/sandbox_hardening/policy.json",
    "runtime_ref": "data/sandbox_hardening/runtime_state.json",
    "audit_ref": "data/sandbox_hardening/audit_logs.json",
    "history_ref": "data/sandbox_hardening/trend_history.jsonl",
    "events_ref": "data/sandbox_hardening/runtime_events.jsonl",
}


def _validate_execution(body: dict[str, Any]) -> list[str]:
    execution = body.get("execution")
    if not isinstance(execution, dict):
        return ["sandbox_hardening_execution"]
    errors: list[str] = []
    if not isinstance(execution.get("events_processed"), int):
        errors.append("sandbox_hardening_execution_field:events_processed")
    for field in ("egress_violations", "resource_violations", "escape_violations"):
        if not isinstance(execution.get(field), list):
            errors.append(f"sandbox_hardening_execution_field:{field}")
    if not isinstance(execution.get("audit_count_coherent"), bool):
        errors.append("sandbox_hardening_execution_field:audit_count_coherent")
    return errors


def validate_sandbox_hardening_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["sandbox_hardening_not_object"]
    errors: list[str] = []
    if body.get("schema") != SANDBOX_HARDENING_SCHEMA:
        errors.append("sandbox_hardening_schema")
    if body.get("schema_version") != SANDBOX_HARDENING_SCHEMA_VERSION:
        errors.append("sandbox_hardening_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("sandbox_hardening_mode")
    if body.get("status") not in _STATUSES:
        errors.append("sandbox_hardening_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("sandbox_hardening_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("sandbox_hardening_failed_gates")
    errors.extend(_validate_execution(body))
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "sandbox_hardening_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"sandbox_hardening_evidence_ref:{key}")
    return errors

