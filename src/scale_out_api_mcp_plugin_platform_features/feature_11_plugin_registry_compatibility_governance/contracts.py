"""Contracts for feature 11 plugin registry compatibility governance."""

from __future__ import annotations

from typing import Any

PLUGIN_REGISTRY_SCHEMA = "sde.scale.feature_11.plugin_registry.v1"
PLUGIN_REGISTRY_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "registry_ref": "data/plugin_registry/registry_state.json",
    "compatibility_ref": "data/plugin_registry/compatibility_matrix.json",
    "governance_ref": "data/plugin_registry/governance.json",
    "history_ref": "data/plugin_registry/trend_history.jsonl",
    "events_ref": "data/plugin_registry/registry_events.jsonl",
}


def _validate_execution(body: dict[str, Any]) -> list[str]:
    execution = body.get("execution")
    if not isinstance(execution, dict):
        return ["plugin_registry_execution"]
    errors: list[str] = []
    if not isinstance(execution.get("events_processed"), int):
        errors.append("plugin_registry_execution_field:events_processed")
    for field in ("decision_violations", "canary_violations"):
        if not isinstance(execution.get(field), list):
            errors.append(f"plugin_registry_execution_field:{field}")
    if not isinstance(execution.get("matrix_coverage_ok"), bool):
        errors.append("plugin_registry_execution_field:matrix_coverage_ok")
    return errors


def validate_plugin_registry_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["plugin_registry_not_object"]
    errors: list[str] = []
    if body.get("schema") != PLUGIN_REGISTRY_SCHEMA:
        errors.append("plugin_registry_schema")
    if body.get("schema_version") != PLUGIN_REGISTRY_SCHEMA_VERSION:
        errors.append("plugin_registry_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("plugin_registry_mode")
    if body.get("status") not in _STATUSES:
        errors.append("plugin_registry_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("plugin_registry_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("plugin_registry_failed_gates")
    errors.extend(_validate_execution(body))
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "plugin_registry_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"plugin_registry_evidence_ref:{key}")
    return errors

