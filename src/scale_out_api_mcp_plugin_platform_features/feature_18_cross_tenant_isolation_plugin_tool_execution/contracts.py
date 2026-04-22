"""Contracts for feature 18 cross-tenant isolation."""

from __future__ import annotations

from typing import Any

CROSS_TENANT_SCHEMA = "sde.scale.feature_18.cross_tenant_isolation.v1"
CROSS_TENANT_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "execution_ref": "data/cross_tenant_isolation/execution_context.json",
    "isolation_ref": "data/cross_tenant_isolation/isolation_state.json",
    "audit_ref": "data/cross_tenant_isolation/audit_signals.json",
    "history_ref": "data/cross_tenant_isolation/trend_history.jsonl",
    "events_ref": "data/cross_tenant_isolation/isolation_events.jsonl",
}


def _validate_execution(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["cross_tenant_execution"]
    errors: list[str] = []
    int_fields = ("events_processed", "adversarial_tests_count")
    for key in int_fields:
        if not isinstance(payload.get(key), int):
            errors.append(f"cross_tenant_execution:{key}")
    for key in ("leakage_attempts", "namespace_violations", "key_scope_violations"):
        if not isinstance(payload.get(key), list):
            errors.append(f"cross_tenant_execution:{key}")
    for key in ("adversarial_pass", "containment_ready"):
        if not isinstance(payload.get(key), bool):
            errors.append(f"cross_tenant_execution:{key}")
    return errors


def validate_cross_tenant_isolation_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["cross_tenant_not_object"]
    errors: list[str] = []
    if body.get("schema") != CROSS_TENANT_SCHEMA:
        errors.append("cross_tenant_schema")
    if body.get("schema_version") != CROSS_TENANT_SCHEMA_VERSION:
        errors.append("cross_tenant_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("cross_tenant_mode")
    if body.get("status") not in _STATUSES:
        errors.append("cross_tenant_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("cross_tenant_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("cross_tenant_failed_gates")
    errors.extend(_validate_execution(body.get("execution")))
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "cross_tenant_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"cross_tenant_evidence_ref:{key}")
    return errors

