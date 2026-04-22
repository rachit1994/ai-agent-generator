from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_12_plugin_runtime_bulkheads_trust_class import (
    build_bulkhead_event_rows,
    build_trust_bulkhead_contract,
    execute_trust_bulkhead_runtime,
    evaluate_bulkheads_gate,
    update_bulkheads_history,
    validate_bulkheads_report_dict,
)


def _policy() -> dict[str, object]:
    return {
        "trust_classes_defined_enforced": True,
        "trust_classes": ["trusted", "sandboxed", "untrusted"],
        "class_quotas": {"trusted": 10, "sandboxed": 5, "untrusted": 3},
        "boundary_policy_audit_controls": True,
        "trust_reclassification_safe": True,
    }


def _runtime() -> dict[str, object]:
    return {
        "execution_pools_segmented": True,
        "class_quotas_isolation_enforced": True,
        "cross_class_leakage_blocked": True,
        "boundary_containment_tests_present": True,
        "dispatch_events": [
            {
                "event_id": "evt-01",
                "plugin_id": "plugin-a",
                "trust_class": "trusted",
                "pool_id": "trusted-pool-1",
                "resource_units": 4,
            },
            {
                "event_id": "evt-02",
                "plugin_id": "plugin-b",
                "trust_class": "sandboxed",
                "pool_id": "sandboxed-pool-1",
                "resource_units": 3,
            },
            {
                "event_id": "evt-03",
                "plugin_id": "plugin-c",
                "trust_class": "untrusted",
                "pool_id": "untrusted-pool-1",
                "resource_units": 1,
            },
        ],
        "reclassifications": [{"plugin_id": "plugin-b", "approved": True, "ticket": "CAB-127"}],
    }


def _telemetry() -> dict[str, object]:
    return {
        "trust_class_telemetry_present": True,
        "class_event_counts": {"trusted": 4, "sandboxed": 3, "untrusted": 1},
    }


def test_trust_bulkheads_gate_passes_for_healthy_payloads() -> None:
    report = evaluate_bulkheads_gate(
        run_id="run-feature-12-pass",
        mode="ci",
        policy=_policy(),
        runtime_state=_runtime(),
        telemetry=_telemetry(),
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert report["execution"]["events_processed"] == 3
    assert validate_bulkheads_report_dict(report) == []


def test_trust_bulkheads_gate_fail_closes_on_missing_leakage_controls() -> None:
    runtime = _runtime()
    runtime["cross_class_leakage_blocked"] = False
    report = evaluate_bulkheads_gate(
        run_id="run-feature-12-leakage-missing",
        mode="preflight",
        policy=_policy(),
        runtime_state=runtime,
        telemetry=_telemetry(),
    )
    assert report["status"] == "fail"
    assert "cross_class_leakage_blocked" in report["failed_gates"]


def test_trust_bulkheads_gate_fail_closes_on_telemetry_trust_class_drift() -> None:
    telemetry = _telemetry()
    telemetry["class_event_counts"] = {"trusted": 8, "sandboxed": 3}
    report = evaluate_bulkheads_gate(
        run_id="run-feature-12-telemetry-class-drift",
        mode="preflight",
        policy=_policy(),
        runtime_state=_runtime(),
        telemetry=telemetry,
    )
    assert report["status"] == "fail"
    assert "trust_class_telemetry_present" in report["failed_gates"]


def test_trust_bulkheads_gate_fail_closes_on_pool_violation() -> None:
    runtime = _runtime()
    runtime["dispatch_events"][0]["pool_id"] = "sandboxed-pool-1"
    report = evaluate_bulkheads_gate(
        run_id="run-feature-12-pool-violation",
        mode="preflight",
        policy=_policy(),
        runtime_state=runtime,
        telemetry=_telemetry(),
    )
    assert report["status"] == "fail"
    assert "execution_pools_segmented" in report["failed_gates"]


def test_execute_trust_bulkhead_runtime_detects_quota_breach() -> None:
    runtime = _runtime()
    runtime["dispatch_events"][0]["resource_units"] = 99
    execution = execute_trust_bulkhead_runtime(
        policy=_policy(),
        runtime_state=runtime,
        telemetry=_telemetry(),
    )
    assert "trusted" in execution["quota_breaches"]


def test_build_bulkhead_event_rows_from_report() -> None:
    report = evaluate_bulkheads_gate(
        run_id="run-feature-12-events",
        mode="ci",
        policy=_policy(),
        runtime_state=_runtime(),
        telemetry=_telemetry(),
    )
    rows = build_bulkhead_event_rows(report=report)
    assert len(rows) == 3
    assert rows[0]["run_id"] == "run-feature-12-events"


def test_bulkhead_contract_is_deterministic() -> None:
    assert build_trust_bulkhead_contract() == build_trust_bulkhead_contract()


def test_bulkhead_history_appends_snapshot() -> None:
    report = evaluate_bulkheads_gate(
        run_id="run-feature-12-history",
        mode="ci",
        policy=_policy(),
        runtime_state=_runtime(),
        telemetry=_telemetry(),
    )
    history = update_bulkheads_history(existing=[], report=report)
    assert len(history) == 1
    assert history[0]["run_id"] == "run-feature-12-history"
    assert history[0]["events_processed"] == 3

