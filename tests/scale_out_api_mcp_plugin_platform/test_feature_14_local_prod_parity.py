from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_14_local_prod_semantic_parity_gates import (
    build_local_prod_parity_contract,
    evaluate_local_prod_parity_gate,
    update_local_prod_parity_history,
    validate_local_prod_parity_report_dict,
)


def _result_payload() -> dict[str, object]:
    return {
        "semantic_outputs": {"decision": "allow", "code": 200},
        "state_transitions": ["queued", "active", "done"],
        "errors": [],
        "authz": {"scope": "tenant:read", "decision": "allow"},
        "idempotency": {"replay_safe": True},
    }


def test_local_prod_parity_gate_passes_for_matching_payloads() -> None:
    payload = _result_payload()
    report = evaluate_local_prod_parity_gate(
        run_id="run-feature-14-pass",
        mode="ci",
        local_results=payload,
        prod_results=payload,
        diff={"diagnostics": []},
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert validate_local_prod_parity_report_dict(report) == []


def test_local_prod_parity_gate_fail_closes_on_error_drift() -> None:
    local = _result_payload()
    prod = _result_payload()
    prod["errors"] = [{"code": "E_TIMEOUT"}]
    report = evaluate_local_prod_parity_gate(
        run_id="run-feature-14-error-drift",
        mode="preflight",
        local_results=local,
        prod_results=prod,
        diff={"diagnostics": ["error mismatch"]},
    )
    assert report["status"] == "fail"
    assert "errors_match" in report["failed_gates"]


def test_local_prod_parity_contract_is_deterministic() -> None:
    assert build_local_prod_parity_contract() == build_local_prod_parity_contract()


def test_local_prod_parity_history_appends_snapshot() -> None:
    payload = _result_payload()
    report = evaluate_local_prod_parity_gate(
        run_id="run-feature-14-history",
        mode="ci",
        local_results=payload,
        prod_results=payload,
        diff={"diagnostics": []},
    )
    history = update_local_prod_parity_history(existing=[], report=report)
    assert len(history) == 1
    assert history[0]["run_id"] == "run-feature-14-history"

