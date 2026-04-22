from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_04_async_job_plane_long_running_api_operations import (
    build_job_event_rows,
    build_job_lifecycle_contract,
    execute_async_job_plane,
    evaluate_async_job_plane_gate,
    update_async_plane_history,
    validate_async_job_plane_report_dict,
)


def _queue_state() -> dict[str, object]:
    return {
        "durable_backend": True,
        "dlq_policy_version": "2026.04",
        "lifecycle_api": True,
        "state_recovery": True,
        "worker_heartbeat_interval_seconds": 30,
        "worker_lease_policy_version": "2026.04",
        "retry_backoff_jitter": True,
        "cancel_timeout_supported": True,
        "job_timeout_seconds": 300,
        "replay_checkpointing": True,
        "max_attempts": 3,
        "max_allowed_lag_seconds": 120,
        "oldest_job_lag_seconds": 90,
        "queue_metrics_present": True,
        "jobs": [
            {"job_id": "job-001", "status": "queued", "attempt": 0},
            {"job_id": "job-002", "status": "running", "attempt": 1},
            {"job_id": "job-003", "status": "succeeded", "attempt": 1},
            {"job_id": "job-004", "status": "failed", "attempt": 3},
            {"job_id": "job-005", "status": "cancelled", "attempt": 1},
        ],
    }


def _workers_state() -> dict[str, object]:
    return {
        "heartbeat_enabled": True,
        "worker_heartbeat_interval_seconds": 30,
        "lease_renewal": True,
        "worker_lease_policy_version": "2026.04",
        "workers": [
            {"worker_id": "worker-a", "capacity": 2},
            {"worker_id": "worker-b", "capacity": 1},
        ],
    }


def _dlq_state() -> dict[str, object]:
    return {
        "enabled": True,
        "replay_supported": True,
        "dlq_policy_version": "2026.04",
        "jobs": [{"job_id": "job-004", "reason": "retry_exhausted"}],
    }


def test_async_job_plane_gate_passes_for_healthy_payloads() -> None:
    report = evaluate_async_job_plane_gate(
        run_id="run-feature-04-pass",
        mode="ci",
        queue_state=_queue_state(),
        workers=_workers_state(),
        dlq=_dlq_state(),
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert report["execution"]["jobs_processed"] == 5
    assert validate_async_job_plane_report_dict(report) == []


def test_async_job_plane_gate_fail_closes_when_dlq_missing() -> None:
    dlq = _dlq_state()
    dlq["enabled"] = False
    report = evaluate_async_job_plane_gate(
        run_id="run-feature-04-dlq-missing",
        mode="preflight",
        queue_state=_queue_state(),
        workers=_workers_state(),
        dlq=dlq,
    )
    assert report["status"] == "fail"
    assert "dlq_present" in report["failed_gates"]


def test_async_job_plane_gate_fail_closes_on_worker_lease_policy_version_drift() -> None:
    workers = _workers_state()
    workers["worker_lease_policy_version"] = "2026.05"
    report = evaluate_async_job_plane_gate(
        run_id="run-feature-04-worker-lease-policy-drift",
        mode="preflight",
        queue_state=_queue_state(),
        workers=workers,
        dlq=_dlq_state(),
    )
    assert report["status"] == "fail"
    assert "worker_heartbeat_enabled" in report["failed_gates"]


def test_async_job_plane_gate_fail_closes_on_dlq_policy_version_drift() -> None:
    dlq = _dlq_state()
    dlq["dlq_policy_version"] = "2026.05"
    report = evaluate_async_job_plane_gate(
        run_id="run-feature-04-dlq-policy-drift",
        mode="preflight",
        queue_state=_queue_state(),
        workers=_workers_state(),
        dlq=dlq,
    )
    assert report["status"] == "fail"
    assert "dlq_present" in report["failed_gates"]


def test_async_job_plane_gate_fail_closes_on_heartbeat_interval_drift() -> None:
    workers = _workers_state()
    workers["worker_heartbeat_interval_seconds"] = 45
    report = evaluate_async_job_plane_gate(
        run_id="run-feature-04-heartbeat-interval-drift",
        mode="preflight",
        queue_state=_queue_state(),
        workers=workers,
        dlq=_dlq_state(),
    )
    assert report["status"] == "fail"
    assert "worker_heartbeat_enabled" in report["failed_gates"]


def test_async_job_plane_gate_fail_closes_on_queue_lag_breach() -> None:
    queue = _queue_state()
    queue["oldest_job_lag_seconds"] = 999
    report = evaluate_async_job_plane_gate(
        run_id="run-feature-04-queue-lag-breach",
        mode="preflight",
        queue_state=queue,
        workers=_workers_state(),
        dlq=_dlq_state(),
    )
    assert report["status"] == "fail"
    assert "queue_metrics_present" in report["failed_gates"]


def test_execute_async_job_plane_marks_dlq_for_retry_exhausted_failures() -> None:
    execution = execute_async_job_plane(
        queue_state=_queue_state(),
        workers=_workers_state(),
        dlq=_dlq_state(),
    )
    assert any(event["event"] == "sent_to_dlq" for event in execution["events"])


def test_build_job_event_rows_from_report_execution() -> None:
    report = evaluate_async_job_plane_gate(
        run_id="run-feature-04-events",
        mode="ci",
        queue_state=_queue_state(),
        workers=_workers_state(),
        dlq=_dlq_state(),
    )
    rows = build_job_event_rows(report=report)
    assert len(rows) == report["execution"]["jobs_processed"]
    assert rows[0]["run_id"] == "run-feature-04-events"


def test_lifecycle_contract_is_deterministic() -> None:
    assert build_job_lifecycle_contract() == build_job_lifecycle_contract()


def test_async_plane_history_appends_snapshot() -> None:
    report = evaluate_async_job_plane_gate(
        run_id="run-feature-04-history",
        mode="ci",
        queue_state=_queue_state(),
        workers=_workers_state(),
        dlq=_dlq_state(),
    )
    history = update_async_plane_history(existing=[], report=report)
    assert len(history) == 1
    assert history[0]["run_id"] == "run-feature-04-history"
    assert history[0]["succeeded_jobs"] == 1

