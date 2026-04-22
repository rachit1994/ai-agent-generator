from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_10_mcp_broker_session_lifecycle_management import (
    build_mcp_session_contract,
    evaluate_mcp_broker_gate,
    update_mcp_broker_history,
    validate_mcp_broker_report_dict,
)


def _broker() -> dict[str, object]:
    return {
        "broker_service_present": True,
        "broker_instance_id": "broker-a1",
        "authz_boundary_enforced": True,
        "deterministic_routing_present": True,
    }


def _sessions() -> dict[str, object]:
    return {
        "session_lifecycle_api_present": True,
        "session_persistence_reclaim": True,
        "heartbeat_resume_supported": True,
        "disconnect_failover_tests_present": True,
    }


def _telemetry() -> dict[str, object]:
    return {"broker_observability_present": True, "broker_instance_id": "broker-a1"}


def test_mcp_broker_gate_passes_for_healthy_payloads() -> None:
    report = evaluate_mcp_broker_gate(
        run_id="run-feature-10-pass",
        mode="ci",
        broker_state=_broker(),
        session_state=_sessions(),
        telemetry=_telemetry(),
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert validate_mcp_broker_report_dict(report) == []


def test_mcp_broker_gate_fail_closes_on_missing_authz() -> None:
    broker = _broker()
    broker["authz_boundary_enforced"] = False
    report = evaluate_mcp_broker_gate(
        run_id="run-feature-10-authz-missing",
        mode="preflight",
        broker_state=broker,
        session_state=_sessions(),
        telemetry=_telemetry(),
    )
    assert report["status"] == "fail"
    assert "authz_boundary_enforced" in report["failed_gates"]


def test_mcp_broker_gate_fail_closes_on_broker_instance_id_drift() -> None:
    telemetry = _telemetry()
    telemetry["broker_instance_id"] = "broker-b2"
    report = evaluate_mcp_broker_gate(
        run_id="run-feature-10-broker-instance-id-drift",
        mode="preflight",
        broker_state=_broker(),
        session_state=_sessions(),
        telemetry=telemetry,
    )
    assert report["status"] == "fail"
    assert "broker_observability_present" in report["failed_gates"]


def test_mcp_session_contract_is_deterministic() -> None:
    assert build_mcp_session_contract() == build_mcp_session_contract()


def test_mcp_broker_history_appends_snapshot() -> None:
    report = evaluate_mcp_broker_gate(
        run_id="run-feature-10-history",
        mode="ci",
        broker_state=_broker(),
        session_state=_sessions(),
        telemetry=_telemetry(),
    )
    history = update_mcp_broker_history(existing=[], report=report)
    assert len(history) == 1
    assert history[0]["run_id"] == "run-feature-10-history"

