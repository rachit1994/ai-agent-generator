"""Runtime for feature 04 async job plane."""

from __future__ import annotations

from typing import Any

from .contracts import ASYNC_JOB_PLANE_SCHEMA, ASYNC_JOB_PLANE_SCHEMA_VERSION


def build_job_lifecycle_contract() -> dict[str, object]:
    return {
        "submit_response": "202 + job_id",
        "status_states": ["queued", "running", "succeeded", "failed", "cancelled"],
        "api": ["submit", "get", "cancel", "retry"],
        "delivery_guarantee": "at_least_once_with_idempotency_key",
    }


def _worker_lease_policy_aligned(queue_state: dict[str, Any], workers: dict[str, Any]) -> bool:
    queue_policy_version = queue_state.get("worker_lease_policy_version")
    workers_policy_version = workers.get("worker_lease_policy_version")
    return (
        isinstance(queue_policy_version, str)
        and queue_policy_version.strip() != ""
        and queue_policy_version == workers_policy_version
    )


def _dlq_policy_aligned(queue_state: dict[str, Any], dlq: dict[str, Any]) -> bool:
    queue_policy_version = queue_state.get("dlq_policy_version")
    dlq_policy_version = dlq.get("dlq_policy_version")
    return (
        isinstance(queue_policy_version, str)
        and queue_policy_version.strip() != ""
        and queue_policy_version == dlq_policy_version
    )


def _heartbeat_interval_aligned(queue_state: dict[str, Any], workers: dict[str, Any]) -> bool:
    queue_heartbeat_seconds = queue_state.get("worker_heartbeat_interval_seconds")
    workers_heartbeat_seconds = workers.get("worker_heartbeat_interval_seconds")
    return (
        isinstance(queue_heartbeat_seconds, int)
        and queue_heartbeat_seconds > 0
        and queue_heartbeat_seconds == workers_heartbeat_seconds
    )


def _valid_job_row(row: Any) -> bool:
    if not isinstance(row, dict):
        return False
    if not isinstance(row.get("job_id"), str) or not row["job_id"].strip():
        return False
    if row.get("status") not in {"queued", "running", "succeeded", "failed", "cancelled"}:
        return False
    return isinstance(row.get("attempt"), int) and row.get("attempt") >= 0


def _collect_jobs(queue_state: dict[str, Any]) -> list[dict[str, Any]]:
    rows = queue_state.get("jobs")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if _valid_job_row(row)]


def _collect_worker_rows(workers: dict[str, Any]) -> list[dict[str, Any]]:
    rows = workers.get("workers")
    if not isinstance(rows, list):
        return []
    valid: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        worker_id = row.get("worker_id")
        capacity = row.get("capacity")
        if isinstance(worker_id, str) and worker_id.strip() and isinstance(capacity, int) and capacity > 0:
            valid.append(row)
    return valid


def _event_for_job(
    *, status: str, attempt: int, max_attempts: int, dlq_enabled: bool, total_capacity: int
) -> str:
    if status == "failed" and attempt >= max_attempts and dlq_enabled:
        return "sent_to_dlq"
    if status == "queued" and total_capacity > 0:
        return "ready_for_dispatch"
    return f"state:{status}"


def execute_async_job_plane(
    *, queue_state: dict[str, Any], workers: dict[str, Any], dlq: dict[str, Any]
) -> dict[str, Any]:
    jobs = _collect_jobs(queue_state)
    worker_rows = _collect_worker_rows(workers)
    total_capacity = sum(int(row["capacity"]) for row in worker_rows)
    worker_count = len(worker_rows)
    processed = 0
    queued = 0
    running = 0
    succeeded = 0
    failed = 0
    cancelled = 0
    events: list[dict[str, Any]] = []
    max_attempts = int(queue_state.get("max_attempts", 3))
    dlq_enabled = dlq.get("enabled") is True
    for job in jobs:
        status = job["status"]
        attempt = int(job["attempt"])
        processed += 1
        if status == "queued":
            queued += 1
        elif status == "running":
            running += 1
        elif status == "succeeded":
            succeeded += 1
        elif status == "failed":
            failed += 1
        else:
            cancelled += 1
        events.append(
            {
                "job_id": job["job_id"],
                "event": _event_for_job(
                    status=status,
                    attempt=attempt,
                    max_attempts=max_attempts,
                    dlq_enabled=dlq_enabled,
                    total_capacity=total_capacity,
                ),
            }
        )
    queue_depth = queued + running
    lag_seconds = int(queue_state.get("oldest_job_lag_seconds", 0))
    lag_breach = isinstance(queue_state.get("max_allowed_lag_seconds"), int) and lag_seconds > int(
        queue_state.get("max_allowed_lag_seconds")
    )
    if lag_breach:
        events.append({"job_id": "-", "event": "queue_lag_breach"})
    dlq_jobs = dlq.get("jobs")
    dlq_count = len(dlq_jobs) if isinstance(dlq_jobs, list) else 0
    return {
        "worker_count": worker_count,
        "total_capacity": total_capacity,
        "jobs_processed": processed,
        "state_counts": {
            "queued": queued,
            "running": running,
            "succeeded": succeeded,
            "failed": failed,
            "cancelled": cancelled,
        },
        "queue_depth": queue_depth,
        "queue_lag_seconds": lag_seconds,
        "queue_lag_breach": lag_breach,
        "dlq_count": dlq_count,
        "events": events,
    }


