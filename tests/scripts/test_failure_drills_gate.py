from __future__ import annotations

import json
import subprocess


def test_failure_drills_gate_script_passes(tmp_path) -> None:
    drills = {
        "executable_reliability_drill_framework_created": True,
        "provider_429_queue_lag_failures_simulated": True,
        "restart_crash_recovery_behavior_simulated": True,
        "framework_version": "drill-fw-1.0",
        "provider_429_scenarios": [
            {
                "name": "provider-openai-429",
                "outcome": "fail_expected",
                "injected_at": "2026-04-22T10:00:00Z",
                "recovered_at": "2026-04-22T10:00:20Z",
                "observed_429_error_rate_pct": 1.5,
                "observed_queue_lag_seconds": 90.0,
                "observed_restart_recovery_seconds": 20.0,
                "remediation_applied": True,
                "remediation_runbook_id": "rb-429",
            }
        ],
        "queue_lag_scenarios": [
            {
                "name": "queue-backlog-over-5m",
                "outcome": "fail_expected",
                "injected_at": "2026-04-22T10:10:00Z",
                "recovered_at": "2026-04-22T10:10:30Z",
                "observed_429_error_rate_pct": 1.0,
                "observed_queue_lag_seconds": 100.0,
                "observed_restart_recovery_seconds": 25.0,
                "remediation_applied": True,
                "remediation_runbook_id": "rb-queue-lag",
            }
        ],
        "restart_scenarios": [
            {
                "name": "worker-restart-recovery",
                "outcome": "pass",
                "injected_at": "2026-04-22T10:20:00Z",
                "recovered_at": "2026-04-22T10:20:35Z",
                "observed_429_error_rate_pct": 0.5,
                "observed_queue_lag_seconds": 80.0,
                "observed_restart_recovery_seconds": 30.0,
                "remediation_applied": True,
                "remediation_runbook_id": "rb-restart",
            }
        ],
    }
    slo = {
        "drill_slo_based_pass_fail_defined": True,
        "drill_outcomes_persisted_and_trended": True,
        "max_429_error_rate_pct": 2.5,
        "max_queue_lag_seconds": 120,
        "max_restart_recovery_seconds": 45,
        "regression_budget_pct": 10,
        "baseline_metrics": {
            "avg_429_error_rate_pct": 1.2,
            "avg_queue_lag_seconds": 90.0,
            "avg_restart_recovery_seconds": 30.0,
        },
        "last_drill_run_id": "drill-23-0007",
    }
    remediation = {
        "drills_run_automatically_ci_nightly": True,
        "drill_quality_regression_alerting_enabled": True,
        "remediation_behavior_verified_under_drills": True,
        "last_drill_run_id": "drill-23-0007",
        "execution_schedule": "ci-and-nightly",
        "alert_channels": ["pagerduty", "slack:#reliability"],
        "verified_runbook_ids": ["rb-429", "rb-queue-lag", "rb-restart"],
    }
    drills_path = tmp_path / "drills.json"
    slo_path = tmp_path / "slo.json"
    remediation_path = tmp_path / "remediation.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    drills_path.write_text(json.dumps(drills), encoding="utf-8")
    slo_path.write_text(json.dumps(slo), encoding="utf-8")
    remediation_path.write_text(json.dumps(remediation), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/failure_drills_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-23-ci",
            "--drills",
            str(drills_path),
            "--slo",
            str(slo_path),
            "--remediation",
            str(remediation_path),
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
    assert report["drill_execution"]["scenario_count"] == 3
    assert history_path.read_text(encoding="utf-8").strip()

