from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_18_cross_tenant_isolation_plugin_tool_execution import (
    build_isolation_event_rows,
    build_cross_tenant_contract,
    execute_cross_tenant_isolation_runtime,
    evaluate_cross_tenant_isolation_gate,
    update_cross_tenant_isolation_history,
    validate_cross_tenant_isolation_report_dict,
)


def _execution() -> dict[str, object]:
    return {
        "tenant_identity_full_path": True,
        "tenant_id": "tenant-a",
        "tenant_budget_profile_id": "budget-standard-v1",
        "execution_events": [
            {
                "event_id": "evt-01",
                "tenant_id": "tenant-a",
                "plugin_id": "plugin-x",
                "queue_namespace": "tenant-a/queue",
                "storage_namespace": "tenant-a/storage",
                "cache_namespace": "tenant-a/cache",
                "key_scope": "tenant-a:key-v1",
            },
            {
                "event_id": "evt-02",
                "tenant_id": "tenant-a",
                "plugin_id": "plugin-y",
                "queue_namespace": "tenant-a/queue",
                "storage_namespace": "tenant-a/storage",
                "cache_namespace": "tenant-a/cache",
                "key_scope": "tenant-a:key-v1",
            },
        ],
        "adversarial_tests": [
            {"name": "cross-tenant-cache-poison", "result": "blocked"},
            {"name": "cross-tenant-queue-replay", "result": "blocked"},
        ],
    }


def _isolation() -> dict[str, object]:
    return {
        "tenant_id": "tenant-a",
        "tenant_budget_profile_id": "budget-standard-v1",
        "tenant_key_policy_version": "2026.04.1",
        "runtime_queue_storage_isolated": True,
        "cache_artifact_reuse_blocked": True,
        "tenant_keys_policy_controls_applied": True,
        "tenant_budgets_guardrails_enforced": True,
        "adversarial_leakage_tests_present": True,
    }


def _audit() -> dict[str, object]:
    return {
        "tenant_id": "tenant-a",
        "tenant_budget_profile_id": "budget-standard-v1",
        "tenant_key_policy_version": "2026.04.1",
        "continuous_isolation_audit_present": True,
        "incident_containment_actions_defined": True,
        "containment_actions": ["kill-tenant-workers", "revoke-tenant-keys"],
    }


def test_cross_tenant_isolation_gate_passes_for_healthy_payloads() -> None:
    report = evaluate_cross_tenant_isolation_gate(
        run_id="run-feature-18-pass",
        mode="ci",
        execution_context=_execution(),
        isolation_state=_isolation(),
        audit_signals=_audit(),
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert report["execution"]["events_processed"] == 2
    assert validate_cross_tenant_isolation_report_dict(report) == []


def test_cross_tenant_isolation_gate_fail_closes_on_missing_identity() -> None:
    execution = _execution()
    execution["tenant_identity_full_path"] = False
    report = evaluate_cross_tenant_isolation_gate(
        run_id="run-feature-18-identity-missing",
        mode="preflight",
        execution_context=execution,
        isolation_state=_isolation(),
        audit_signals=_audit(),
    )
    assert report["status"] == "fail"
    assert "tenant_identity_full_path" in report["failed_gates"]


def test_cross_tenant_isolation_gate_fail_closes_on_tenant_id_drift() -> None:
    isolation = _isolation()
    isolation["tenant_id"] = "tenant-b"
    report = evaluate_cross_tenant_isolation_gate(
        run_id="run-feature-18-tenant-id-drift",
        mode="preflight",
        execution_context=_execution(),
        isolation_state=isolation,
        audit_signals=_audit(),
    )
    assert report["status"] == "fail"
    assert "tenant_identity_full_path" in report["failed_gates"]


def test_cross_tenant_isolation_gate_fail_closes_on_key_policy_version_drift() -> None:
    audit = _audit()
    audit["tenant_key_policy_version"] = "2026.04.2"
    report = evaluate_cross_tenant_isolation_gate(
        run_id="run-feature-18-key-policy-version-drift",
        mode="preflight",
        execution_context=_execution(),
        isolation_state=_isolation(),
        audit_signals=audit,
    )
    assert report["status"] == "fail"
    assert "tenant_keys_policy_controls_applied" in report["failed_gates"]


def test_cross_tenant_isolation_gate_fail_closes_on_budget_profile_drift() -> None:
    isolation = _isolation()
    isolation["tenant_budget_profile_id"] = "budget-premium-v2"
    report = evaluate_cross_tenant_isolation_gate(
        run_id="run-feature-18-budget-profile-drift",
        mode="preflight",
        execution_context=_execution(),
        isolation_state=isolation,
        audit_signals=_audit(),
    )
    assert report["status"] == "fail"
    assert "tenant_budget_profile_consistent" in report["failed_gates"]


def test_cross_tenant_isolation_gate_fail_closes_on_namespace_violation() -> None:
    execution = _execution()
    execution["execution_events"][0]["storage_namespace"] = "tenant-b/storage"
    report = evaluate_cross_tenant_isolation_gate(
        run_id="run-feature-18-namespace-violation",
        mode="preflight",
        execution_context=execution,
        isolation_state=_isolation(),
        audit_signals=_audit(),
    )
    assert report["status"] == "fail"
    assert "runtime_queue_storage_isolated" in report["failed_gates"]


def test_execute_cross_tenant_isolation_runtime_detects_leakage_attempt() -> None:
    execution = _execution()
    execution["execution_events"][1]["tenant_id"] = "tenant-b"
    result = execute_cross_tenant_isolation_runtime(
        execution_context=execution,
        audit_signals=_audit(),
    )
    assert len(result["leakage_attempts"]) == 1


def test_build_isolation_event_rows_from_report() -> None:
    report = evaluate_cross_tenant_isolation_gate(
        run_id="run-feature-18-events",
        mode="ci",
        execution_context=_execution(),
        isolation_state=_isolation(),
        audit_signals=_audit(),
    )
    rows = build_isolation_event_rows(report=report)
    assert len(rows) == 3
    assert rows[0]["run_id"] == "run-feature-18-events"


def test_cross_tenant_contract_is_deterministic() -> None:
    assert build_cross_tenant_contract() == build_cross_tenant_contract()


def test_cross_tenant_history_appends_snapshot() -> None:
    report = evaluate_cross_tenant_isolation_gate(
        run_id="run-feature-18-history",
        mode="ci",
        execution_context=_execution(),
        isolation_state=_isolation(),
        audit_signals=_audit(),
    )
    history = update_cross_tenant_isolation_history(existing=[], report=report)
    assert len(history) == 1
    assert history[0]["run_id"] == "run-feature-18-history"
    assert history[0]["events_processed"] == 2

