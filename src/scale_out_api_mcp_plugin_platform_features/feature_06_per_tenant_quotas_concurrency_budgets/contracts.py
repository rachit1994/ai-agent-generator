"""Contracts for feature 06 tenant quotas and concurrency budgets."""

from __future__ import annotations

from typing import Any

TENANT_QUOTA_SCHEMA = "sde.scale.feature_06.tenant_quota.v1"
TENANT_QUOTA_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "quota_ref": "data/tenant_quotas/quota_state.json",
    "scheduler_ref": "data/tenant_quotas/scheduler_state.json",
    "observability_ref": "data/tenant_quotas/observability.json",
    "history_ref": "data/tenant_quotas/trend_history.jsonl",
    "events_ref": "data/tenant_quotas/quota_events.jsonl",
}


def _validate_execution(body: dict[str, Any]) -> list[str]:
    execution = body.get("execution")
    if not isinstance(execution, dict):
        return ["tenant_quota_execution"]
    errors: list[str] = []
    if not isinstance(execution.get("events_processed"), int):
        errors.append("tenant_quota_execution_field:events_processed")
    for field in ("cap_violations", "missing_reason_violations"):
        if not isinstance(execution.get(field), list):
            errors.append(f"tenant_quota_execution_field:{field}")
    if not isinstance(execution.get("rejection_count_coherent"), bool):
        errors.append("tenant_quota_execution_field:rejection_count_coherent")
    return errors


def validate_tenant_quota_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["tenant_quota_not_object"]
    errors: list[str] = []
    if body.get("schema") != TENANT_QUOTA_SCHEMA:
        errors.append("tenant_quota_schema")
    if body.get("schema_version") != TENANT_QUOTA_SCHEMA_VERSION:
        errors.append("tenant_quota_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("tenant_quota_mode")
    if body.get("status") not in _STATUSES:
        errors.append("tenant_quota_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("tenant_quota_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("tenant_quota_failed_gates")
    errors.extend(_validate_execution(body))
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "tenant_quota_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"tenant_quota_evidence_ref:{key}")
    return errors

