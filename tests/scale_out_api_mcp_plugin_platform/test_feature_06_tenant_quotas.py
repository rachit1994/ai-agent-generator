from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_06_per_tenant_quotas_concurrency_budgets import (
    build_quota_event_rows,
    build_tenant_quota_contract,
    evaluate_tenant_quota_gate,
    execute_tenant_quota_runtime,
    update_tenant_quota_history,
    validate_tenant_quota_report_dict,
)


def _quota() -> dict[str, object]:
    return {
        "tenant_identity_threaded": True,
        "tenant_scope": "tenant-a",
        "durable_quota_state": True,
        "refill_window_supported": True,
        "refill_window_seconds": 60,
        "admin_controls_present": True,
        "quota_policy_version": "2026.04",
        "tenant_limits": {"tenant-a": 5},
        "tenant_usage": {"tenant-a": 2},
    }


def _scheduler() -> dict[str, object]:
    return {
        "hard_limit_enforced": True,
        "fairness_policy_enforced": True,
        "rejection_reasons_present": True,
        "tenant_scope": "tenant-a",
        "refill_window_seconds": 60,
        "quota_policy_version": "2026.04",
        "rejection_reason_codes": ["tenant_quota_exhausted", "tenant_concurrency_exhausted"],
        "admission_events": [
            {
                "event_id": "quota-evt-001",
                "tenant_id": "tenant-a",
                "requested_slots": 2,
                "status": "admitted",
                "reason_code": "tenant_concurrency_exhausted",
            },
            {
                "event_id": "quota-evt-002",
                "tenant_id": "tenant-a",
                "requested_slots": 4,
                "status": "rejected",
                "reason_code": "tenant_quota_exhausted",
            },
        ],
    }


def _obs() -> dict[str, object]:
    return {
        "tenant_observability_present": True,
        "tenant_scope": "tenant-a",
        "refill_window_seconds": 60,
        "quota_policy_version": "2026.04",
        "tracked_rejection_reason_codes": ["tenant_quota_exhausted", "tenant_concurrency_exhausted"],
        "rejection_count": 1,
    }


def test_tenant_quota_gate_passes_for_healthy_payloads() -> None:
    report = evaluate_tenant_quota_gate(
        run_id="run-feature-06-pass",
        mode="ci",
        quota_state=_quota(),
        scheduler_state=_scheduler(),
        observability=_obs(),
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert validate_tenant_quota_report_dict(report) == []


def test_tenant_quota_gate_fail_closes_on_missing_fairness() -> None:
    scheduler = _scheduler()
    scheduler["fairness_policy_enforced"] = False
    report = evaluate_tenant_quota_gate(
        run_id="run-feature-06-fairness-missing",
        mode="preflight",
        quota_state=_quota(),
        scheduler_state=scheduler,
        observability=_obs(),
    )
    assert report["status"] == "fail"
    assert "fairness_policy_enforced" in report["failed_gates"]


def test_tenant_quota_gate_fail_closes_on_missing_rejection_reason_codes() -> None:
    scheduler = _scheduler()
    scheduler["rejection_reason_codes"] = []
    report = evaluate_tenant_quota_gate(
        run_id="run-feature-06-rejection-reason-codes-missing",
        mode="preflight",
        quota_state=_quota(),
        scheduler_state=scheduler,
        observability=_obs(),
    )
    assert report["status"] == "fail"
    assert "rejection_reasons_present" in report["failed_gates"]


def test_tenant_quota_gate_fail_closes_on_observability_reason_drift() -> None:
    observability = _obs()
    observability["tracked_rejection_reason_codes"] = ["tenant_quota_exhausted"]
    report = evaluate_tenant_quota_gate(
        run_id="run-feature-06-observability-reason-drift",
        mode="preflight",
        quota_state=_quota(),
        scheduler_state=_scheduler(),
        observability=observability,
    )
    assert report["status"] == "fail"
    assert "tenant_observability_present" in report["failed_gates"]


def test_tenant_quota_gate_fail_closes_on_policy_version_drift() -> None:
    scheduler = _scheduler()
    scheduler["quota_policy_version"] = "2026.05"
    report = evaluate_tenant_quota_gate(
        run_id="run-feature-06-policy-version-drift",
        mode="preflight",
        quota_state=_quota(),
        scheduler_state=scheduler,
        observability=_obs(),
    )
    assert report["status"] == "fail"
    assert "admin_controls_present" in report["failed_gates"]


def test_tenant_quota_gate_fail_closes_on_refill_window_seconds_drift() -> None:
    scheduler = _scheduler()
    scheduler["refill_window_seconds"] = 30
    report = evaluate_tenant_quota_gate(
        run_id="run-feature-06-refill-window-seconds-drift",
        mode="preflight",
        quota_state=_quota(),
        scheduler_state=scheduler,
        observability=_obs(),
    )
    assert report["status"] == "fail"
    assert "refill_window_supported" in report["failed_gates"]


def test_tenant_quota_gate_fail_closes_on_tenant_scope_drift() -> None:
    observability = _obs()
    observability["tenant_scope"] = "tenant-b"
    report = evaluate_tenant_quota_gate(
        run_id="run-feature-06-tenant-scope-drift",
        mode="preflight",
        quota_state=_quota(),
        scheduler_state=_scheduler(),
        observability=observability,
    )
    assert report["status"] == "fail"
    assert "tenant_identity_threaded" in report["failed_gates"]


def test_tenant_quota_contract_is_deterministic() -> None:
    assert build_tenant_quota_contract() == build_tenant_quota_contract()


def test_execute_tenant_quota_runtime_detects_missing_rejection_reason() -> None:
    scheduler = _scheduler()
    scheduler["admission_events"][1].pop("reason_code")
    execution = execute_tenant_quota_runtime(
        quota_state=_quota(), scheduler_state=scheduler, observability=_obs()
    )
    assert execution["missing_reason_violations"] == ["quota-evt-002"]


def test_tenant_quota_gate_fail_closes_on_rejection_metric_drift() -> None:
    observability = _obs()
    observability["rejection_count"] = 0
    report = evaluate_tenant_quota_gate(
        run_id="run-feature-06-rejection-metric-drift",
        mode="preflight",
        quota_state=_quota(),
        scheduler_state=_scheduler(),
        observability=observability,
    )
    assert report["status"] == "fail"
    assert "runtime_rejection_metrics_coherent" in report["failed_gates"]


def test_tenant_quota_history_appends_snapshot() -> None:
    report = evaluate_tenant_quota_gate(
        run_id="run-feature-06-history",
        mode="ci",
        quota_state=_quota(),
        scheduler_state=_scheduler(),
        observability=_obs(),
    )
    history = update_tenant_quota_history(existing=[], report=report)
    assert len(history) == 1
    assert history[0]["run_id"] == "run-feature-06-history"
    assert history[0]["events_processed"] == 2


def test_build_quota_event_rows_contains_signals() -> None:
    report = evaluate_tenant_quota_gate(
        run_id="run-feature-06-events",
        mode="ci",
        quota_state=_quota(),
        scheduler_state=_scheduler(),
        observability=_obs(),
    )
    rows = build_quota_event_rows(report=report)
    assert len(rows) == 3

