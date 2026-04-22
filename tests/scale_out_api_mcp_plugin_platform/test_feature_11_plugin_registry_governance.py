from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_11_plugin_registry_compatibility_governance import (
    build_registry_event_rows,
    build_plugin_registry_contract,
    evaluate_plugin_registry_gate,
    execute_plugin_registry_runtime,
    update_plugin_registry_history,
    validate_plugin_registry_report_dict,
)


def _registry() -> dict[str, object]:
    return {
        "registry_service_present": True,
        "metadata_version_contract_enforced": True,
        "provenance_signature_verified": True,
        "publish_events": [
            {
                "event_id": "reg-evt-001",
                "plugin_id": "plugin-x",
                "version": "1.4.0",
                "signature_valid": True,
                "compatibility_pass": True,
                "decision": "published",
            },
            {
                "event_id": "reg-evt-002",
                "plugin_id": "plugin-y",
                "version": "2.0.0",
                "signature_valid": True,
                "compatibility_pass": False,
                "decision": "rejected",
            },
        ],
    }


def _compatibility() -> dict[str, object]:
    return {
        "compatibility_matrix_automated": True,
        "incompatible_rejection_tests_present": True,
        "compatibility_matrix_version": "2026.04",
        "tested_plugins": ["plugin-x", "plugin-y"],
    }


def _governance() -> dict[str, object]:
    return {
        "publish_rollout_gated": True,
        "canary_percent": 10,
        "rollout_strategy": "canary",
        "compatibility_matrix_version": "2026.04",
        "deprecation_rollback_governed": True,
        "governance_audit_history_persisted": True,
    }


def test_plugin_registry_gate_passes_for_healthy_payloads() -> None:
    report = evaluate_plugin_registry_gate(
        run_id="run-feature-11-pass",
        mode="ci",
        registry_state=_registry(),
        compatibility_matrix=_compatibility(),
        governance=_governance(),
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert validate_plugin_registry_report_dict(report) == []


def test_plugin_registry_gate_fail_closes_on_missing_signature_verification() -> None:
    registry = _registry()
    registry["provenance_signature_verified"] = False
    report = evaluate_plugin_registry_gate(
        run_id="run-feature-11-signature-missing",
        mode="preflight",
        registry_state=registry,
        compatibility_matrix=_compatibility(),
        governance=_governance(),
    )
    assert report["status"] == "fail"
    assert "provenance_signature_verified" in report["failed_gates"]


def test_plugin_registry_gate_fail_closes_on_invalid_rollout_governance() -> None:
    governance = _governance()
    governance["canary_percent"] = 0
    report = evaluate_plugin_registry_gate(
        run_id="run-feature-11-invalid-rollout-governance",
        mode="preflight",
        registry_state=_registry(),
        compatibility_matrix=_compatibility(),
        governance=governance,
    )
    assert report["status"] == "fail"
    assert "publish_rollout_gated" in report["failed_gates"]


def test_plugin_registry_gate_fail_closes_on_compatibility_matrix_version_drift() -> None:
    governance = _governance()
    governance["compatibility_matrix_version"] = "2026.05"
    report = evaluate_plugin_registry_gate(
        run_id="run-feature-11-compatibility-version-drift",
        mode="preflight",
        registry_state=_registry(),
        compatibility_matrix=_compatibility(),
        governance=governance,
    )
    assert report["status"] == "fail"
    assert "compatibility_matrix_automated" in report["failed_gates"]


def test_execute_plugin_registry_runtime_detects_invalid_publish_decision() -> None:
    registry = _registry()
    registry["publish_events"][1]["decision"] = "published"
    execution = execute_plugin_registry_runtime(
        registry_state=registry,
        compatibility_matrix=_compatibility(),
        governance=_governance(),
    )
    assert execution["decision_violations"] == ["reg-evt-002"]


def test_plugin_registry_gate_fail_closes_on_matrix_coverage_gap() -> None:
    compatibility = _compatibility()
    compatibility["tested_plugins"] = ["plugin-x"]
    report = evaluate_plugin_registry_gate(
        run_id="run-feature-11-matrix-coverage-gap",
        mode="preflight",
        registry_state=_registry(),
        compatibility_matrix=compatibility,
        governance=_governance(),
    )
    assert report["status"] == "fail"
    assert "runtime_matrix_coverage_valid" in report["failed_gates"]


def test_registry_contract_is_deterministic() -> None:
    assert build_plugin_registry_contract() == build_plugin_registry_contract()


def test_plugin_registry_history_appends_snapshot() -> None:
    report = evaluate_plugin_registry_gate(
        run_id="run-feature-11-history",
        mode="ci",
        registry_state=_registry(),
        compatibility_matrix=_compatibility(),
        governance=_governance(),
    )
    history = update_plugin_registry_history(existing=[], report=report)
    assert len(history) == 1
    assert history[0]["run_id"] == "run-feature-11-history"
    assert history[0]["events_processed"] == 2


def test_build_registry_event_rows_contains_signals() -> None:
    report = evaluate_plugin_registry_gate(
        run_id="run-feature-11-events",
        mode="ci",
        registry_state=_registry(),
        compatibility_matrix=_compatibility(),
        governance=_governance(),
    )
    rows = build_registry_event_rows(report=report)
    assert len(rows) == 3

