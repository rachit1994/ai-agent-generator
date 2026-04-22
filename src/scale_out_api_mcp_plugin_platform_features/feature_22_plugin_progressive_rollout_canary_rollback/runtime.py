"""Runtime for feature 22 plugin progressive rollout gate."""

from __future__ import annotations

from typing import Any

from .contracts import PLUGIN_ROLLOUT_SCHEMA, PLUGIN_ROLLOUT_SCHEMA_VERSION


def build_plugin_rollout_contract() -> dict[str, object]:
    return {
        "progressive_rollout_controller": True,
        "canary_cohorts_and_traffic_percentages": True,
        "health_gated_promotion_logic": True,
        "auto_rollback_on_slo_policy_breach": True,
        "rollout_timeline_auditability": True,
        "pause_resume_override_operations": True,
        "full_canary_rollback_lifecycle_tests": True,
        "rollout_observability_signal_integration": True,
    }


def _valid_stages(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    total = 0
    for stage in value:
        if not isinstance(stage, dict):
            return False
        cohort = stage.get("cohort")
        traffic = stage.get("traffic_percent")
        if not isinstance(cohort, str) or not cohort.strip():
            return False
        if not isinstance(traffic, int) or traffic <= 0 or traffic > 100:
            return False
        total += traffic
    return total == 100


def _valid_timeline_events(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    for event in value:
        if not isinstance(event, dict):
            return False
        if event.get("type") not in {"canary_start", "promote", "rollback", "pause", "resume"}:
            return False
        if not isinstance(event.get("timestamp"), str) or "T" not in event.get("timestamp"):
            return False
        if not isinstance(event.get("actor"), str) or not event.get("actor").strip():
            return False
    return True


def _rollback_timeline_coherent(health: dict[str, Any], operations: dict[str, Any]) -> bool:
    rollback_triggered = health.get("rollback_triggered")
    timeline_events = operations.get("timeline_events")
    if rollback_triggered is not True:
        return rollback_triggered is False
    if not isinstance(timeline_events, list):
        return False
    return any(
        isinstance(event, dict) and event.get("type") == "rollback"
        for event in timeline_events
    )


def summarize_plugin_rollout_health(
    *, controller: dict[str, Any], health: dict[str, Any], operations: dict[str, Any]
) -> dict[str, bool]:
    return {
        "plugin_progressive_rollout_controller_built": controller.get(
            "plugin_progressive_rollout_controller_built"
        )
        is True
        and isinstance(controller.get("active_plugin_version"), str)
        and controller.get("active_plugin_version").strip() != "",
        "canary_cohorts_staged_traffic_supported": controller.get(
            "canary_cohorts_staged_traffic_supported"
        )
        is True
        and _valid_stages(controller.get("stages")),
        "health_gated_promotion_enforced": health.get("health_gated_promotion_enforced") is True
        and isinstance(health.get("error_rate_pct"), (int, float))
        and float(health.get("error_rate_pct")) >= 0.0
        and isinstance(health.get("latency_p95_ms"), int)
        and health.get("latency_p95_ms") >= 0,
        "auto_rollback_on_slo_or_policy_breach": health.get("auto_rollback_on_slo_or_policy_breach")
        is True
        and health.get("rollback_triggered") in {True, False}
        and _rollback_timeline_coherent(health, operations),
        "rollout_timeline_persisted_for_audit": operations.get("rollout_timeline_persisted_for_audit")
        is True
        and _valid_timeline_events(operations.get("timeline_events")),
        "pause_resume_override_operations_available": operations.get(
            "pause_resume_override_operations_available"
        )
        is True
        and isinstance(operations.get("override_actions_count"), int)
        and operations.get("override_actions_count") >= 0,
        "canary_and_rollback_lifecycle_tested": operations.get("canary_and_rollback_lifecycle_tested")
        is True
        and isinstance(operations.get("lifecycle_test_run_id"), str)
        and operations.get("lifecycle_test_run_id").strip() != "",
        "rollout_actions_integrated_with_observability_signals": health.get(
            "rollout_actions_integrated_with_observability_signals"
        )
        is True
        and isinstance(health.get("observability_signal_ids"), list)
        and len(health.get("observability_signal_ids")) > 0,
    }


def evaluate_plugin_rollout_gate(
    *,
    run_id: str,
    mode: str,
    controller: dict[str, Any],
    health: dict[str, Any],
    operations: dict[str, Any],
) -> dict[str, Any]:
    checks = summarize_plugin_rollout_health(
        controller=controller, health=health, operations=operations
    )
    failed_gates = [name for name, passed in checks.items() if passed is not True]
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": PLUGIN_ROLLOUT_SCHEMA,
        "schema_version": PLUGIN_ROLLOUT_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "release_blocked": status == "fail",
        "checks": checks,
        "failed_gates": failed_gates,
        "plugin_rollout_contract": build_plugin_rollout_contract(),
        "evidence": {
            "controller_ref": "data/plugin_rollout/controller_state.json",
            "health_ref": "data/plugin_rollout/health_signals.json",
            "operations_ref": "data/plugin_rollout/operations_state.json",
            "history_ref": "data/plugin_rollout/trend_history.jsonl",
        },
    }


def update_plugin_rollout_history(
    *, existing: list[dict[str, Any]], report: dict[str, Any]
) -> list[dict[str, Any]]:
    row = {
        "run_id": report["run_id"],
        "status": report["status"],
        "failed_gate_count": len(report["failed_gates"]),
    }
    return [*existing, row]

