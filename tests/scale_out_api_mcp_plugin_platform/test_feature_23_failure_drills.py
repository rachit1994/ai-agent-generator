from __future__ import annotations

import pytest

from scale_out_api_mcp_plugin_platform_features.feature_23_scale_failure_drills_provider_429_queue_lag_restart import (
    build_drill_event_rows,
    build_failure_drills_contract,
    execute_failure_drills,
    evaluate_failure_drills_gate,
    update_failure_drills_history,
    validate_failure_drills_report_dict,
)


def _drills() -> dict[str, object]:
    return {
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


def _slo() -> dict[str, object]:
    return {
        "drill_slo_based_pass_fail_defined": True,
        "drill_outcomes_persisted_and_trended": True,
        "max_429_error_rate_pct": 2.5,
        "max_queue_lag_seconds": 120,
        "max_restart_recovery_seconds": 45,
        "regression_budget_pct": 10,
        "baseline_metrics": {
            "avg_429_error_rate_pct": 1.2,
            "avg_queue_lag_seconds": 90,
            "avg_restart_recovery_seconds": 30,
        },
        "last_drill_run_id": "drill-23-0007",
    }


def _remediation() -> dict[str, object]:
    return {
        "drills_run_automatically_ci_nightly": True,
        "drill_quality_regression_alerting_enabled": True,
        "remediation_behavior_verified_under_drills": True,
        "last_drill_run_id": "drill-23-0007",
        "execution_schedule": "ci-and-nightly",
        "alert_channels": ["pagerduty", "slack:#reliability"],
        "verified_runbook_ids": ["rb-429", "rb-queue-lag", "rb-restart"],
    }


def test_failure_drills_gate_passes_for_complete_inputs() -> None:
    report = evaluate_failure_drills_gate(
        run_id="run-feature-23-pass",
        mode="ci",
        drills=_drills(),
        slo=_slo(),
        remediation=_remediation(),
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert report["drill_execution"]["scenario_count"] == 3
    assert validate_failure_drills_report_dict(report) == []


def test_failure_drills_gate_fail_closes_on_missing_alerting() -> None:
    remediation = _remediation()
    remediation["drill_quality_regression_alerting_enabled"] = False
    report = evaluate_failure_drills_gate(
        run_id="run-feature-23-fail",
        mode="preflight",
        drills=_drills(),
        slo=_slo(),
        remediation=remediation,
    )
    assert report["status"] == "fail"
    assert "drill_quality_regression_alerting_enabled" in report["failed_gates"]


def test_failure_drills_gate_fail_closes_on_invalid_scenario_outcome() -> None:
    drills = _drills()
    drills["provider_429_scenarios"] = [{"name": "provider-openai-429", "outcome": "unknown"}]
    report = evaluate_failure_drills_gate(
        run_id="run-feature-23-invalid-scenario",
        mode="preflight",
        drills=drills,
        slo=_slo(),
        remediation=_remediation(),
    )
    assert report["status"] == "fail"
    assert "provider_429_queue_lag_failures_simulated" in report["failed_gates"]


def test_failure_drills_gate_fail_closes_on_duplicate_scenario_name_across_sets() -> None:
    drills = _drills()
    drills["restart_scenarios"] = [
        {
            "name": "provider-openai-429",
            "outcome": "pass",
            "injected_at": "2026-04-22T10:20:00Z",
            "recovered_at": "2026-04-22T10:20:35Z",
            "observed_429_error_rate_pct": 0.5,
            "observed_queue_lag_seconds": 80.0,
            "observed_restart_recovery_seconds": 30.0,
            "remediation_applied": True,
            "remediation_runbook_id": "rb-restart",
        }
    ]
    report = evaluate_failure_drills_gate(
        run_id="run-feature-23-duplicate-scenario-name",
        mode="preflight",
        drills=drills,
        slo=_slo(),
        remediation=_remediation(),
    )
    assert report["status"] == "fail"
    assert "restart_crash_recovery_behavior_simulated" in report["failed_gates"]


def test_failure_drills_gate_fail_closes_on_last_drill_run_id_drift() -> None:
    remediation = _remediation()
    remediation["last_drill_run_id"] = "drill-23-0008"
    report = evaluate_failure_drills_gate(
        run_id="run-feature-23-last-drill-run-id-drift",
        mode="preflight",
        drills=_drills(),
        slo=_slo(),
        remediation=remediation,
    )
    assert report["status"] == "fail"
    assert "drill_outcomes_persisted_and_trended" in report["failed_gates"]


def test_failure_drills_contract_deterministic() -> None:
    assert build_failure_drills_contract() == build_failure_drills_contract()


def test_failure_drills_history_appends_row() -> None:
    report = evaluate_failure_drills_gate(
        run_id="run-feature-23-history",
        mode="ci",
        drills=_drills(),
        slo=_slo(),
        remediation=_remediation(),
    )
    history = update_failure_drills_history(existing=[], report=report)
    assert history[0]["run_id"] == "run-feature-23-history"
    assert history[0]["avg_429_error_rate_pct"] == pytest.approx(1.0)


def test_execute_failure_drills_detects_threshold_breach() -> None:
    drills = _drills()
    drills["provider_429_scenarios"][0]["observed_429_error_rate_pct"] = 9.0
    execution = execute_failure_drills(drills=drills, slo=_slo(), remediation=_remediation())
    assert execution["failed_scenarios"][0]["reason"] == "429_error_rate_exceeded"


def test_execute_failure_drills_detects_missing_runbook_verification() -> None:
    remediation = _remediation()
    remediation["verified_runbook_ids"] = ["rb-429"]
    execution = execute_failure_drills(drills=_drills(), slo=_slo(), remediation=remediation)
    assert execution["regression"]["remediation_verified"] is False
    assert "rb-queue-lag" in execution["regression"]["missing_verified_runbooks"]


def test_execute_failure_drills_flags_regression_and_alerts() -> None:
    drills = _drills()
    all_scenarios = (
        drills["provider_429_scenarios"]
        + drills["queue_lag_scenarios"]
        + drills["restart_scenarios"]
    )
    for scenario in all_scenarios:
        scenario["observed_429_error_rate_pct"] = 2.0
        scenario["observed_queue_lag_seconds"] = 115.0
        scenario["observed_restart_recovery_seconds"] = 44.0
    execution = execute_failure_drills(drills=drills, slo=_slo(), remediation=_remediation())
    assert execution["regression"]["regression_detected"] is True
    assert execution["regression"]["alerts_emitted"] is True


def test_build_drill_event_rows_from_report_timeline() -> None:
    report = evaluate_failure_drills_gate(
        run_id="run-feature-23-events",
        mode="ci",
        drills=_drills(),
        slo=_slo(),
        remediation=_remediation(),
    )
    rows = build_drill_event_rows(report=report)
    assert len(rows) == 3
    assert rows[0]["run_id"] == "run-feature-23-events"

