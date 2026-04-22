from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_13_sandbox_hardening_egress_cgroups_limits import (
    build_runtime_event_rows,
    build_sandbox_policy_contract,
    evaluate_sandbox_hardening_gate,
    execute_sandbox_runtime,
    update_sandbox_hardening_history,
    validate_sandbox_hardening_report_dict,
)


def _policy() -> dict[str, object]:
    return {
        "default_egress": "deny",
        "egress_allowlist": ["api.openai.com", "storage.internal"],
        "max_timeout_ms": 60000,
        "startup_policy_validation_enforced": True,
        "policy_versioned_validated": True,
        "policy_version": "1.2.0",
        "syscall_allowlist": ["read", "write", "close"],
        "read_only_mounts": ["/usr", "/bin"],
        "syscall_default_action": "deny",
    }


def _runtime() -> dict[str, object]:
    return {
        "sandbox_isolation_runtime_present": True,
        "cgroup_resource_limits_enforced": True,
        "applied_policy_version": "1.2.0",
        "cpu_limit_millis": 1500,
        "memory_limit_mb": 512,
        "pid_limit": 128,
        "fd_limit": 512,
        "filesystem_syscall_restricted": True,
        "timeouts_hard_kill_enforced": True,
        "timeout_ms": 30000,
        "kill_signal": "SIGKILL",
        "escape_detection_kill_switch_enforced": True,
        "escape_exhaustion_tests_present": True,
        "runtime_events": [
            {
                "event_id": "rt-001",
                "type": "egress_attempt",
                "host": "malicious.example",
                "status": "denied",
                "timestamp": "2026-04-22T10:00:10Z",
            },
            {
                "event_id": "rt-002",
                "type": "resource_sample",
                "cpu_millis": 1200,
                "memory_mb": 420,
                "status": "ok",
                "timestamp": "2026-04-22T10:00:11Z",
            },
            {
                "event_id": "rt-003",
                "type": "escape_probe",
                "status": "denied",
                "timestamp": "2026-04-22T10:00:12Z",
            },
        ],
    }


def _audit() -> dict[str, object]:
    return {
        "denied_ops_count": 2,
        "denied_events": [
            {
                "event_id": "deny-001",
                "action": "network.connect",
                "reason": "egress_allowlist_violation",
                "timestamp": "2026-04-22T10:01:00Z",
            },
            {
                "event_id": "deny-002",
                "action": "syscall.unshare",
                "reason": "syscall_filtered",
                "timestamp": "2026-04-22T10:02:00Z",
            },
        ],
    }


