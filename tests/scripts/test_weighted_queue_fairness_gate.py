from __future__ import annotations

import json
import subprocess


def test_weighted_queue_fairness_gate_script_passes(tmp_path) -> None:
    scheduler = {
        "queue_backend": "memory_sim",
        "tenant_weights": {"tenant-a": 5, "tenant-b": 3},
        "plugin_weights": {"plugin-x": 4, "plugin-y": 2},
        "scheduler_state_version": 2,
        "replay_cursor": "cursor-0002",
        "replay_applied_decisions": 48,
        "decision_log_entries": 120,
        "replay_hash": "trace-hash-008",
        "dispatch_events": [
            {
                "event_id": "sched-001",
                "tenant": "tenant-a",
                "plugin": "plugin-x",
                "status": "scheduled",
                "wait_ms": 35,
            },
            {
                "event_id": "sched-002",
                "tenant": "tenant-b",
                "plugin": "plugin-y",
                "status": "scheduled",
                "wait_ms": 45,
            },
            {
                "event_id": "sched-003",
                "tenant": "tenant-b",
                "plugin": "plugin-y",
                "status": "dropped",
                "wait_ms": 0,
            },
        ],
    }
    telemetry = {
        "fairness_score": 0.93,
        "p95_wait_ms": 47,
        "class_wait_p95_ms": {"tenant-a": 42, "tenant-b": 47},
        "mixed_load_stress_validation": True,
        "mixed_load_samples": 180,
        "deterministic_trace_hash": "trace-hash-008",
    }
    policy = {
        "starvation_prevention_aging_policy": True,
        "safe_admin_weight_tuning_controls": True,
        "last_admin_change_ticket": "CAB-2026-0042",
        "deterministic_scheduler_tests": True,
        "admin_tuning_range": {"min": 1, "max": 20},
        "deterministic_trace_hash": "trace-hash-008",
    }
    scheduler_path = tmp_path / "scheduler.json"
    telemetry_path = tmp_path / "telemetry.json"
    policy_path = tmp_path / "policy.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    scheduler_path.write_text(json.dumps(scheduler), encoding="utf-8")
    telemetry_path.write_text(json.dumps(telemetry), encoding="utf-8")
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/weighted_queue_fairness_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-08-ci",
            "--scheduler",
            str(scheduler_path),
            "--telemetry",
            str(telemetry_path),
            "--policy",
            str(policy_path),
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
    assert history_path.read_text(encoding="utf-8").strip()
    events_path = tmp_path / "scheduler_events.jsonl"
    assert events_path.read_text(encoding="utf-8").strip()

