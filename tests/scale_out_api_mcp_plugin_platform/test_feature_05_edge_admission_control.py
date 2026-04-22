from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_05_edge_admission_control_rate_limits_retry_after import (
    build_admission_event_rows,
    build_edge_policy_contract,
    evaluate_edge_admission_gate,
    execute_edge_admission_runtime,
    update_edge_admission_history,
    validate_edge_admission_report_dict,
)


def _policy() -> dict[str, object]:
    return {
        "edge_middleware_present": True,
        "scoped_limits_present": True,
        "scope_keys": ["tenant_id", "user_id", "api_key", "route"],
        "burst_sustained_budgets": True,
        "burst_limit_per_minute": 60,
        "sustained_limit_per_hour": 600,
        "outage_policy_defined": True,
        "outage_mode": "fail_closed",
        "dynamic_policy_updates_safe": True,
        "policy_version": "edge-policy-v1",
        "max_retry_after_seconds": 60,
    }


def _counters() -> dict[str, object]:
    return {
        "deny_throttle_metrics": True,
        "deny_count": 1,
        "throttle_count": 1,
        "sampled_requests": 3,
    }


def _traffic() -> dict[str, object]:
    return {
        "retry_after_compliant": True,
        "retry_after_seconds": 15,
        "integration_load_tests_present": True,
        "load_test_profile": "burst-and-sustained-traffic",
        "request_events": [
            {
                "event_id": "edge-evt-001",
                "tenant_id": "tenant-a",
                "user_id": "user-1",
                "api_key": "key-1",
                "route": "/v1/chat",
                "decision": "allow",
                "retry_after_seconds": 0,
            },
            {
                "event_id": "edge-evt-002",
                "tenant_id": "tenant-a",
                "user_id": "user-1",
                "api_key": "key-1",
                "route": "/v1/chat",
                "decision": "throttle",
                "retry_after_seconds": 15,
            },
            {
                "event_id": "edge-evt-003",
                "tenant_id": "tenant-a",
                "user_id": "user-2",
                "api_key": "key-2",
                "route": "/v1/tools",
                "decision": "deny",
                "retry_after_seconds": 30,
            },
        ],
    }


def test_edge_admission_gate_passes_for_healthy_payloads() -> None:
    report = evaluate_edge_admission_gate(
        run_id="run-feature-05-pass",
        mode="ci",
        policy=_policy(),
        counters=_counters(),
        traffic_sample=_traffic(),
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert validate_edge_admission_report_dict(report) == []


def test_edge_admission_gate_fail_closes_on_missing_retry_after() -> None:
    traffic = _traffic()
    traffic["retry_after_compliant"] = False
    report = evaluate_edge_admission_gate(
        run_id="run-feature-05-retry-after-missing",
        mode="preflight",
        policy=_policy(),
        counters=_counters(),
        traffic_sample=traffic,
    )
    assert report["status"] == "fail"
    assert "retry_after_compliant" in report["failed_gates"]


def test_edge_admission_gate_fail_closes_on_invalid_scope_keys() -> None:
    policy = _policy()
    policy["scope_keys"] = ["tenant_id", "route"]
    report = evaluate_edge_admission_gate(
        run_id="run-feature-05-invalid-scope-keys",
        mode="preflight",
        policy=policy,
        counters=_counters(),
        traffic_sample=_traffic(),
    )
    assert report["status"] == "fail"
    assert "scoped_limits_present" in report["failed_gates"]


def test_edge_admission_gate_fail_closes_on_retry_after_exceeds_policy_cap() -> None:
    traffic = _traffic()
    traffic["retry_after_seconds"] = 120
    report = evaluate_edge_admission_gate(
        run_id="run-feature-05-retry-after-cap-exceeded",
        mode="preflight",
        policy=_policy(),
        counters=_counters(),
        traffic_sample=traffic,
    )
    assert report["status"] == "fail"
    assert "retry_after_compliant" in report["failed_gates"]


def test_execute_edge_admission_runtime_detects_counter_drift() -> None:
    counters = _counters()
    counters["deny_count"] = 0
    execution = execute_edge_admission_runtime(
        policy=_policy(),
        counters=counters,
        traffic_sample=_traffic(),
    )
    assert execution["counter_coherent"] is False


def test_edge_admission_gate_fail_closes_on_runtime_scope_violation() -> None:
    traffic = _traffic()
    traffic["request_events"][0]["tenant_id"] = ""
    report = evaluate_edge_admission_gate(
        run_id="run-feature-05-runtime-scope-violation",
        mode="preflight",
        policy=_policy(),
        counters=_counters(),
        traffic_sample=traffic,
    )
    assert report["status"] == "fail"
    assert "runtime_scope_keys_consistent" in report["failed_gates"]


def test_edge_policy_contract_is_deterministic() -> None:
    assert build_edge_policy_contract() == build_edge_policy_contract()


def test_edge_admission_history_appends_snapshot() -> None:
    report = evaluate_edge_admission_gate(
        run_id="run-feature-05-history",
        mode="ci",
        policy=_policy(),
        counters=_counters(),
        traffic_sample=_traffic(),
    )
    history = update_edge_admission_history(existing=[], report=report)
    assert len(history) == 1
    assert history[0]["run_id"] == "run-feature-05-history"
    assert history[0]["events_processed"] == 3


def test_build_admission_event_rows_contains_signals() -> None:
    report = evaluate_edge_admission_gate(
        run_id="run-feature-05-events",
        mode="ci",
        policy=_policy(),
        counters=_counters(),
        traffic_sample=_traffic(),
    )
    rows = build_admission_event_rows(report=report)
    assert len(rows) == 3