def summarize_async_plane_health(
    *, queue_state: dict[str, Any], workers: dict[str, Any], dlq: dict[str, Any]
) -> dict[str, bool]:
    execution = execute_async_job_plane(queue_state=queue_state, workers=workers, dlq=dlq)
    return {
        "durable_queue_present": queue_state.get("durable_backend") is True and execution["jobs_processed"] > 0,
        "lifecycle_api_present": queue_state.get("lifecycle_api") is True and execution["worker_count"] > 0,
        "state_recovery_enabled": queue_state.get("state_recovery") is True and queue_state.get("replay_checkpointing") is True,
        "worker_heartbeat_enabled": workers.get("heartbeat_enabled") is True
        and _worker_lease_policy_aligned(queue_state, workers)
        and _heartbeat_interval_aligned(queue_state, workers)
        and workers.get("lease_renewal") is True,
        "retry_backoff_budgeted": queue_state.get("retry_backoff_jitter") is True and isinstance(queue_state.get("max_attempts"), int),
        "dlq_present": dlq.get("enabled") is True and _dlq_policy_aligned(queue_state, dlq) and dlq.get("replay_supported") is True,
        "cancel_timeout_supported": queue_state.get("cancel_timeout_supported") is True and queue_state.get("job_timeout_seconds") is not None,
        "queue_metrics_present": queue_state.get("queue_metrics_present") is True
        and execution["queue_depth"] >= 0
        and execution["queue_lag_breach"] is False,
    }


def evaluate_async_job_plane_gate(
    *,
    run_id: str,
    mode: str,
    queue_state: dict[str, Any],
    workers: dict[str, Any],
    dlq: dict[str, Any],
) -> dict[str, Any]:
    execution = execute_async_job_plane(queue_state=queue_state, workers=workers, dlq=dlq)
    checks = summarize_async_plane_health(queue_state=queue_state, workers=workers, dlq=dlq)
    failed_gates = [name for name, passed in checks.items() if passed is not True]
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": ASYNC_JOB_PLANE_SCHEMA,
        "schema_version": ASYNC_JOB_PLANE_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "release_blocked": status == "fail",
        "checks": checks,
        "execution": execution,
        "failed_gates": failed_gates,
        "lifecycle_contract": build_job_lifecycle_contract(),
        "evidence": {
            "queue_ref": "data/async_job_plane/queue_state.json",
            "workers_ref": "data/async_job_plane/workers.json",
            "dlq_ref": "data/async_job_plane/dlq.json",
            "history_ref": "data/async_job_plane/trend_history.jsonl",
            "events_ref": "data/async_job_plane/job_events.jsonl",
        },
    }


def update_async_plane_history(*, existing: list[dict[str, Any]], report: dict[str, Any]) -> list[dict[str, Any]]:
    execution = report.get("execution")
    state_counts = execution.get("state_counts", {}) if isinstance(execution, dict) else {}
    row = {
        "run_id": report["run_id"],
        "status": report["status"],
        "failed_gate_count": len(report["failed_gates"]),
        "succeeded_jobs": state_counts.get("succeeded"),
        "failed_jobs": state_counts.get("failed"),
    }
    return [*existing, row]


def build_job_event_rows(*, report: dict[str, Any]) -> list[dict[str, Any]]:
    execution = report.get("execution")
    if not isinstance(execution, dict):
        return []
    events = execution.get("events")
    if not isinstance(events, list):
        return []
    rows: list[dict[str, Any]] = []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            continue
        rows.append(
            {
                "run_id": report.get("run_id"),
                "event_index": index,
                "job_id": event.get("job_id"),
                "event": event.get("event"),
            }
        )
    return rows

