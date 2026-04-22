"""Contracts for feature 22 plugin progressive rollout gate."""

from __future__ import annotations

from typing import Any

PLUGIN_ROLLOUT_SCHEMA = "sde.scale.feature_22.plugin_rollout.v1"
PLUGIN_ROLLOUT_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "controller_ref": "data/plugin_rollout/controller_state.json",
    "health_ref": "data/plugin_rollout/health_signals.json",
    "operations_ref": "data/plugin_rollout/operations_state.json",
    "history_ref": "data/plugin_rollout/trend_history.jsonl",
}


def validate_plugin_rollout_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["plugin_rollout_not_object"]
    errors: list[str] = []
    if body.get("schema") != PLUGIN_ROLLOUT_SCHEMA:
        errors.append("plugin_rollout_schema")
    if body.get("schema_version") != PLUGIN_ROLLOUT_SCHEMA_VERSION:
        errors.append("plugin_rollout_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("plugin_rollout_mode")
    if body.get("status") not in _STATUSES:
        errors.append("plugin_rollout_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("plugin_rollout_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("plugin_rollout_failed_gates")
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "plugin_rollout_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"plugin_rollout_evidence_ref:{key}")
    return errors

