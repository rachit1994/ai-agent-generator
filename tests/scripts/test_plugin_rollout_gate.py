from __future__ import annotations

import json
import subprocess


def test_plugin_rollout_gate_script_passes(tmp_path) -> None:
    controller = {
        "plugin_progressive_rollout_controller_built": True,
        "canary_cohorts_staged_traffic_supported": True,
        "active_plugin_version": "2.4.1",
        "stages": [
            {"cohort": "canary", "traffic_percent": 10},
            {"cohort": "ramp", "traffic_percent": 30},
            {"cohort": "stable", "traffic_percent": 60},
        ],
    }
    health = {
        "health_gated_promotion_enforced": True,
        "auto_rollback_on_slo_or_policy_breach": True,
        "error_rate_pct": 0.4,
        "latency_p95_ms": 180,
        "rollback_triggered": False,
        "rollout_actions_integrated_with_observability_signals": True,
        "observability_signal_ids": ["sig-01", "sig-02"],
    }
    operations = {
        "rollout_timeline_persisted_for_audit": True,
        "pause_resume_override_operations_available": True,
        "override_actions_count": 1,
        "canary_and_rollback_lifecycle_tested": True,
        "lifecycle_test_run_id": "rollout-lifecycle-22",
        "timeline_events": [
            {"type": "canary_start", "timestamp": "2026-04-22T10:01:00Z", "actor": "rollout-controller"},
            {"type": "promote", "timestamp": "2026-04-22T10:11:00Z", "actor": "rollout-controller"},
        ],
    }
    controller_path = tmp_path / "controller.json"
    health_path = tmp_path / "health.json"
    operations_path = tmp_path / "operations.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    controller_path.write_text(json.dumps(controller), encoding="utf-8")
    health_path.write_text(json.dumps(health), encoding="utf-8")
    operations_path.write_text(json.dumps(operations), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/plugin_rollout_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-22-ci",
            "--controller",
            str(controller_path),
            "--health",
            str(health_path),
            "--operations",
            str(operations_path),
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

