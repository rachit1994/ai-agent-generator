"""Runtime for feature 10 MCP broker/session lifecycle management."""

from __future__ import annotations

from typing import Any

from .contracts import MCP_BROKER_SCHEMA, MCP_BROKER_SCHEMA_VERSION


def build_mcp_session_contract() -> dict[str, object]:
    return {
        "apis": ["create_session", "resume_session", "terminate_session"],
        "states": ["created", "active", "idle", "expired", "terminated"],
        "lease_heartbeat": True,
        "reconnect_resume": True,
        "authz_required": True,
    }


def _broker_telemetry_aligned(broker_state: dict[str, Any], telemetry: dict[str, Any]) -> bool:
    broker_instance_id = broker_state.get("broker_instance_id")
    telemetry_broker_instance_id = telemetry.get("broker_instance_id")
    return (
        isinstance(broker_instance_id, str)
        and broker_instance_id.strip() != ""
        and broker_instance_id == telemetry_broker_instance_id
    )


def summarize_mcp_broker_health(
    *, broker_state: dict[str, Any], session_state: dict[str, Any], telemetry: dict[str, Any]
) -> dict[str, bool]:
    return {
        "broker_service_present": broker_state.get("broker_service_present") is True,
        "session_lifecycle_api_present": session_state.get("session_lifecycle_api_present") is True,
        "session_persistence_reclaim": session_state.get("session_persistence_reclaim") is True,
        "heartbeat_resume_supported": session_state.get("heartbeat_resume_supported") is True,
        "authz_boundary_enforced": broker_state.get("authz_boundary_enforced") is True,
        "deterministic_routing_present": broker_state.get("deterministic_routing_present") is True,
        "disconnect_failover_tests_present": session_state.get("disconnect_failover_tests_present") is True,
        "broker_observability_present": telemetry.get("broker_observability_present") is True
        and _broker_telemetry_aligned(broker_state, telemetry),
    }


def evaluate_mcp_broker_gate(
    *,
    run_id: str,
    mode: str,
    broker_state: dict[str, Any],
    session_state: dict[str, Any],
    telemetry: dict[str, Any],
) -> dict[str, Any]:
    checks = summarize_mcp_broker_health(
        broker_state=broker_state,
        session_state=session_state,
        telemetry=telemetry,
    )
    failed_gates = [name for name, passed in checks.items() if passed is not True]
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": MCP_BROKER_SCHEMA,
        "schema_version": MCP_BROKER_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "release_blocked": status == "fail",
        "checks": checks,
        "failed_gates": failed_gates,
        "session_contract": build_mcp_session_contract(),
        "evidence": {
            "broker_ref": "data/mcp_broker/broker_state.json",
            "sessions_ref": "data/mcp_broker/session_state.json",
            "telemetry_ref": "data/mcp_broker/telemetry.json",
            "history_ref": "data/mcp_broker/trend_history.jsonl",
        },
    }


def update_mcp_broker_history(*, existing: list[dict[str, Any]], report: dict[str, Any]) -> list[dict[str, Any]]:
    row = {
        "run_id": report["run_id"],
        "status": report["status"],
        "failed_gate_count": len(report["failed_gates"]),
    }
    return [*existing, row]

