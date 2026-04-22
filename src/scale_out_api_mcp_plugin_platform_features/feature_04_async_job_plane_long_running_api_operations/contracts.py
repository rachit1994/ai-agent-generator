"""Contracts for feature 04 async job plane."""

from __future__ import annotations

from typing import Any

ASYNC_JOB_PLANE_SCHEMA = "sde.scale.feature_04.async_job_plane.v1"
ASYNC_JOB_PLANE_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "queue_ref": "data/async_job_plane/queue_state.json",
    "workers_ref": "data/async_job_plane/workers.json",
    "dlq_ref": "data/async_job_plane/dlq.json",
    "history_ref": "data/async_job_plane/trend_history.jsonl",
    "events_ref": "data/async_job_plane/job_events.jsonl",
}


def _validate_execution(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["async_job_plane_execution"]
    errors: list[str] = []
    for key in ("worker_count", "total_capacity", "jobs_processed", "queue_depth", "queue_lag_seconds", "dlq_count"):
        if not isinstance(payload.get(key), int):
            errors.append(f"async_job_plane_execution:{key}")
    if not isinstance(payload.get("queue_lag_breach"), bool):
        errors.append("async_job_plane_execution:queue_lag_breach")
    state_counts = payload.get("state_counts")
    if not isinstance(state_counts, dict):
        errors.append("async_job_plane_execution:state_counts")
    else:
        for state in ("queued", "running", "succeeded", "failed", "cancelled"):
            if not isinstance(state_counts.get(state), int):
                errors.append(f"async_job_plane_execution:state:{state}")
    if not isinstance(payload.get("events"), list):
        errors.append("async_job_plane_execution:events")
    return errors


def validate_async_job_plane_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["async_job_plane_not_object"]
    errors: list[str] = []
    if body.get("schema") != ASYNC_JOB_PLANE_SCHEMA:
        errors.append("async_job_plane_schema")
    if body.get("schema_version") != ASYNC_JOB_PLANE_SCHEMA_VERSION:
        errors.append("async_job_plane_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("async_job_plane_mode")
    if body.get("status") not in _STATUSES:
        errors.append("async_job_plane_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("async_job_plane_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("async_job_plane_failed_gates")
    errors.extend(_validate_execution(body.get("execution")))
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "async_job_plane_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"async_job_plane_evidence_ref:{key}")
    return errors

