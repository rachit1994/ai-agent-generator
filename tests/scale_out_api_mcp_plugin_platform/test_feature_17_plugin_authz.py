from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_17_plugin_authz_scopes_least_privilege import (
    build_authz_event_rows,
    build_plugin_authz_contract,
    evaluate_plugin_authz_gate,
    execute_plugin_authz_runtime,
    update_plugin_authz_history,
    validate_plugin_authz_report_dict,
)


def _taxonomy() -> dict[str, object]:
    return {
        "scope_taxonomy_permission_model_defined": True,
        "policy_model_version": "2026.04",
        "scope_catalog": ["read:artifacts", "write:artifacts", "execute:tools"],
    }


def _policy() -> dict[str, object]:
    return {
        "least_privilege_policy_engine_implemented": True,
        "policy_model_version": "2026.04",
        "scope_checks_every_invocation": True,
        "deny_by_default_enforced": True,
        "policy_authoring_simulation_versioned": True,
        "escalation_scope_confusion_tests_present": True,
        "admin_policy_controls_present": True,
        "allowed_scopes_by_plugin": {
            "plugin-a": ["read:artifacts"],
            "plugin-b": ["read:artifacts", "execute:tools"],
        },
    }


def _audit() -> dict[str, object]:
    return {
        "allow_deny_decisions_audited": True,
        "allow_decisions": 1,
        "deny_decisions": 1,
        "total_decisions": 2,
        "decision_events": [
            {
                "event_id": "authz-evt-001",
                "plugin_id": "plugin-a",
                "scope": "read:artifacts",
                "decision": "allow",
            },
            {
                "event_id": "authz-evt-002",
                "plugin_id": "plugin-a",
                "scope": "write:artifacts",
                "decision": "deny",
            },
        ],
    }


def test_plugin_authz_gate_passes_for_healthy_payloads() -> None:
    report = evaluate_plugin_authz_gate(
        run_id="run-feature-17-pass",
        mode="ci",
        taxonomy=_taxonomy(),
        policy_state=_policy(),
        audit_logs=_audit(),
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert validate_plugin_authz_report_dict(report) == []


def test_plugin_authz_gate_fail_closes_on_missing_deny_default() -> None:
    policy = _policy()
    policy["deny_by_default_enforced"] = False
    report = evaluate_plugin_authz_gate(
        run_id="run-feature-17-deny-default-missing",
        mode="preflight",
        taxonomy=_taxonomy(),
        policy_state=policy,
        audit_logs=_audit(),
    )
    assert report["status"] == "fail"
    assert "deny_by_default_enforced" in report["failed_gates"]


def test_plugin_authz_gate_fail_closes_on_audit_metrics_mismatch() -> None:
    audit = _audit()
    audit["total_decisions"] = 25
    report = evaluate_plugin_authz_gate(
        run_id="run-feature-17-audit-metrics-mismatch",
        mode="preflight",
        taxonomy=_taxonomy(),
        policy_state=_policy(),
        audit_logs=audit,
    )
    assert report["status"] == "fail"
    assert "allow_deny_decisions_audited" in report["failed_gates"]


def test_plugin_authz_gate_fail_closes_on_policy_model_version_drift() -> None:
    policy = _policy()
    policy["policy_model_version"] = "2026.05"
    report = evaluate_plugin_authz_gate(
        run_id="run-feature-17-policy-model-version-drift",
        mode="preflight",
        taxonomy=_taxonomy(),
        policy_state=policy,
        audit_logs=_audit(),
    )
    assert report["status"] == "fail"
    assert "scope_taxonomy_permission_model_defined" in report["failed_gates"]


def test_execute_plugin_authz_runtime_detects_decision_violation() -> None:
    audit = _audit()
    audit["decision_events"][1]["decision"] = "allow"
    execution = execute_plugin_authz_runtime(
        taxonomy=_taxonomy(),
        policy_state=_policy(),
        audit_logs=audit,
    )
    assert execution["decision_violations"] == ["authz-evt-002"]


def test_plugin_authz_gate_fail_closes_on_unknown_scope() -> None:
    audit = _audit()
    audit["decision_events"][0]["scope"] = "delete:artifacts"
    report = evaluate_plugin_authz_gate(
        run_id="run-feature-17-unknown-scope",
        mode="preflight",
        taxonomy=_taxonomy(),
        policy_state=_policy(),
        audit_logs=audit,
    )
    assert report["status"] == "fail"
    assert "runtime_scope_catalog_valid" in report["failed_gates"]


def test_plugin_authz_contract_is_deterministic() -> None:
    assert build_plugin_authz_contract() == build_plugin_authz_contract()


def test_plugin_authz_history_appends_snapshot() -> None:
    report = evaluate_plugin_authz_gate(
        run_id="run-feature-17-history",
        mode="ci",
        taxonomy=_taxonomy(),
        policy_state=_policy(),
        audit_logs=_audit(),
    )
    history = update_plugin_authz_history(existing=[], report=report)
    assert len(history) == 1
    assert history[0]["run_id"] == "run-feature-17-history"
    assert history[0]["events_processed"] == 2


def test_build_authz_event_rows_contains_signals() -> None:
    report = evaluate_plugin_authz_gate(
        run_id="run-feature-17-events",
        mode="ci",
        taxonomy=_taxonomy(),
        policy_state=_policy(),
        audit_logs=_audit(),
    )
    rows = build_authz_event_rows(report=report)
    assert len(rows) == 3

