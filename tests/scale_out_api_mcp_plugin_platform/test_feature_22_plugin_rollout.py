from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_22_plugin_progressive_rollout_canary_rollback import (
    build_plugin_rollout_contract,
    evaluate_plugin_rollout_gate,
    update_plugin_rollout_history,
    validate_plugin_rollout_report_dict,
)


def _controller() -> dict[str, object]:
    return {
        "plugin_progressive_rollout_controller_built": True,
        "canary_cohorts_staged_traffic_supported": True,
        "active_plugin_version": "2.4.1",
        "stages": [
            {"cohort": "canary", "traffic_percent": 10},
            {"cohort": "ramp", "traffic_percent": 30},
            {"cohort": "stable", "traffic_percent": 60},
        ],
    }


def _health() -> dict[str, object]:
    return {
        "health_gated_promotion_enforced": True,
        "auto_rollback_on_slo_or_policy_breach": True,
        "error_rate_pct": 0.4,
        "latency_p95_ms": 180,
        "rollback_triggered": False,
        "rollout_actions_integrated_with_observability_signals": True,
        "observability_signal_ids": ["sig-01", "sig-02"],
    }


def _operations() -> dict[str, object]:
    return {
        "rollout_timeline_persisted_for_audit": True,
        "pause_resume_override_operations_available": True,
        "override_actions_count": 1,
        "canary_and_rollback_lifecycle_tested": True,
        "lifecycle_test_run_id": "rollout-lifecycle-22",
        "timeline_events": [
            {"type": "canary_start", "timestamp": "2026-04-22T10:01:00Z", "actor": "rollout-controller"},
            {"type": "promote", "timestamp": "2026-04-22T10:11:00Z", "actor": "rollout-controller"},
        ],
    }


def test_plugin_rollout_gate_passes_with_complete_inputs() -> None:
    report = evaluate_plugin_rollout_gate(
        run_id="run-feature-22-pass",
        mode="ci",
        controller=_controller(),
        health=_health(),
        operations=_operations(),
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert validate_plugin_rollout_report_dict(report) == []


def test_plugin_rollout_gate_fail_closes_on_missing_autorollback() -> None:
    health = _health()
    health["auto_rollback_on_slo_or_policy_breach"] = False
    report = evaluate_plugin_rollout_gate(
        run_id="run-feature-22-fail",
        mode="preflight",
        controller=_controller(),
        health=health,
        operations=_operations(),
    )
    assert report["status"] == "fail"
    assert "auto_rollback_on_slo_or_policy_breach" in report["failed_gates"]


def test_plugin_rollout_gate_fail_closes_on_invalid_stage_percent_total() -> None:
    controller = _controller()
    controller["stages"] = [
        {"cohort": "canary", "traffic_percent": 10},
        {"cohort": "ramp", "traffic_percent": 20},
    ]
    report = evaluate_plugin_rollout_gate(
        run_id="run-feature-22-stage-percent-invalid",
        mode="preflight",
        controller=controller,
        health=_health(),
        operations=_operations(),
    )
    assert report["status"] == "fail"
    assert "canary_cohorts_staged_traffic_supported" in report["failed_gates"]


def test_plugin_rollout_gate_fail_closes_on_rollback_without_timeline_event() -> None:
    health = _health()
    health["rollback_triggered"] = True
    report = evaluate_plugin_rollout_gate(
        run_id="run-feature-22-rollback-timeline-incoherent",
        mode="preflight",
        controller=_controller(),
        health=health,
        operations=_operations(),
    )
    assert report["status"] == "fail"
    assert "auto_rollback_on_slo_or_policy_breach" in report["failed_gates"]


def test_plugin_rollout_contract_is_deterministic() -> None:
    assert build_plugin_rollout_contract() == build_plugin_rollout_contract()


def test_plugin_rollout_history_appends_row() -> None:
    report = evaluate_plugin_rollout_gate(
        run_id="run-feature-22-history",
        mode="ci",
        controller=_controller(),
        health=_health(),
        operations=_operations(),
    )
    history = update_plugin_rollout_history(existing=[], report=report)
    assert history[0]["run_id"] == "run-feature-22-history"

