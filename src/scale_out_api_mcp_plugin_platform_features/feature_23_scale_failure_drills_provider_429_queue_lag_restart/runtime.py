"""Runtime for feature 23 scale failure drills gate."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .contracts import FAILURE_DRILLS_SCHEMA, FAILURE_DRILLS_SCHEMA_VERSION


def build_failure_drills_contract() -> dict[str, object]:
    return {
        "executable_reliability_drill_framework": True,
        "provider_429_and_queue_lag_simulation": True,
        "restart_crash_recovery_simulation": True,
        "drill_slo_pass_fail_criteria": True,
        "drill_outcomes_persisted_and_trended": True,
        "automatic_ci_nightly_execution": True,
        "drill_regression_alerting": True,
        "remediation_behavior_verified": True,
    }


def _valid_scenarios(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    for scenario in value:
        if not isinstance(scenario, dict):
            return False
        name = scenario.get("name")
        outcome = scenario.get("outcome")
        if not isinstance(name, str) or not name.strip():
            return False
        if outcome not in {"pass", "fail_expected"}:
            return False
    return True


def _valid_threshold(threshold: Any) -> bool:
    return isinstance(threshold, (int, float)) and float(threshold) >= 0.0


def _parse_iso8601(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _observed_non_negative(value: Any) -> bool:
    return isinstance(value, (int, float)) and float(value) >= 0.0


def _collect_scenarios(drills: dict[str, Any]) -> list[dict[str, Any]]:
    scenarios: list[dict[str, Any]] = []
    for category in ("provider_429_scenarios", "queue_lag_scenarios", "restart_scenarios"):
        raw = drills.get(category)
        if not isinstance(raw, list):
            continue
        for scenario in raw:
            if isinstance(scenario, dict):
                scenarios.append(scenario)
    return scenarios


def _scenario_failed_reason(
    scenario: dict[str, Any],
    *,
    max_429_error_rate_pct: float,
    max_queue_lag_seconds: float,
    max_restart_recovery_seconds: float,
) -> str | None:
    start_at = _parse_iso8601(scenario.get("injected_at"))
    end_at = _parse_iso8601(scenario.get("recovered_at"))
    if start_at is None or end_at is None:
        return "invalid_timestamps"
    if end_at < start_at:
        return "negative_recovery_window"
    observed_429 = scenario.get("observed_429_error_rate_pct")
    observed_lag = scenario.get("observed_queue_lag_seconds")
    observed_restart = scenario.get("observed_restart_recovery_seconds")
    if not (
        _observed_non_negative(observed_429)
        and _observed_non_negative(observed_lag)
        and _observed_non_negative(observed_restart)
    ):
        return "invalid_observed_metrics"
    if observed_429 > max_429_error_rate_pct:
        return "429_error_rate_exceeded"
    if observed_lag > max_queue_lag_seconds:
        return "queue_lag_exceeded"
    if observed_restart > max_restart_recovery_seconds:
        return "restart_recovery_exceeded"
    if scenario.get("remediation_applied") is not True:
        return "remediation_not_applied"
    runbook_id = scenario.get("remediation_runbook_id")
    if not isinstance(runbook_id, str) or not runbook_id.strip():
        return "invalid_remediation_runbook_id"
    return None


def execute_failure_drills(
    *, drills: dict[str, Any], slo: dict[str, Any], remediation: dict[str, Any]
) -> dict[str, Any]:
    scenarios = _collect_scenarios(drills)
    failed_scenarios: list[dict[str, str]] = []
    passed_scenarios = 0
    max_429 = float(slo["max_429_error_rate_pct"])
    max_lag = float(slo["max_queue_lag_seconds"])
    max_restart = float(slo["max_restart_recovery_seconds"])
    total_429 = 0.0
    total_lag = 0.0
    total_restart = 0.0
    timeline: list[dict[str, str]] = []
    for scenario in scenarios:
        name = str(scenario.get("name", ""))
        reason = _scenario_failed_reason(
            scenario,
            max_429_error_rate_pct=max_429,
            max_queue_lag_seconds=max_lag,
            max_restart_recovery_seconds=max_restart,
        )
        total_429 += float(scenario.get("observed_429_error_rate_pct", 0.0))
        total_lag += float(scenario.get("observed_queue_lag_seconds", 0.0))
        total_restart += float(scenario.get("observed_restart_recovery_seconds", 0.0))
        if reason is None:
            passed_scenarios += 1
            terminal_state = "pass"
        else:
            failed_scenarios.append({"name": name, "reason": reason})
            terminal_state = "fail"
        timeline.append(
            {
                "scenario": name,
                "injected_at": str(scenario.get("injected_at", "")),
                "recovered_at": str(scenario.get("recovered_at", "")),
                "terminal_state": terminal_state,
            }
        )
    total = len(scenarios)
    avg_429 = total_429 / total if total else 0.0
    avg_lag = total_lag / total if total else 0.0
    avg_restart = total_restart / total if total else 0.0
    regression_budget_pct = float(slo.get("regression_budget_pct", 10.0))
    baseline = slo.get("baseline_metrics")
    if not isinstance(baseline, dict):
        baseline = {}
    baseline_429 = float(baseline.get("avg_429_error_rate_pct", avg_429))
    baseline_lag = float(baseline.get("avg_queue_lag_seconds", avg_lag))
    baseline_restart = float(baseline.get("avg_restart_recovery_seconds", avg_restart))
    allow_429 = baseline_429 * (1.0 + regression_budget_pct / 100.0)
    allow_lag = baseline_lag * (1.0 + regression_budget_pct / 100.0)
    allow_restart = baseline_restart * (1.0 + regression_budget_pct / 100.0)
    regression_detected = any(
        (
            avg_429 > allow_429,
            avg_lag > allow_lag,
            avg_restart > allow_restart,
        )
    )
    channels = remediation.get("alert_channels")
    alerts_emitted = bool(regression_detected and isinstance(channels, list) and channels)
    verified_runbooks = remediation.get("verified_runbook_ids")
    expected_runbooks = {
        str(scenario.get("remediation_runbook_id", "")).strip() for scenario in scenarios
    }
    expected_runbooks.discard("")
    verified_runbook_set = set(verified_runbooks) if isinstance(verified_runbooks, list) else set()
    missing_verified = sorted(expected_runbooks - verified_runbook_set)
    remediation_verified = not missing_verified
    return {
        "scenario_count": total,
        "passed_scenarios": passed_scenarios,
        "failed_scenarios": failed_scenarios,
        "metrics": {
            "avg_429_error_rate_pct": round(avg_429, 4),
            "avg_queue_lag_seconds": round(avg_lag, 4),
            "avg_restart_recovery_seconds": round(avg_restart, 4),
        },
        "regression": {
            "regression_detected": regression_detected,
            "alerts_emitted": alerts_emitted,
            "missing_verified_runbooks": missing_verified,
            "remediation_verified": remediation_verified,
        },
        "timeline": timeline,
    }


def _unique_scenario_names(drills: dict[str, Any]) -> bool:
    scenario_sets = (
        drills.get("provider_429_scenarios"),
        drills.get("queue_lag_scenarios"),
        drills.get("restart_scenarios"),
    )
    seen: set[str] = set()
    for scenario_list in scenario_sets:
        if not isinstance(scenario_list, list):
            return False
        for scenario in scenario_list:
            if not isinstance(scenario, dict):
                return False
            name = scenario.get("name")
            if not isinstance(name, str) or not name.strip():
                return False
            if name in seen:
                return False
            seen.add(name)
    return True


def _drill_run_id_aligned(slo: dict[str, Any], remediation: dict[str, Any]) -> bool:
    slo_run_id = slo.get("last_drill_run_id")
    remediation_run_id = remediation.get("last_drill_run_id")
    return (
        isinstance(slo_run_id, str)
        and slo_run_id.strip() != ""
        and slo_run_id == remediation_run_id
    )


def summarize_failure_drills_health(
    *, drills: dict[str, Any], slo: dict[str, Any], remediation: dict[str, Any]
) -> dict[str, bool]:
    execution = execute_failure_drills(drills=drills, slo=slo, remediation=remediation)
    return {
        "executable_reliability_drill_framework_created": drills.get(
            "executable_reliability_drill_framework_created"
        )
        is True
        and isinstance(drills.get("framework_version"), str)
        and drills.get("framework_version").strip() != "",
        "provider_429_queue_lag_failures_simulated": drills.get(
            "provider_429_queue_lag_failures_simulated"
        )
        is True
        and _valid_scenarios(drills.get("provider_429_scenarios"))
        and _valid_scenarios(drills.get("queue_lag_scenarios")),
        "restart_crash_recovery_behavior_simulated": drills.get(
            "restart_crash_recovery_behavior_simulated"
        )
        is True
        and _valid_scenarios(drills.get("restart_scenarios"))
        and _unique_scenario_names(drills),
        "drill_slo_based_pass_fail_defined": slo.get("drill_slo_based_pass_fail_defined") is True
        and _valid_threshold(slo.get("max_429_error_rate_pct"))
        and _valid_threshold(slo.get("max_queue_lag_seconds"))
        and _valid_threshold(slo.get("max_restart_recovery_seconds")),
        "drill_outcomes_persisted_and_trended": slo.get("drill_outcomes_persisted_and_trended")
        is True
        and isinstance(slo.get("last_drill_run_id"), str)
        and slo.get("last_drill_run_id").strip() != ""
        and _drill_run_id_aligned(slo, remediation),
        "drills_run_automatically_ci_nightly": remediation.get("drills_run_automatically_ci_nightly")
        is True
        and remediation.get("execution_schedule") in {"nightly", "ci-and-nightly"},
        "drill_quality_regression_alerting_enabled": remediation.get(
            "drill_quality_regression_alerting_enabled"
        )
        is True
        and isinstance(remediation.get("alert_channels"), list)
        and len(remediation.get("alert_channels")) > 0,
        "remediation_behavior_verified_under_drills": remediation.get(
            "remediation_behavior_verified_under_drills"
        )
        is True
        and isinstance(remediation.get("verified_runbook_ids"), list)
        and len(remediation.get("verified_runbook_ids")) > 0,
        "all_scenarios_executed_and_passing": execution["scenario_count"] > 0
        and execution["scenario_count"] == execution["passed_scenarios"],
        "regression_alerts_and_remediation_validated": (
            execution["regression"]["regression_detected"] is False
            or execution["regression"]["alerts_emitted"] is True
        )
        and execution["regression"]["remediation_verified"] is True,
    }


def evaluate_failure_drills_gate(
    *,
    run_id: str,
    mode: str,
    drills: dict[str, Any],
    slo: dict[str, Any],
    remediation: dict[str, Any],
) -> dict[str, Any]:
    execution = execute_failure_drills(drills=drills, slo=slo, remediation=remediation)
    checks = summarize_failure_drills_health(drills=drills, slo=slo, remediation=remediation)
    failed_gates = [name for name, passed in checks.items() if passed is not True]
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": FAILURE_DRILLS_SCHEMA,
        "schema_version": FAILURE_DRILLS_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "release_blocked": status == "fail",
        "checks": checks,
        "failed_gates": failed_gates,
        "drill_execution": execution,
        "failure_drills_contract": build_failure_drills_contract(),
        "evidence": {
            "drills_ref": "data/failure_drills/drills.json",
            "slo_ref": "data/failure_drills/slo_assertions.json",
            "remediation_ref": "data/failure_drills/remediation.json",
            "history_ref": "data/failure_drills/trend_history.jsonl",
            "events_ref": "data/failure_drills/drill_events.jsonl",
        },
    }


def update_failure_drills_history(
    *, existing: list[dict[str, Any]], report: dict[str, Any]
) -> list[dict[str, Any]]:
    execution = report.get("drill_execution")
    metrics = execution.get("metrics", {}) if isinstance(execution, dict) else {}
    row = {
        "run_id": report["run_id"],
        "status": report["status"],
        "failed_gate_count": len(report["failed_gates"]),
        "avg_429_error_rate_pct": metrics.get("avg_429_error_rate_pct"),
        "avg_queue_lag_seconds": metrics.get("avg_queue_lag_seconds"),
        "avg_restart_recovery_seconds": metrics.get("avg_restart_recovery_seconds"),
    }
    return [*existing, row]


def build_drill_event_rows(*, report: dict[str, Any]) -> list[dict[str, Any]]:
    execution = report.get("drill_execution")
    if not isinstance(execution, dict):
        return []
    timeline = execution.get("timeline")
    if not isinstance(timeline, list):
        return []
    rows: list[dict[str, Any]] = []
    for index, row in enumerate(timeline):
        if not isinstance(row, dict):
            continue
        rows.append(
            {
                "run_id": report.get("run_id"),
                "event_index": index,
                "scenario": row.get("scenario"),
                "injected_at": row.get("injected_at"),
                "recovered_at": row.get("recovered_at"),
                "terminal_state": row.get("terminal_state"),
            }
        )
    return rows

