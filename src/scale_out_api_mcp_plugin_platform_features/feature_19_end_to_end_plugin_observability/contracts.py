"""Contracts for feature 19 end-to-end plugin observability."""

from __future__ import annotations

from typing import Any

PLUGIN_OBSERVABILITY_SCHEMA = "sde.scale.feature_19.plugin_observability.v1"
PLUGIN_OBSERVABILITY_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "spans_ref": "data/plugin_observability/spans.jsonl",
    "metrics_ref": "data/plugin_observability/metrics.json",
    "retention_ref": "data/plugin_observability/retention_policy.json",
    "history_ref": "data/plugin_observability/trend_history.jsonl",
    "events_ref": "data/plugin_observability/observability_events.jsonl",
}


def _validate_execution(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["plugin_observability_execution"]
    errors: list[str] = []
    int_fields = (
        "event_count",
        "error_count",
        "plugin_count",
        "tenant_count",
        "correlation_count",
        "retention_days",
    )
    for key in int_fields:
        if not isinstance(payload.get(key), int):
            errors.append(f"plugin_observability_execution:{key}")
    if not isinstance(payload.get("sampling_rate"), (int, float)):
        errors.append("plugin_observability_execution:sampling_rate")
    for key in ("continuity_ok", "trace_stitch_ok"):
        if not isinstance(payload.get(key), bool):
            errors.append(f"plugin_observability_execution:{key}")
    stage_counts = payload.get("stage_counts")
    if not isinstance(stage_counts, dict):
        errors.append("plugin_observability_execution:stage_counts")
    else:
        for stage in ("api", "mcp", "runtime"):
            if not isinstance(stage_counts.get(stage), int):
                errors.append(f"plugin_observability_execution:stage:{stage}")
    return errors


def validate_plugin_observability_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["plugin_observability_not_object"]
    errors: list[str] = []
    if body.get("schema") != PLUGIN_OBSERVABILITY_SCHEMA:
        errors.append("plugin_observability_schema")
    if body.get("schema_version") != PLUGIN_OBSERVABILITY_SCHEMA_VERSION:
        errors.append("plugin_observability_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("plugin_observability_mode")
    if body.get("status") not in _STATUSES:
        errors.append("plugin_observability_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("plugin_observability_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("plugin_observability_failed_gates")
    errors.extend(_validate_execution(body.get("execution")))
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "plugin_observability_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"plugin_observability_evidence_ref:{key}")
    return errors

