from __future__ import annotations

import json
import subprocess


def test_async_job_plane_gate_script_passes_for_healthy_payloads(tmp_path) -> None:
    queue = {
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
    workers = {
        "heartbeat_enabled": True,
        "worker_heartbeat_interval_seconds": 30,
        "lease_renewal": True,
        "worker_lease_policy_version": "2026.04",
        "workers": [
            {"worker_id": "worker-a", "capacity": 2},
            {"worker_id": "worker-b", "capacity": 1},
        ],
    }
    dlq = {
        "enabled": True,
        "replay_supported": True,
        "dlq_policy_version": "2026.04",
        "jobs": [{"job_id": "job-004", "reason": "retry_exhausted"}],
    }
    queue_path = tmp_path / "queue.json"
    workers_path = tmp_path / "workers.json"
    dlq_path = tmp_path / "dlq.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    queue_path.write_text(json.dumps(queue), encoding="utf-8")
    workers_path.write_text(json.dumps(workers), encoding="utf-8")
    dlq_path.write_text(json.dumps(dlq), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/async_job_plane_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-04-ci",
            "--queue",
            str(queue_path),
            "--workers",
            str(workers_path),
            "--dlq",
            str(dlq_path),
            "--out",
            str(out_path),
            "--history",
            str(history_path),
        ],
        check=False,
        text=True,
    )
    assert result.returncode == 0
    report = json.loads(out_path.read_text(encoding="utf-8"))
    assert report["status"] == "pass"
    assert report["execution"]["jobs_processed"] == 5
    events_path = out_path.parent / "job_events.jsonl"
    assert events_path.is_file()
    assert history_path.read_text(encoding="utf-8").strip()

