from __future__ import annotations

from typing import Any

PLUGIN_CIRCUIT_BREAKER_SCHEMA = "sde.scale.feature_09.plugin_circuit_breakers.v1"
PLUGIN_CIRCUIT_BREAKER_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "runtime_ref": "data/plugin_circuit_breakers/runtime_state.json",
    "policy_ref": "data/plugin_circuit_breakers/policy.json",
    "telemetry_ref": "data/plugin_circuit_breakers/telemetry.json",
    "history_ref": "data/plugin_circuit_breakers/trend_history.jsonl",
    "events_ref": "data/plugin_circuit_breakers/transition_events.jsonl",
}


def _validate_execution(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["plugin_circuit_breaker_execution"]
    errors = _validate_state_counts(payload.get("state_counts"))
    errors.extend(_validate_retry_budget(payload.get("retry_budget")))
    errors.extend(_validate_fallback(payload.get("fallback")))
    if not isinstance(payload.get("runtime_failures"), list):
        errors.append("plugin_circuit_breaker_runtime_failures")
    return errors


def _validate_state_counts(state_counts: Any) -> list[str]:
    if not isinstance(state_counts, dict):
        return ["plugin_circuit_breaker_state_counts"]
    errors: list[str] = []
    for key in ("open", "half_open", "closed"):
        if not isinstance(state_counts.get(key), int):
            errors.append(f"plugin_circuit_breaker_state_count:{key}")
    return errors


def _validate_retry_budget(retry_budget: Any) -> list[str]:
    if not isinstance(retry_budget, dict):
        return ["plugin_circuit_breaker_retry_budget"]
    errors: list[str] = []
    for key in ("limit", "remaining_before", "consumed", "remaining_after"):
        if not isinstance(retry_budget.get(key), int):
            errors.append(f"plugin_circuit_breaker_retry_budget:{key}")
    if not isinstance(retry_budget.get("saturation"), bool):
        errors.append("plugin_circuit_breaker_retry_budget:saturation")
    return errors


def _validate_fallback(fallback: Any) -> list[str]:
    if not isinstance(fallback, dict):
        return ["plugin_circuit_breaker_fallback"]
    errors: list[str] = []
    if fallback.get("mode") not in {"serve_cached", "fail_fast"}:
        errors.append("plugin_circuit_breaker_fallback:mode")
    if not isinstance(fallback.get("activations"), int):
        errors.append("plugin_circuit_breaker_fallback:activations")
    if not isinstance(fallback.get("cooldown_seconds"), int):
        errors.append("plugin_circuit_breaker_fallback:cooldown_seconds")
    return errors


def _validate_top_level(body: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if body.get("schema") != PLUGIN_CIRCUIT_BREAKER_SCHEMA:
        errors.append("plugin_circuit_breaker_schema")
    if body.get("schema_version") != PLUGIN_CIRCUIT_BREAKER_SCHEMA_VERSION:
        errors.append("plugin_circuit_breaker_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("plugin_circuit_breaker_mode")
    if body.get("status") not in _STATUSES:
        errors.append("plugin_circuit_breaker_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("plugin_circuit_breaker_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("plugin_circuit_breaker_failed_gates")
    return errors


def validate_plugin_circuit_breaker_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["plugin_circuit_breaker_not_object"]
    errors = _validate_top_level(body)
    errors.extend(_validate_execution(body.get("breaker_execution")))
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "plugin_circuit_breaker_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"plugin_circuit_breaker_evidence_ref:{key}")
    return errors
