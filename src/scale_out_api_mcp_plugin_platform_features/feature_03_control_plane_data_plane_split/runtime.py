"""Runtime for feature 03 control/data plane split."""

from __future__ import annotations

from typing import Any

from .contracts import PLANE_SPLIT_SCHEMA, PLANE_SPLIT_SCHEMA_VERSION


def build_plane_boundary_contract() -> dict[str, object]:
    return {
        "version": "v1",
        "control_api": ["schedule_job", "cancel_job", "get_job_status"],
        "data_api": ["execute_job", "report_result"],
        "auth_boundary": "mTLS+service-token",
        "isolation_policy": "no_direct_state_mutation",
    }


def _valid_auth_boundary(control: dict[str, Any], data: dict[str, Any]) -> bool:
    control_boundary = control.get("auth_boundary")
    data_boundary = data.get("auth_boundary")
    return (
        isinstance(control_boundary, str)
        and control_boundary in {"service-token", "mTLS+service-token"}
        and control_boundary == data_boundary
    )


def _valid_telemetry_partition(control: dict[str, Any], data: dict[str, Any]) -> bool:
    control_channel = control.get("telemetry_channel")
    data_channel = data.get("telemetry_channel")
    return (
        isinstance(control_channel, str)
        and control_channel.startswith("control-")
        and isinstance(data_channel, str)
        and data_channel.startswith("data-")
        and control_channel != data_channel
    )


def _valid_service_routing_names(control: dict[str, Any], data: dict[str, Any]) -> bool:
    control_service = control.get("service_name")
    data_service = data.get("service_name")
    return (
        isinstance(control_service, str)
        and control_service.startswith("control-")
        and isinstance(data_service, str)
        and data_service.startswith("data-")
        and control_service != data_service
    )


def _valid_scaling_partition(control: dict[str, Any], data: dict[str, Any]) -> bool:
    control_scaling = control.get("scaling_policy")
    data_scaling = data.get("scaling_policy")
    return (
        isinstance(control_scaling, str)
        and control_scaling.startswith("control-")
        and isinstance(data_scaling, str)
        and data_scaling.startswith("data-")
        and control_scaling != data_scaling
    )


def _valid_dispatch_event(event: Any) -> bool:
    if not isinstance(event, dict):
        return False
    required = ("event_id", "run_id", "from_plane", "to_plane", "route", "status")
    if not all(isinstance(event.get(key), str) and event.get(key).strip() != "" for key in required):
        return False
    if event.get("from_plane") != "control" or event.get("to_plane") != "data":
        return False
    if event.get("status") not in {"queued", "dispatched", "running", "succeeded", "failed"}:
        return False
    return event.get("route") in {"schedule_job", "cancel_job", "get_job_status", "execute_job", "report_result"}


def _collect_dispatch_events(control: dict[str, Any]) -> list[dict[str, Any]]:
    rows = control.get("dispatch_events")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if _valid_dispatch_event(row)]


def execute_plane_split_runtime(*, control: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
    events = _collect_dispatch_events(control)
    route_violations: list[str] = []
    dependency_violations: list[str] = []
    ownership_violations: list[str] = []
    control_owner = control.get("owner_team")
    data_owner = data.get("owner_team")
    for event in events:
        route = event["route"]
        if event["from_plane"] == "control" and route in {"execute_job", "report_result"}:
            route_violations.append(event["event_id"])
        if data.get("control_dependency") is True and event["status"] in {"running", "failed"}:
            dependency_violations.append(event["event_id"])
    if not (isinstance(control_owner, str) and control_owner.strip()):
        ownership_violations.append("control_owner_missing")
    if not (isinstance(data_owner, str) and data_owner.strip()):
        ownership_violations.append("data_owner_missing")
    if isinstance(control_owner, str) and isinstance(data_owner, str) and control_owner == data_owner:
        ownership_violations.append("shared_owner_team")
    rollback = control.get("rollback_runbook")
    rollback_ready = isinstance(rollback, str) and rollback.strip() != ""
    return {
        "events_processed": len(events),
        "route_violations": route_violations,
        "dependency_violations": dependency_violations,
        "ownership_violations": ownership_violations,
        "rollback_ready": rollback_ready,
    }


def summarize_plane_isolation(*, control: dict[str, Any], data: dict[str, Any]) -> dict[str, bool]:
    execution = execute_plane_split_runtime(control=control, data=data)
    return {
        "separate_services": _valid_service_routing_names(control, data),
        "separate_scaling": _valid_scaling_partition(control, data),
        "auth_boundary": _valid_auth_boundary(control, data),
        "telemetry_partitioned": _valid_telemetry_partition(control, data),
        "failure_isolated": data.get("control_dependency") is False
        and len(execution["dependency_violations"]) == 0
        and len(execution["route_violations"]) == 0,
        "operational_ownership_split": len(execution["ownership_violations"]) == 0,
        "plane_rollbacks_defined": execution["rollback_ready"] is True,
    }


def evaluate_plane_split_gate(
    *,
    run_id: str,
    mode: str,
    control: dict[str, Any],
    data: dict[str, Any],
) -> dict[str, Any]:
    execution = execute_plane_split_runtime(control=control, data=data)
    checks = summarize_plane_isolation(control=control, data=data)
    failed_gates = [name for name, passed in checks.items() if passed is not True]
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": PLANE_SPLIT_SCHEMA,
        "schema_version": PLANE_SPLIT_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "release_blocked": status == "fail",
        "checks": checks,
        "execution": execution,
        "failed_gates": failed_gates,
        "boundary_contract": build_plane_boundary_contract(),
        "evidence": {
            "control_ref": "data/plane_split/control_plane.json",
            "data_ref": "data/plane_split/data_plane.json",
            "boundary_ref": "data/plane_split/boundary_contract.json",
            "history_ref": "data/plane_split/trend_history.jsonl",
            "events_ref": "data/plane_split/plane_events.jsonl",
        },
    }


def update_plane_split_history(*, existing: list[dict[str, Any]], report: dict[str, Any]) -> list[dict[str, Any]]:
    execution = report.get("execution")
    row = {
        "run_id": report["run_id"],
        "status": report["status"],
        "failed_gate_count": len(report["failed_gates"]),
        "events_processed": execution.get("events_processed") if isinstance(execution, dict) else None,
    }
    return [*existing, row]


def build_plane_event_rows(*, report: dict[str, Any]) -> list[dict[str, Any]]:
    execution = report.get("execution")
    if not isinstance(execution, dict):
        return []
    return [
        {"run_id": report.get("run_id"), "signal": "events_processed", "value": execution.get("events_processed", 0)},
        {"run_id": report.get("run_id"), "signal": "route_violations", "value": len(execution.get("route_violations", []))},
        {"run_id": report.get("run_id"), "signal": "dependency_violations", "value": len(execution.get("dependency_violations", []))},
    ]

