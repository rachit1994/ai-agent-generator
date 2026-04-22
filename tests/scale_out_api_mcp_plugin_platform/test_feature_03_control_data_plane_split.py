from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_03_control_plane_data_plane_split import (
    build_plane_boundary_contract,
    build_plane_event_rows,
    evaluate_plane_split_gate,
    execute_plane_split_runtime,
    update_plane_split_history,
    validate_plane_split_report_dict,
)


def _control_payload() -> dict[str, object]:
    return {
        "service_name": "control-plane-api",
        "scaling_policy": "control-cpu_target_60",
        "auth_boundary": "service-token",
        "telemetry_channel": "control-traces",
        "owner_team": "platform-control",
        "rollback_runbook": "RB-CONTROL-003",
        "dispatch_events": [
            {
                "event_id": "evt-001",
                "run_id": "run-feature-03-pass",
                "from_plane": "control",
                "to_plane": "data",
                "route": "schedule_job",
                "status": "dispatched",
            }
        ],
    }


def _data_payload() -> dict[str, object]:
    return {
        "service_name": "data-plane-worker",
        "scaling_policy": "data-queue_depth_target",
        "auth_boundary": "service-token",
        "telemetry_channel": "data-traces",
        "control_dependency": False,
        "owner_team": "platform-data",
    }


def test_plane_split_gate_passes_for_isolated_planes() -> None:
    report = evaluate_plane_split_gate(
        run_id="run-feature-03-pass",
        mode="ci",
        control=_control_payload(),
        data=_data_payload(),
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert validate_plane_split_report_dict(report) == []


def test_plane_split_gate_fail_closes_on_shared_service_name() -> None:
    control = _control_payload()
    data = _data_payload()
    data["service_name"] = "control-plane-api"
    report = evaluate_plane_split_gate(
        run_id="run-feature-03-shared-service",
        mode="preflight",
        control=control,
        data=data,
    )
    assert report["status"] == "fail"
    assert "separate_services" in report["failed_gates"]


def test_plane_split_gate_fail_closes_on_invalid_telemetry_partition() -> None:
    control = _control_payload()
    data = _data_payload()
    data["telemetry_channel"] = "control-traces"
    report = evaluate_plane_split_gate(
        run_id="run-feature-03-telemetry-partition-invalid",
        mode="preflight",
        control=control,
        data=data,
    )
    assert report["status"] == "fail"
    assert "telemetry_partitioned" in report["failed_gates"]


def test_plane_split_gate_fail_closes_on_invalid_service_namespace() -> None:
    control = _control_payload()
    data = _data_payload()
    control["service_name"] = "api-control-plane"
    report = evaluate_plane_split_gate(
        run_id="run-feature-03-service-namespace-invalid",
        mode="preflight",
        control=control,
        data=data,
    )
    assert report["status"] == "fail"
    assert "separate_services" in report["failed_gates"]


def test_plane_split_gate_fail_closes_on_invalid_scaling_namespace() -> None:
    control = _control_payload()
    control["scaling_policy"] = "cpu_target_60"
    report = evaluate_plane_split_gate(
        run_id="run-feature-03-scaling-namespace-invalid",
        mode="preflight",
        control=control,
        data=_data_payload(),
    )
    assert report["status"] == "fail"
    assert "separate_scaling" in report["failed_gates"]


def test_boundary_contract_is_deterministic() -> None:
    assert build_plane_boundary_contract() == build_plane_boundary_contract()


def test_execute_plane_split_runtime_detects_route_violation() -> None:
    control = _control_payload()
    control["dispatch_events"] = [
        {
            "event_id": "evt-009",
            "run_id": "run-feature-03-route-violation",
            "from_plane": "control",
            "to_plane": "data",
            "route": "execute_job",
            "status": "running",
        }
    ]
    execution = execute_plane_split_runtime(control=control, data=_data_payload())
    assert execution["route_violations"] == ["evt-009"]


def test_plane_split_gate_fail_closes_on_shared_ownership() -> None:
    control = _control_payload()
    data = _data_payload()
    data["owner_team"] = "platform-control"
    report = evaluate_plane_split_gate(
        run_id="run-feature-03-shared-ownership",
        mode="preflight",
        control=control,
        data=data,
    )
    assert report["status"] == "fail"
    assert "operational_ownership_split" in report["failed_gates"]


def test_plane_split_gate_fail_closes_when_rollback_missing() -> None:
    control = _control_payload()
    control["rollback_runbook"] = ""
    report = evaluate_plane_split_gate(
        run_id="run-feature-03-missing-rollback",
        mode="preflight",
        control=control,
        data=_data_payload(),
    )
    assert report["status"] == "fail"
    assert "plane_rollbacks_defined" in report["failed_gates"]


def test_plane_split_history_appends_snapshot() -> None:
    report = evaluate_plane_split_gate(
        run_id="run-feature-03-history",
        mode="ci",
        control=_control_payload(),
        data=_data_payload(),
    )
    history = update_plane_split_history(existing=[], report=report)
    assert len(history) == 1
    assert history[0]["run_id"] == "run-feature-03-history"
    assert history[0]["events_processed"] == 1


def test_build_plane_event_rows_contains_three_signals() -> None:
    report = evaluate_plane_split_gate(
        run_id="run-feature-03-events",
        mode="ci",
        control=_control_payload(),
        data=_data_payload(),
    )
    rows = build_plane_event_rows(report=report)
    assert len(rows) == 3