def test_sandbox_hardening_gate_passes_for_healthy_payloads() -> None:
    report = evaluate_sandbox_hardening_gate(
        run_id="run-feature-13-pass",
        mode="ci",
        policy=_policy(),
        runtime_state=_runtime(),
        audit_logs=_audit(),
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert validate_sandbox_hardening_report_dict(report) == []


def test_sandbox_hardening_gate_fail_closes_on_missing_egress_allowlist() -> None:
    policy = _policy()
    policy["default_egress"] = "allow"
    report = evaluate_sandbox_hardening_gate(
        run_id="run-feature-13-egress-missing",
        mode="preflight",
        policy=policy,
        runtime_state=_runtime(),
        audit_logs=_audit(),
    )
    assert report["status"] == "fail"
    assert "egress_allowlist_enforced" in report["failed_gates"]


def test_sandbox_hardening_gate_fail_closes_on_missing_kill_switch() -> None:
    runtime_state = _runtime()
    runtime_state["escape_detection_kill_switch_enforced"] = False
    report = evaluate_sandbox_hardening_gate(
        run_id="run-feature-13-kill-switch-missing",
        mode="preflight",
        policy=_policy(),
        runtime_state=runtime_state,
        audit_logs=_audit(),
    )
    assert report["status"] == "fail"
    assert "escape_detection_kill_switch_enforced" in report["failed_gates"]


def test_sandbox_hardening_gate_fail_closes_on_timeout_exceeding_policy_max() -> None:
    runtime_state = _runtime()
    runtime_state["timeout_ms"] = 70000
    report = evaluate_sandbox_hardening_gate(
        run_id="run-feature-13-timeout-over-policy-max",
        mode="preflight",
        policy=_policy(),
        runtime_state=runtime_state,
        audit_logs=_audit(),
    )
    assert report["status"] == "fail"
    assert "timeouts_hard_kill_enforced" in report["failed_gates"]


def test_sandbox_hardening_gate_fail_closes_on_invalid_policy_version() -> None:
    policy = _policy()
    policy["policy_version"] = "v1"
    report = evaluate_sandbox_hardening_gate(
        run_id="run-feature-13-policy-version-invalid",
        mode="preflight",
        policy=policy,
        runtime_state=_runtime(),
        audit_logs=_audit(),
    )
    assert report["status"] == "fail"
    assert "policy_versioned_validated" in report["failed_gates"]


def test_sandbox_hardening_gate_fail_closes_on_policy_version_drift() -> None:
    runtime_state = _runtime()
    runtime_state["applied_policy_version"] = "1.1.9"
    report = evaluate_sandbox_hardening_gate(
        run_id="run-feature-13-policy-version-drift",
        mode="preflight",
        policy=_policy(),
        runtime_state=runtime_state,
        audit_logs=_audit(),
    )
    assert report["status"] == "fail"
    assert "policy_versioned_validated" in report["failed_gates"]


def test_sandbox_hardening_gate_fail_closes_on_invalid_allowlist_host() -> None:
    policy = _policy()
    policy["egress_allowlist"] = ["api openai com"]
    report = evaluate_sandbox_hardening_gate(
        run_id="run-feature-13-invalid-allowlist-host",
        mode="preflight",
        policy=policy,
        runtime_state=_runtime(),
        audit_logs=_audit(),
    )
    assert report["status"] == "fail"
    assert "egress_allowlist_enforced" in report["failed_gates"]


def test_sandbox_hardening_gate_fail_closes_on_unstructured_deny_timestamp() -> None:
    audit_logs = _audit()
    audit_logs["denied_events"] = [{"action": "network.connect", "reason": "egress_allowlist_violation"}]
    audit_logs["denied_ops_count"] = 1
    report = evaluate_sandbox_hardening_gate(
        run_id="run-feature-13-deny-event-timestamp-missing",
        mode="preflight",
        policy=_policy(),
        runtime_state=_runtime(),
        audit_logs=audit_logs,
    )
    assert report["status"] == "fail"
    assert "deny_audit_events_structured" in report["failed_gates"]


def test_sandbox_hardening_gate_fail_closes_on_out_of_order_deny_events() -> None:
    audit_logs = _audit()
    audit_logs["denied_events"] = [
        {
            "event_id": "deny-002",
            "action": "syscall.unshare",
            "reason": "syscall_filtered",
            "timestamp": "2026-04-22T10:02:00Z",
        },
        {
            "event_id": "deny-001",
            "action": "network.connect",
            "reason": "egress_allowlist_violation",
            "timestamp": "2026-04-22T10:01:00Z",
        },
    ]
    report = evaluate_sandbox_hardening_gate(
        run_id="run-feature-13-deny-event-order-invalid",
        mode="preflight",
        policy=_policy(),
        runtime_state=_runtime(),
        audit_logs=audit_logs,
    )
    assert report["status"] == "fail"
    assert "deny_audit_events_structured" in report["failed_gates"]


def test_sandbox_hardening_gate_fail_closes_on_unknown_deny_reason() -> None:
    audit_logs = _audit()
    audit_logs["denied_events"][0]["reason"] = "unknown_reason"
    report = evaluate_sandbox_hardening_gate(
        run_id="run-feature-13-deny-reason-invalid",
        mode="preflight",
        policy=_policy(),
        runtime_state=_runtime(),
        audit_logs=audit_logs,
    )
    assert report["status"] == "fail"
    assert "deny_audit_events_structured" in report["failed_gates"]


def test_sandbox_hardening_gate_fail_closes_on_duplicate_deny_event_id() -> None:
    audit_logs = _audit()
    audit_logs["denied_events"][1]["event_id"] = "deny-001"
    report = evaluate_sandbox_hardening_gate(
        run_id="run-feature-13-deny-event-id-duplicate",
        mode="preflight",
        policy=_policy(),
        runtime_state=_runtime(),
        audit_logs=audit_logs,
    )
    assert report["status"] == "fail"
    assert "deny_audit_events_structured" in report["failed_gates"]


def test_execute_sandbox_runtime_detects_resource_violation() -> None:
    runtime_state = _runtime()
    runtime_state["runtime_events"] = [
        {
            "event_id": "rt-009",
            "type": "resource_sample",
            "cpu_millis": 2000,
            "memory_mb": 420,
            "status": "ok",
            "timestamp": "2026-04-22T10:00:20Z",
        }
    ]
    execution = execute_sandbox_runtime(policy=_policy(), runtime_state=runtime_state, audit_logs=_audit())
    assert execution["resource_violations"] == ["rt-009"]


def test_sandbox_hardening_gate_fail_closes_on_runtime_escape_violation() -> None:
    runtime_state = _runtime()
    runtime_state["runtime_events"][2]["status"] = "allowed"
    report = evaluate_sandbox_hardening_gate(
        run_id="run-feature-13-runtime-escape-violation",
        mode="preflight",
        policy=_policy(),
        runtime_state=runtime_state,
        audit_logs=_audit(),
    )
    assert report["status"] == "fail"
    assert "runtime_escape_contained" in report["failed_gates"]


def test_sandbox_policy_contract_is_deterministic() -> None:
    assert build_sandbox_policy_contract() == build_sandbox_policy_contract()


def test_sandbox_history_appends_snapshot() -> None:
    report = evaluate_sandbox_hardening_gate(
        run_id="run-feature-13-history",
        mode="ci",
        policy=_policy(),
        runtime_state=_runtime(),
        audit_logs=_audit(),
    )
    history = update_sandbox_hardening_history(existing=[], report=report)
    assert len(history) == 1
    assert history[0]["run_id"] == "run-feature-13-history"
    assert history[0]["events_processed"] == 3


def test_build_runtime_event_rows_contains_signals() -> None:
    report = evaluate_sandbox_hardening_gate(
        run_id="run-feature-13-events",
        mode="ci",
        policy=_policy(),
        runtime_state=_runtime(),
        audit_logs=_audit(),
    )
    rows = build_runtime_event_rows(report=report)
    assert len(rows) == 4

