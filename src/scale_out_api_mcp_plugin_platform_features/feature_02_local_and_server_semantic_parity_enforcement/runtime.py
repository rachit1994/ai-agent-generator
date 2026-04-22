"""Runtime for feature 02 semantic parity enforcement."""

from __future__ import annotations

from typing import Any

from .contracts import SEMANTIC_PARITY_SCHEMA, SEMANTIC_PARITY_SCHEMA_VERSION


def build_parity_matrix() -> dict[str, list[str]]:
    return {
        "idempotency": ["operation", "request_hash", "result_hash", "replay_safe"],
        "authz": ["role", "resource", "decision", "reason_code"],
        "state_transitions": ["operation", "from_state", "to_state", "transition_valid"],
        "error_taxonomy": ["operation", "error_code", "retryable", "class"],
    }


def summarize_parity_drift(*, local: dict[str, Any], server: dict[str, Any]) -> dict[str, list[str]]:
    drift: dict[str, list[str]] = {"idempotency": [], "authz": [], "state_transitions": [], "error_taxonomy": []}
    for key in drift:
        local_rows = local.get(key, [])
        server_rows = server.get(key, [])
        if local_rows != server_rows:
            drift[key].append("payload_mismatch")
    return drift


def evaluate_semantic_parity(
    *,
    run_id: str,
    mode: str,
    local: dict[str, Any],
    server: dict[str, Any],
    contract_package: str,
) -> dict[str, Any]:
    drift = summarize_parity_drift(local=local, server=server)
    failed_gates: list[str] = []
    if drift["idempotency"]:
        failed_gates.append("idempotency_parity_drift")
    if drift["authz"]:
        failed_gates.append("authz_parity_drift")
    if drift["state_transitions"]:
        failed_gates.append("state_transition_parity_drift")
    if drift["error_taxonomy"]:
        failed_gates.append("error_taxonomy_parity_drift")
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": SEMANTIC_PARITY_SCHEMA,
        "schema_version": SEMANTIC_PARITY_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "contract_package": contract_package,
        "status": status,
        "release_blocked": status == "fail",
        "failed_gates": failed_gates,
        "drift": drift,
        "matrix": build_parity_matrix(),
        "evidence": {
            "parity_matrix_ref": "data/semantic_parity/parity_matrix.json",
            "local_ref": "data/semantic_parity/local_runtime.json",
            "server_ref": "data/semantic_parity/server_runtime.json",
            "history_ref": "data/semantic_parity/trend_history.jsonl",
        },
    }


def update_parity_history(*, existing: list[dict[str, Any]], report: dict[str, Any]) -> list[dict[str, Any]]:
    row = {
        "run_id": report["run_id"],
        "status": report["status"],
        "drift_count": len(report["failed_gates"]),
    }
    return [*existing, row]

