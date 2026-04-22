"""Contracts for feature 10 MCP broker session lifecycle management."""

from __future__ import annotations

from typing import Any

MCP_BROKER_SCHEMA = "sde.scale.feature_10.mcp_broker.v1"
MCP_BROKER_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "broker_ref": "data/mcp_broker/broker_state.json",
    "sessions_ref": "data/mcp_broker/session_state.json",
    "telemetry_ref": "data/mcp_broker/telemetry.json",
    "history_ref": "data/mcp_broker/trend_history.jsonl",
}


def validate_mcp_broker_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["mcp_broker_not_object"]
    errors: list[str] = []
    if body.get("schema") != MCP_BROKER_SCHEMA:
        errors.append("mcp_broker_schema")
    if body.get("schema_version") != MCP_BROKER_SCHEMA_VERSION:
        errors.append("mcp_broker_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("mcp_broker_mode")
    if body.get("status") not in _STATUSES:
        errors.append("mcp_broker_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("mcp_broker_run_id")
    if not isinstance(body.get("failed_gates"), list):
        errors.append("mcp_broker_failed_gates")
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return [*errors, "mcp_broker_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if evidence.get(key) != expected:
            errors.append(f"mcp_broker_evidence_ref:{key}")
    return errors

