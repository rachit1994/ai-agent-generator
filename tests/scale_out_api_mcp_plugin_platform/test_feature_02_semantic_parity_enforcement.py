from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_02_local_and_server_semantic_parity_enforcement import (
    build_parity_matrix,
    evaluate_semantic_parity,
    update_parity_history,
    validate_semantic_parity_report_dict,
)


def _runtime_payload() -> dict[str, object]:
    return {
        "idempotency": [{"operation": "invoke", "request_hash": "a1", "result_hash": "r1", "replay_safe": True}],
        "authz": [{"role": "dev", "resource": "tool:x", "decision": "allow", "reason_code": "ok"}],
        "state_transitions": [
            {"operation": "run", "from_state": "queued", "to_state": "active", "transition_valid": True}
        ],
        "error_taxonomy": [{"operation": "invoke", "error_code": "none", "retryable": False, "class": "ok"}],
    }


def test_semantic_parity_passes_for_matching_payloads() -> None:
    payload = _runtime_payload()
    report = evaluate_semantic_parity(
        run_id="run-feature-02-pass",
        mode="ci",
        local=payload,
        server=payload,
        contract_package="sde.semantic_contracts.v1",
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert validate_semantic_parity_report_dict(report) == []


def test_semantic_parity_fail_closes_for_authz_drift() -> None:
    local = _runtime_payload()
    server = _runtime_payload()
    server["authz"] = [{"role": "dev", "resource": "tool:x", "decision": "deny", "reason_code": "policy"}]
    report = evaluate_semantic_parity(
        run_id="run-feature-02-authz-drift",
        mode="preflight",
        local=local,
        server=server,
        contract_package="sde.semantic_contracts.v1",
    )
    assert report["status"] == "fail"
    assert report["release_blocked"] is True
    assert "authz_parity_drift" in report["failed_gates"]


def test_parity_matrix_is_deterministic() -> None:
    assert build_parity_matrix() == build_parity_matrix()


def test_update_parity_history_appends_snapshot() -> None:
    payload = _runtime_payload()
    report = evaluate_semantic_parity(
        run_id="run-feature-02-history",
        mode="ci",
        local=payload,
        server=payload,
        contract_package="sde.semantic_contracts.v1",
    )
    updated = update_parity_history(existing=[], report=report)
    assert len(updated) == 1
    assert updated[0]["run_id"] == "run-feature-02-history"

