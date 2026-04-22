from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_09_plugin_circuit_breakers_retry_budgets import (
    build_transition_event_rows,
    build_plugin_circuit_breaker_contract,
    execute_plugin_circuit_breaker_runtime,
    evaluate_plugin_circuit_breaker_gate,
    update_plugin_circuit_breaker_history,
    validate_plugin_circuit_breaker_report_dict,
)


def _runtime() -> dict[str, object]:
    return {
        "plugin_level_circuit_breaker_runtime": True,
        "plugin_id": "plugin-x",
        "current_state": "closed",
        "plugin_level_retry_budget_enforcement": True,
        "retry_budget_policy_version": "2026.04",
        "retry_budget_remaining": 7,
        "retry_budget_limit": 10,
        "bulkhead_blast_radius_containment": True,
    }


def _policy() -> dict[str, object]:
    return {
        "failure_classification_for_transitions": True,
        "failure_classes": ["transient", "permanent", "throttle"],
        "retry_budget_policy_version": "2026.04",
        "transition_policy_version": "2026.04",
        "fallback_behavior_for_open_circuits": True,
        "fallback_mode": "serve_cached",
        "cooldown_seconds": 30,
        "half_open_probe_count": 2,
        "operator_safe_breaker_controls": True,
        "operator_approval_ticket": "CAB-2026-0177",
    }


def _telemetry() -> dict[str, object]:
    return {
        "plugin_id": "plugin-x",
        "state_transition_telemetry": True,
        "transition_policy_version": "2026.04",
        "transition_counts": {"open": 2, "half_open": 3, "closed": 4},
        "transition_events": [
            {
                "event_id": "evt-01",
                "from_state": "closed",
                "to_state": "open",
                "failure_class": "throttle",
                "retry_attempt": 1,
            },
            {
                "event_id": "evt-02",
                "from_state": "open",
                "to_state": "half_open",
                "failure_class": "transient",
                "retry_attempt": 1,
            },
            {
                "event_id": "evt-03",
                "from_state": "half_open",
                "to_state": "closed",
                "failure_class": "transient",
                "retry_attempt": 0,
            },
        ],
        "degraded_plugin_end_to_end_tests": True,
        "degraded_test_run_id": "cb-degraded-09-001",
    }


def test_plugin_circuit_breaker_gate_passes() -> None:
    report = evaluate_plugin_circuit_breaker_gate(
        run_id="run-feature-09-pass",
        mode="ci",
        runtime_state=_runtime(),
        policy=_policy(),
        telemetry=_telemetry(),
    )
    assert report["status"] == "pass"
    assert report["breaker_execution"]["events_processed"] == 3
    assert validate_plugin_circuit_breaker_report_dict(report) == []


def test_plugin_circuit_breaker_gate_fail_closes() -> None:
    policy = _policy()
    policy["fallback_behavior_for_open_circuits"] = False
    report = evaluate_plugin_circuit_breaker_gate(
        run_id="run-feature-09-fail",
        mode="preflight",
        runtime_state=_runtime(),
        policy=policy,
        telemetry=_telemetry(),
    )
    assert report["status"] == "fail"
    assert "fallback_behavior_for_open_circuits" in report["failed_gates"]


def test_plugin_circuit_breaker_gate_fail_closes_on_missing_transition_counts() -> None:
    telemetry = _telemetry()
    telemetry["transition_counts"] = {"open": 2, "closed": 4}
    report = evaluate_plugin_circuit_breaker_gate(
        run_id="run-feature-09-transition-counts-invalid",
        mode="preflight",
        runtime_state=_runtime(),
        policy=_policy(),
        telemetry=telemetry,
    )
    assert report["status"] == "fail"
    assert "state_transition_telemetry" in report["failed_gates"]


def test_plugin_circuit_breaker_gate_fail_closes_on_retry_budget_overflow() -> None:
    runtime_state = _runtime()
    runtime_state["retry_budget_remaining"] = 11
    report = evaluate_plugin_circuit_breaker_gate(
        run_id="run-feature-09-retry-budget-overflow",
        mode="preflight",
        runtime_state=runtime_state,
        policy=_policy(),
        telemetry=_telemetry(),
    )
    assert report["status"] == "fail"
    assert "plugin_level_retry_budget_enforcement" in report["failed_gates"]


