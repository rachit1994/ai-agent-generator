"""Contracts for feature 23 scale failure drills."""

from __future__ import annotations

from typing import Any

FAILURE_DRILLS_SCHEMA = "sde.scale.feature_23.failure_drills.v1"
FAILURE_DRILLS_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "drills_ref": "data/failure_drills/drills.json",
    "slo_ref": "data/failure_drills/slo_assertions.json",
    "remediation_ref": "data/failure_drills/remediation.json",
    "history_ref": "data/failure_drills/trend_history.jsonl",
    "events_ref": "data/failure_drills/drill_events.jsonl",
}


def _validate_execution_metrics(metrics: Any) -> list[str]:
    if not isinstance(metrics, dict):
        return ["failure_drills_metrics"]
    errors: list[str] = []
    for key in (
        "avg_429_error_rate_pct",
        "avg_queue_lag_seconds",
        "avg_restart_recovery_seconds",
    ):
        if not isinstance(metrics.get(key), (int, float)):
            errors.append(f"failure_drills_metric:{key}")
    return errors


def _validate_execution_regression(regression: Any) -> list[str]:
    if not isinstance(regression, dict):
        return ["failure_drills_regression"]
    errors: list[str] = []
    for key in ("regression_detected", "alerts_emitted", "remediation_verified"):
        if not isinstance(regression.get(key), bool):
            errors.append(f"failure_drills_regression:{key}")
    if not isinstance(regression.get("missing_verified_runbooks"), list):
        errors.append("failure_drills_regression:missing_verified_runbooks")
    return errors


def _validate_drill_execution(execution: Any) -> list[str]:
    if not isinstance(execution, dict):
        return ["failure_drills_drill_execution"]
    errors: list[str] = []
    if not isinstance(execution.get("scenario_count"), int):
        errors.append("failure_drills_scenario_count")
    if not isinstance(execution.get("passed_scenarios"), int):
        errors.append("failure_drills_passed_scenarios")
    if not isinstance(execution.get("failed_scenarios"), list):
        errors.append("failure_drills_failed_scenarios")
    errors.extend(_validate_execution_metrics(execution.get("metrics")))
    errors.extend(_validate_execution_regression(execution.get("regression")))
    if not isinstance(execution.get("timeline"), list):
        errors.append("failure_drills_timeline")
    return errors


def validate_failure_drills_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["failure_drills_not_object"]
    errors: list[str] = []
    if body.get("schema") != FAILURE_DRILLS_SCHEMA:
        errors.append("failure_drills_schema")
    if body.get("schema_version") != FAILURE_DRILLS_SCHEMA_VERSION:
        errors.append("failure_drills_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("failure_drills_mode")
    if body.get("status") not in _STATUSES:
        errors.append("failure_drills_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("failure_drills_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("failure_drills_failed_gates")
    errors.extend(_validate_drill_execution(body.get("drill_execution")))
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "failure_drills_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"failure_drills_evidence_ref:{key}")
    return errors

