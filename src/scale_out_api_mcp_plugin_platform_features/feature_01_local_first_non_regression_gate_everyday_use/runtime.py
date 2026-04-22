"""Runtime for feature 01 local non-regression gate."""

from __future__ import annotations

from typing import Any

from .contracts import LOCAL_NON_REGRESSION_SCHEMA, LOCAL_NON_REGRESSION_SCHEMA_VERSION


def _ratio(current: float, baseline: float) -> float:
    if baseline <= 0:
        return 1.0
    return round(current / baseline, 4)


def build_benchmark_suite() -> dict[str, object]:
    return {
        "suite": "local_non_regression_v1",
        "commands": ["sde --help", "sde run --dry-run", "sde doctor"],
        "profiles": ["cold_start", "warm_start", "daily_workflow"],
    }


def evaluate_local_non_regression_gate(
    *,
    run_id: str,
    mode: str,
    feature_flag: str,
    current: dict[str, float],
    baseline: dict[str, float],
) -> dict[str, Any]:
    thresholds = {
        "max_startup_regression_ratio": 1.1,
        "max_workflow_regression_ratio": 1.1,
        "min_success_rate": 0.99,
        "min_recovery_rate": 0.98,
        "max_error_rate": 0.01,
        "max_cpu_peak_percent": 85.0,
        "max_memory_peak_mb": 1024.0,
    }
    failed_gates: list[str] = []
    if _ratio(current["startup_ms_cold_p95"], baseline["startup_ms_cold_p95"]) > thresholds["max_startup_regression_ratio"]:
        failed_gates.append("startup_cold_regression")
    if _ratio(current["startup_ms_warm_p95"], baseline["startup_ms_warm_p95"]) > thresholds["max_startup_regression_ratio"]:
        failed_gates.append("startup_warm_regression")
    if _ratio(current["workflow_p95_ms"], baseline["workflow_p95_ms"]) > thresholds["max_workflow_regression_ratio"]:
        failed_gates.append("workflow_latency_regression")
    if current["workflow_success_rate"] < thresholds["min_success_rate"]:
        failed_gates.append("slo_success_rate_breach")
    if current["workflow_recovery_rate"] < thresholds["min_recovery_rate"]:
        failed_gates.append("slo_recovery_rate_breach")
    if current["developer_error_rate"] > thresholds["max_error_rate"]:
        failed_gates.append("slo_error_rate_breach")
    if current["cpu_peak_percent"] > thresholds["max_cpu_peak_percent"]:
        failed_gates.append("resource_cpu_ceiling_breach")
    if current["memory_peak_mb"] > thresholds["max_memory_peak_mb"]:
        failed_gates.append("resource_memory_ceiling_breach")
    status = "pass" if len(failed_gates) == 0 else "fail"
    return {
        "schema": LOCAL_NON_REGRESSION_SCHEMA,
        "schema_version": LOCAL_NON_REGRESSION_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "feature_flag": feature_flag,
        "status": status,
        "release_blocked": status == "fail",
        "failed_gates": failed_gates,
        "current": current,
        "baseline": baseline,
        "benchmarks": build_benchmark_suite(),
        "evidence": {
            "baseline_ref": "data/local_non_regression/baseline.json",
            "benchmarks_ref": "data/local_non_regression/benchmarks.json",
            "history_ref": "data/local_non_regression/trend_history.jsonl",
        },
    }


def update_trend_history(*, existing: list[dict[str, Any]], report: dict[str, Any]) -> list[dict[str, Any]]:
    snapshot = {
        "run_id": report["run_id"],
        "status": report["status"],
        "developer_error_rate": report["current"]["developer_error_rate"],
        "workflow_p95_ms": report["current"]["workflow_p95_ms"],
    }
    return [*existing, snapshot]

