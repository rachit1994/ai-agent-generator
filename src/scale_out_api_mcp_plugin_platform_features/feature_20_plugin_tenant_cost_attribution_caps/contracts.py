"""Contracts for feature 20 per-plugin/per-tenant cost attribution and caps."""

from __future__ import annotations

from typing import Any

COST_ATTRIBUTION_SCHEMA = "sde.scale.feature_20.cost_attribution.v1"
COST_ATTRIBUTION_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "metering_ref": "data/cost_attribution/metering.json",
    "aggregation_ref": "data/cost_attribution/aggregation.json",
    "caps_ref": "data/cost_attribution/caps.json",
    "history_ref": "data/cost_attribution/trend_history.jsonl",
    "events_ref": "data/cost_attribution/cost_events.jsonl",
}


def _validate_execution(body: dict[str, Any]) -> list[str]:
    execution = body.get("execution")
    if not isinstance(execution, dict):
        return ["cost_attribution_execution"]
    errors: list[str] = []
    if not isinstance(execution.get("events_processed"), int):
        errors.append("cost_attribution_execution_field:events_processed")
    for field in ("tenant_totals", "plugin_totals"):
        if not isinstance(execution.get(field), dict):
            errors.append(f"cost_attribution_execution_field:{field}")
    for field in ("cap_violations", "billing_export_violations"):
        if not isinstance(execution.get(field), list):
            errors.append(f"cost_attribution_execution_field:{field}")
    return errors


def validate_cost_attribution_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["cost_attribution_not_object"]
    errors: list[str] = []
    if body.get("schema") != COST_ATTRIBUTION_SCHEMA:
        errors.append("cost_attribution_schema")
    if body.get("schema_version") != COST_ATTRIBUTION_SCHEMA_VERSION:
        errors.append("cost_attribution_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("cost_attribution_mode")
    if body.get("status") not in _STATUSES:
        errors.append("cost_attribution_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("cost_attribution_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("cost_attribution_failed_gates")
    errors.extend(_validate_execution(body))
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "cost_attribution_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"cost_attribution_evidence_ref:{key}")
    return errors

