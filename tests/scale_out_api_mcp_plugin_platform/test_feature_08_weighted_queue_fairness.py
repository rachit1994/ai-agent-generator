from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_08_distributed_queue_fairness_weighted_scheduling import (
    build_scheduler_event_rows,
    build_weighted_queue_fairness_contract,
    evaluate_weighted_queue_fairness_gate,
    execute_weighted_scheduler_runtime,
    update_weighted_queue_fairness_history,
    validate_weighted_queue_fairness_report_dict,
)


def _scheduler() -> dict[str, object]:
    return {
        "queue_backend": "memory_sim",
        "tenant_weights": {"tenant-a": 5, "tenant-b": 3},
        "plugin_weights": {"plugin-x": 4, "plugin-y": 2},
        "scheduler_state_version": 2,
        "replay_cursor": "cursor-0002",
        "replay_applied_decisions": 48,
        "decision_log_entries": 120,
        "replay_hash": "trace-hash-008",
        "dispatch_events": [
            {
                "event_id": "sched-001",
                "tenant": "tenant-a",
                "plugin": "plugin-x",
                "status": "scheduled",
                "wait_ms": 35,
            },
            {
                "event_id": "sched-002",
                "tenant": "tenant-b",
                "plugin": "plugin-y",
                "status": "scheduled",
                "wait_ms": 45,
            },
            {
                "event_id": "sched-003",
                "tenant": "tenant-b",
                "plugin": "plugin-y",
                "status": "dropped",
                "wait_ms": 0,
            },
        ],
    }


def _telemetry() -> dict[str, object]:
    return {
        "fairness_score": 0.93,
        "p95_wait_ms": 47,
        "class_wait_p95_ms": {"tenant-a": 42, "tenant-b": 47},
        "mixed_load_stress_validation": True,
        "mixed_load_samples": 180,
        "deterministic_trace_hash": "trace-hash-008",
    }


def _policy() -> dict[str, object]:
    return {
        "starvation_prevention_aging_policy": True,
        "safe_admin_weight_tuning_controls": True,
        "last_admin_change_ticket": "CAB-2026-0042",
        "deterministic_scheduler_tests": True,
        "admin_tuning_range": {"min": 1, "max": 20},
        "deterministic_trace_hash": "trace-hash-008",
    }


def test_weighted_queue_fairness_gate_passes_for_complete_inputs() -> None:
    report = evaluate_weighted_queue_fairness_gate(
        run_id="run-feature-08-pass",
        mode="ci",
        scheduler=_scheduler(),
        telemetry=_telemetry(),
        policy=_policy(),
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert validate_weighted_queue_fairness_report_dict(report) == []


def test_weighted_queue_fairness_gate_fail_closes_on_missing_aging_policy() -> None:
    policy = _policy()
    policy["starvation_prevention_aging_policy"] = False
    report = evaluate_weighted_queue_fairness_gate(
        run_id="run-feature-08-fail",
        mode="preflight",
        scheduler=_scheduler(),
        telemetry=_telemetry(),
        policy=policy,
    )
    assert report["status"] == "fail"
    assert "starvation_prevention_aging_policy" in report["failed_gates"]


def test_weighted_queue_fairness_gate_fail_closes_on_invalid_weights() -> None:
    scheduler = _scheduler()
    scheduler["tenant_weights"] = {"tenant-a": 0}
    report = evaluate_weighted_queue_fairness_gate(
        run_id="run-feature-08-weight-invalid",
        mode="preflight",
        scheduler=scheduler,
        telemetry=_telemetry(),
        policy=_policy(),
    )
    assert report["status"] == "fail"
    assert "tenant_plugin_priority_weighting_supported" in report["failed_gates"]


def test_weighted_queue_fairness_gate_fail_closes_on_replay_drift() -> None:
    scheduler = _scheduler()
    scheduler["replay_applied_decisions"] = 200
    report = evaluate_weighted_queue_fairness_gate(
        run_id="run-feature-08-replay-drift",
        mode="preflight",
        scheduler=scheduler,
        telemetry=_telemetry(),
        policy=_policy(),
    )
    assert report["status"] == "fail"
    assert "scheduler_replay_consistency" in report["failed_gates"]


def test_weighted_queue_fairness_gate_fail_closes_on_telemetry_scope_drift() -> None:
    telemetry = _telemetry()
    telemetry["class_wait_p95_ms"] = {"tenant-a": 42, "tenant-c": 51}
    report = evaluate_weighted_queue_fairness_gate(
        run_id="run-feature-08-telemetry-scope-drift",
        mode="preflight",
        scheduler=_scheduler(),
        telemetry=telemetry,
        policy=_policy(),
    )
    assert report["status"] == "fail"
    assert "fairness_wait_time_telemetry_published" in report["failed_gates"]


def test_weighted_queue_fairness_gate_fail_closes_on_incoherent_global_p95_wait() -> None:
    telemetry = _telemetry()
    telemetry["p95_wait_ms"] = 46
    report = evaluate_weighted_queue_fairness_gate(
        run_id="run-feature-08-p95-incoherent",
        mode="preflight",
        scheduler=_scheduler(),
        telemetry=telemetry,
        policy=_policy(),
    )
    assert report["status"] == "fail"
    assert "fairness_wait_time_telemetry_published" in report["failed_gates"]


def test_execute_weighted_scheduler_runtime_detects_replay_hash_mismatch() -> None:
    telemetry = _telemetry()
    telemetry["deterministic_trace_hash"] = "trace-hash-other"
    execution = execute_weighted_scheduler_runtime(scheduler=_scheduler(), telemetry=telemetry)
    assert execution["deterministic_replay_ok"] is False


def test_weighted_queue_fairness_gate_fail_closes_on_starvation_runtime_violation() -> None:
    scheduler = _scheduler()
    scheduler["dispatch_events"][0]["wait_ms"] = 80
    report = evaluate_weighted_queue_fairness_gate(
        run_id="run-feature-08-starvation-runtime-violation",
        mode="preflight",
        scheduler=scheduler,
        telemetry=_telemetry(),
        policy=_policy(),
    )
    assert report["status"] == "fail"
    assert "runtime_starvation_prevented" in report["failed_gates"]


def test_weighted_queue_fairness_contract_is_deterministic() -> None:
    assert build_weighted_queue_fairness_contract() == build_weighted_queue_fairness_contract()


def test_weighted_queue_fairness_history_appends_row() -> None:
    report = evaluate_weighted_queue_fairness_gate(
        run_id="run-feature-08-history",
        mode="ci",
        scheduler=_scheduler(),
        telemetry=_telemetry(),
        policy=_policy(),
    )
    history = update_weighted_queue_fairness_history(existing=[], report=report)
    assert history[0]["run_id"] == "run-feature-08-history"
    assert history[0]["events_processed"] == 3


def test_build_scheduler_event_rows_contains_expected_signals() -> None:
    report = evaluate_weighted_queue_fairness_gate(
        run_id="run-feature-08-events",
        mode="ci",
        scheduler=_scheduler(),
        telemetry=_telemetry(),
        policy=_policy(),
    )
    rows = build_scheduler_event_rows(report=report)
    assert len(rows) == 4

