from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_01_local_first_non_regression_gate_everyday_use import (
    build_benchmark_suite,
    evaluate_local_non_regression_gate,
    update_trend_history,
    validate_local_non_regression_report_dict,
)


def _current_metrics() -> dict[str, float]:
    return {
        "startup_ms_cold_p95": 980.0,
        "startup_ms_warm_p95": 210.0,
        "workflow_p95_ms": 1400.0,
        "workflow_success_rate": 0.995,
        "workflow_recovery_rate": 0.99,
        "developer_error_rate": 0.003,
        "cpu_peak_percent": 71.0,
        "memory_peak_mb": 820.0,
    }


def _baseline_metrics() -> dict[str, float]:
    return {
        "startup_ms_cold_p95": 1000.0,
        "startup_ms_warm_p95": 230.0,
        "workflow_p95_ms": 1500.0,
        "workflow_success_rate": 0.996,
        "workflow_recovery_rate": 0.991,
        "developer_error_rate": 0.004,
        "cpu_peak_percent": 75.0,
        "memory_peak_mb": 900.0,
    }


def test_gate_passes_for_healthy_metrics() -> None:
    report = evaluate_local_non_regression_gate(
        run_id="run-feature-01-pass",
        mode="ci",
        feature_flag="scale_local_non_regression",
        current=_current_metrics(),
        baseline=_baseline_metrics(),
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert validate_local_non_regression_report_dict(report) == []


def test_gate_fail_closes_on_slo_breach() -> None:
    current = _current_metrics()
    current["workflow_success_rate"] = 0.95
    report = evaluate_local_non_regression_gate(
        run_id="run-feature-01-slo-fail",
        mode="preflight",
        feature_flag="scale_local_non_regression",
        current=current,
        baseline=_baseline_metrics(),
    )
    assert report["status"] == "fail"
    assert report["release_blocked"] is True
    assert "slo_success_rate_breach" in report["failed_gates"]


def test_gate_fail_closes_on_startup_regression() -> None:
    current = _current_metrics()
    current["startup_ms_cold_p95"] = 1400.0
    report = evaluate_local_non_regression_gate(
        run_id="run-feature-01-startup-regression",
        mode="ci",
        feature_flag="scale_local_non_regression",
        current=current,
        baseline=_baseline_metrics(),
    )
    assert report["status"] == "fail"
    assert "startup_cold_regression" in report["failed_gates"]


def test_gate_fail_closes_on_resource_ceiling_breach() -> None:
    current = _current_metrics()
    current["memory_peak_mb"] = 2048.0
    report = evaluate_local_non_regression_gate(
        run_id="run-feature-01-memory-breach",
        mode="ci",
        feature_flag="scale_local_non_regression",
        current=current,
        baseline=_baseline_metrics(),
    )
    assert report["status"] == "fail"
    assert "resource_memory_ceiling_breach" in report["failed_gates"]


def test_benchmark_suite_is_deterministic() -> None:
    assert build_benchmark_suite() == build_benchmark_suite()


def test_update_trend_history_appends_latest_snapshot() -> None:
    report = evaluate_local_non_regression_gate(
        run_id="run-feature-01-history",
        mode="ci",
        feature_flag="scale_local_non_regression",
        current=_current_metrics(),
        baseline=_baseline_metrics(),
    )
    updated = update_trend_history(existing=[], report=report)
    assert len(updated) == 1
    assert updated[0]["run_id"] == "run-feature-01-history"
    assert "developer_error_rate" in updated[0]
