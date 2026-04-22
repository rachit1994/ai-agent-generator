"""Contracts for feature 17 plugin authz scopes."""

from __future__ import annotations

from typing import Any

PLUGIN_AUTHZ_SCHEMA = "sde.scale.feature_17.plugin_authz.v1"
PLUGIN_AUTHZ_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "taxonomy_ref": "data/plugin_authz/taxonomy.json",
    "policy_ref": "data/plugin_authz/policy_state.json",
    "audit_ref": "data/plugin_authz/audit_logs.json",
    "history_ref": "data/plugin_authz/trend_history.jsonl",
    "events_ref": "data/plugin_authz/authz_events.jsonl",
}


def _validate_execution(body: dict[str, Any]) -> list[str]:
    execution = body.get("execution")
    if not isinstance(execution, dict):
        return ["plugin_authz_execution"]
    errors: list[str] = []
    if not isinstance(execution.get("events_processed"), int):
        errors.append("plugin_authz_execution_field:events_processed")
    for field in ("decision_violations", "unknown_scope_violations"):
        if not isinstance(execution.get(field), list):
            errors.append(f"plugin_authz_execution_field:{field}")
    if not isinstance(execution.get("decision_counter_coherent"), bool):
        errors.append("plugin_authz_execution_field:decision_counter_coherent")
    return errors


def validate_plugin_authz_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["plugin_authz_not_object"]
    errors: list[str] = []
    if body.get("schema") != PLUGIN_AUTHZ_SCHEMA:
        errors.append("plugin_authz_schema")
    if body.get("schema_version") != PLUGIN_AUTHZ_SCHEMA_VERSION:
        errors.append("plugin_authz_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("plugin_authz_mode")
    if body.get("status") not in _STATUSES:
        errors.append("plugin_authz_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("plugin_authz_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("plugin_authz_failed_gates")
    errors.extend(_validate_execution(body))
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "plugin_authz_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"plugin_authz_evidence_ref:{key}")
    return errors