def test_plugin_circuit_breaker_gate_fail_closes_on_degraded_test_without_open_transition() -> None:
    telemetry = _telemetry()
    telemetry["transition_counts"] = {"open": 0, "half_open": 3, "closed": 4}
    report = evaluate_plugin_circuit_breaker_gate(
        run_id="run-feature-09-degraded-without-open-transition",
        mode="preflight",
        runtime_state=_runtime(),
        policy=_policy(),
        telemetry=telemetry,
    )
    assert report["status"] == "fail"
    assert "degraded_plugin_end_to_end_tests" in report["failed_gates"]


def test_plugin_circuit_breaker_gate_fail_closes_on_transition_policy_version_drift() -> None:
    telemetry = _telemetry()
    telemetry["transition_policy_version"] = "2026.05"
    report = evaluate_plugin_circuit_breaker_gate(
        run_id="run-feature-09-transition-policy-version-drift",
        mode="preflight",
        runtime_state=_runtime(),
        policy=_policy(),
        telemetry=telemetry,
    )
    assert report["status"] == "fail"
    assert "state_transition_telemetry" in report["failed_gates"]


def test_plugin_circuit_breaker_gate_fail_closes_on_retry_budget_policy_version_drift() -> None:
    runtime_state = _runtime()
    runtime_state["retry_budget_policy_version"] = "2026.05"
    report = evaluate_plugin_circuit_breaker_gate(
        run_id="run-feature-09-retry-budget-policy-version-drift",
        mode="preflight",
        runtime_state=runtime_state,
        policy=_policy(),
        telemetry=_telemetry(),
    )
    assert report["status"] == "fail"
    assert "plugin_level_retry_budget_enforcement" in report["failed_gates"]


def test_plugin_circuit_breaker_gate_fail_closes_on_plugin_id_telemetry_drift() -> None:
    telemetry = _telemetry()
    telemetry["plugin_id"] = "plugin-y"
    report = evaluate_plugin_circuit_breaker_gate(
        run_id="run-feature-09-plugin-id-telemetry-drift",
        mode="preflight",
        runtime_state=_runtime(),
        policy=_policy(),
        telemetry=telemetry,
    )
    assert report["status"] == "fail"
    assert "state_transition_telemetry" in report["failed_gates"]


def test_plugin_circuit_breaker_gate_fail_closes_on_invalid_transition_event() -> None:
    telemetry = _telemetry()
    telemetry["transition_events"][0]["to_state"] = "unknown"
    report = evaluate_plugin_circuit_breaker_gate(
        run_id="run-feature-09-invalid-transition-event",
        mode="preflight",
        runtime_state=_runtime(),
        policy=_policy(),
        telemetry=telemetry,
    )
    assert report["status"] == "fail"
    assert "state_transition_telemetry" in report["failed_gates"]


def test_execute_plugin_circuit_breaker_runtime_detects_permanent_not_open() -> None:
    telemetry = _telemetry()
    telemetry["transition_events"][0] = {
        "event_id": "evt-10",
        "from_state": "closed",
        "to_state": "closed",
        "failure_class": "permanent",
        "retry_attempt": 0,
    }
    execution = execute_plugin_circuit_breaker_runtime(
        runtime_state=_runtime(),
        policy=_policy(),
        telemetry=telemetry,
    )
    assert "permanent_not_open:evt-10" in execution["runtime_failures"]


def test_transition_event_rows_render_from_report() -> None:
    report = evaluate_plugin_circuit_breaker_gate(
        run_id="run-feature-09-events",
        mode="ci",
        runtime_state=_runtime(),
        policy=_policy(),
        telemetry=_telemetry(),
    )
    rows = build_transition_event_rows(report=report)
    assert len(rows) == 3
    assert rows[0]["run_id"] == "run-feature-09-events"


def test_plugin_circuit_breaker_contract_deterministic() -> None:
    assert build_plugin_circuit_breaker_contract() == build_plugin_circuit_breaker_contract()


def test_plugin_circuit_breaker_history_appends() -> None:
    report = evaluate_plugin_circuit_breaker_gate(
        run_id="run-feature-09-history",
        mode="ci",
        runtime_state=_runtime(),
        policy=_policy(),
        telemetry=_telemetry(),
    )
    history = update_plugin_circuit_breaker_history(existing=[], report=report)
    assert history[0]["run_id"] == "run-feature-09-history"
    assert history[0]["retry_remaining_after"] == 5
