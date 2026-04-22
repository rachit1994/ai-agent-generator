from __future__ import annotations

import json
import subprocess


def test_tenant_quota_gate_script_passes_for_healthy_payloads(tmp_path) -> None:
    quota = {
        "tenant_identity_threaded": True,
        "tenant_scope": "tenant-a",
        "durable_quota_state": True,
        "refill_window_supported": True,
        "refill_window_seconds": 60,
        "admin_controls_present": True,
        "quota_policy_version": "2026.04",
        "tenant_limits": {"tenant-a": 5},
        "tenant_usage": {"tenant-a": 2},
    }
    scheduler = {
        "hard_limit_enforced": True,
        "fairness_policy_enforced": True,
        "rejection_reasons_present": True,
        "tenant_scope": "tenant-a",
        "refill_window_seconds": 60,
        "quota_policy_version": "2026.04",
        "rejection_reason_codes": ["tenant_quota_exhausted", "tenant_concurrency_exhausted"],
        "admission_events": [
            {
                "event_id": "quota-evt-001",
                "tenant_id": "tenant-a",
                "requested_slots": 2,
                "status": "admitted",
                "reason_code": "tenant_concurrency_exhausted",
            },
            {
                "event_id": "quota-evt-002",
                "tenant_id": "tenant-a",
                "requested_slots": 4,
                "status": "rejected",
                "reason_code": "tenant_quota_exhausted",
            },
        ],
    }
    observability = {
        "tenant_observability_present": True,
        "tenant_scope": "tenant-a",
        "refill_window_seconds": 60,
        "quota_policy_version": "2026.04",
        "tracked_rejection_reason_codes": ["tenant_quota_exhausted", "tenant_concurrency_exhausted"],
        "rejection_count": 1,
    }
    quota_path = tmp_path / "quota.json"
    scheduler_path = tmp_path / "scheduler.json"
    obs_path = tmp_path / "obs.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    quota_path.write_text(json.dumps(quota), encoding="utf-8")
    scheduler_path.write_text(json.dumps(scheduler), encoding="utf-8")
    obs_path.write_text(json.dumps(observability), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/tenant_quota_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-06-ci",
            "--quota",
            str(quota_path),
            "--scheduler",
            str(scheduler_path),
            "--observability",
            str(obs_path),
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
    events_path = tmp_path / "quota_events.jsonl"
    assert events_path.read_text(encoding="utf-8").strip()

