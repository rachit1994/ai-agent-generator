"""Contracts for feature 08 distributed queue fairness gate."""

from __future__ import annotations

from typing import Any

WEIGHTED_QUEUE_FAIRNESS_SCHEMA = "sde.scale.feature_08.weighted_queue_fairness.v1"
WEIGHTED_QUEUE_FAIRNESS_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "scheduler_ref": "data/weighted_queue_fairness/scheduler_state.json",
    "telemetry_ref": "data/weighted_queue_fairness/telemetry.json",
    "policy_ref": "data/weighted_queue_fairness/policy.json",
    "history_ref": "data/weighted_queue_fairness/trend_history.jsonl",
    "events_ref": "data/weighted_queue_fairness/scheduler_events.jsonl",
}


def _validate_execution(body: dict[str, Any]) -> list[str]:
    execution = body.get("execution")
    if not isinstance(execution, dict):
        return ["weighted_queue_fairness_execution"]
    errors: list[str] = []
    if not isinstance(execution.get("events_processed"), int):
        errors.append("weighted_queue_fairness_execution_field:events_processed")
    for field in ("starvation_violations", "weighting_violations"):
        if not isinstance(execution.get(field), list):
            errors.append(f"weighted_queue_fairness_execution_field:{field}")
    if not isinstance(execution.get("max_tenant_drop_share"), (int, float)):
        errors.append("weighted_queue_fairness_execution_field:max_tenant_drop_share")
    for field in ("deterministic_replay_ok", "fairness_score_ok"):
        if not isinstance(execution.get(field), bool):
            errors.append(f"weighted_queue_fairness_execution_field:{field}")
    return errors


def validate_weighted_queue_fairness_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["weighted_queue_fairness_not_object"]
    errors: list[str] = []
    if body.get("schema") != WEIGHTED_QUEUE_FAIRNESS_SCHEMA:
        errors.append("weighted_queue_fairness_schema")
    if body.get("schema_version") != WEIGHTED_QUEUE_FAIRNESS_SCHEMA_VERSION:
        errors.append("weighted_queue_fairness_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("weighted_queue_fairness_mode")
    if body.get("status") not in _STATUSES:
        errors.append("weighted_queue_fairness_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("weighted_queue_fairness_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("weighted_queue_fairness_failed_gates")
    errors.extend(_validate_execution(body))
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "weighted_queue_fairness_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"weighted_queue_fairness_evidence_ref:{key}")
    return errors

