"""Runtime for feature 08 distributed queue fairness gate."""

from __future__ import annotations

from typing import Any

from .contracts import WEIGHTED_QUEUE_FAIRNESS_SCHEMA, WEIGHTED_QUEUE_FAIRNESS_SCHEMA_VERSION


def build_weighted_queue_fairness_contract() -> dict[str, object]:
    return {
        "distributed_weighted_fair_queue_delivered": True,
        "tenant_plugin_priority_weighting_supported": True,
        "starvation_prevention_aging_policy": True,
        "scheduler_state_persistence_replay": True,
        "fairness_wait_time_telemetry_published": True,
        "safe_admin_weight_tuning_controls": True,
        "mixed_load_stress_validation": True,
        "deterministic_scheduler_tests": True,
    }


def _valid_weight_map(value: Any) -> bool:
    if not isinstance(value, dict) or not value:
        return False
    for key, weight in value.items():
        if not isinstance(key, str) or not key.strip():
            return False
        if not isinstance(weight, int) or weight <= 0:
            return False
    return True


def _valid_fairness_score(value: Any) -> bool:
    return isinstance(value, (int, float)) and 0.0 <= float(value) <= 1.0


def _valid_wait_map(value: Any) -> bool:
    if not isinstance(value, dict) or not value:
        return False
    for key, wait_ms in value.items():
        if not isinstance(key, str) or not key.strip():
            return False
        if not isinstance(wait_ms, int) or wait_ms < 0:
            return False
    return True


def _coherent_replay_state(scheduler: dict[str, Any]) -> bool:
    replay_applied = scheduler.get("replay_applied_decisions")
    decisions_total = scheduler.get("decision_log_entries")
    return (
        isinstance(replay_applied, int)
        and replay_applied >= 0
        and isinstance(decisions_total, int)
        and decisions_total >= replay_applied
    )


def _wait_keys_align(scheduler: dict[str, Any], telemetry: dict[str, Any]) -> bool:
    tenant_weights = scheduler.get("tenant_weights")
    wait_map = telemetry.get("class_wait_p95_ms")
    if not isinstance(tenant_weights, dict) or not isinstance(wait_map, dict):
        return False
    return set(tenant_weights.keys()) == set(wait_map.keys())


def _p95_coherent_with_class_waits(telemetry: dict[str, Any]) -> bool:
    p95_wait_ms = telemetry.get("p95_wait_ms")
    wait_map = telemetry.get("class_wait_p95_ms")
    if not isinstance(p95_wait_ms, int) or not isinstance(wait_map, dict) or not wait_map:
        return False
    max_class_wait = max(wait_map.values())
    return isinstance(max_class_wait, int) and p95_wait_ms >= max_class_wait


def _valid_dispatch_event(event: Any) -> bool:
    if not isinstance(event, dict):
        return False
    required = ("event_id", "tenant", "plugin", "status", "wait_ms")
    if not all(key in event for key in required):
        return False
    if event.get("status") not in {"scheduled", "deferred", "dropped"}:
        return False
    if not isinstance(event.get("wait_ms"), int) or event.get("wait_ms") < 0:
        return False
    return isinstance(event.get("tenant"), str) and isinstance(event.get("plugin"), str)


def _collect_dispatch_events(scheduler: dict[str, Any]) -> list[dict[str, Any]]:
    events = scheduler.get("dispatch_events")
    if not isinstance(events, list):
        return []
    return [event for event in events if _valid_dispatch_event(event)]


def _evaluate_dispatch_event(
    *,
    event: dict[str, Any],
    tenant_weights: Any,
    plugin_weights: Any,
    dropped_by_tenant: dict[str, int],
) -> tuple[bool, bool]:
    tenant = event["tenant"]
    plugin = event["plugin"]
    dropped_by_tenant[tenant] = dropped_by_tenant.get(tenant, 0) + (1 if event["status"] == "dropped" else 0)
    tenant_weight = tenant_weights.get(tenant) if isinstance(tenant_weights, dict) else None
    plugin_weight = plugin_weights.get(plugin) if isinstance(plugin_weights, dict) else None
    if not isinstance(tenant_weight, int) or not isinstance(plugin_weight, int):
        return True, False
    if event["status"] == "scheduled" and event["wait_ms"] > (200 // max(tenant_weight, 1)):
        return False, True
    return False, False


def _drop_share(dropped_by_tenant: dict[str, int]) -> float:
    total_dropped = sum(dropped_by_tenant.values())
    if total_dropped < 5:
        return 0.0
    return max(dropped_by_tenant.values()) / total_dropped


def execute_weighted_scheduler_runtime(*, scheduler: dict[str, Any], telemetry: dict[str, Any]) -> dict[str, Any]:
    tenant_weights = scheduler.get("tenant_weights")
    plugin_weights = scheduler.get("plugin_weights")
    events = _collect_dispatch_events(scheduler)
    starvation_violations: list[str] = []
    weighting_violations: list[str] = []
    dropped_by_tenant: dict[str, int] = {}
    for event in events:
        has_weighting_violation, has_starvation_violation = _evaluate_dispatch_event(
            event=event,
            tenant_weights=tenant_weights,
            plugin_weights=plugin_weights,
            dropped_by_tenant=dropped_by_tenant,
        )
        if has_weighting_violation:
            weighting_violations.append(event["event_id"])
        if has_starvation_violation:
            starvation_violations.append(event["event_id"])
    fairness_score = telemetry.get("fairness_score")
    replay_hash = scheduler.get("replay_hash")
    telemetry_hash = telemetry.get("deterministic_trace_hash")
    deterministic_replay_ok = (
        isinstance(replay_hash, str)
        and replay_hash.strip() != ""
        and isinstance(telemetry_hash, str)
        and replay_hash == telemetry_hash
    )
    max_tenant_drop_share = _drop_share(dropped_by_tenant) if events else 0.0
    return {
        "events_processed": len(events),
        "starvation_violations": starvation_violations,
        "weighting_violations": weighting_violations,
        "max_tenant_drop_share": max_tenant_drop_share,
        "deterministic_replay_ok": deterministic_replay_ok,
        "fairness_score_ok": _valid_fairness_score(fairness_score) and float(fairness_score) >= 0.9,
    }


def summarize_weighted_queue_fairness_health(
    *, scheduler: dict[str, Any], telemetry: dict[str, Any], policy: dict[str, Any]
) -> dict[str, bool]:
    execution = execute_weighted_scheduler_runtime(scheduler=scheduler, telemetry=telemetry)
    fairness_score = telemetry.get("fairness_score")
    p95_wait_ms = telemetry.get("p95_wait_ms")
    admin_range = policy.get("admin_tuning_range")
    return {
        "distributed_weighted_fair_queue_delivered": isinstance(
            scheduler.get("queue_backend"), str
        )
        and scheduler.get("queue_backend") in {"redis", "postgres", "memory_sim"},
        "tenant_plugin_priority_weighting_supported": _valid_weight_map(
            scheduler.get("tenant_weights")
        )
        and _valid_weight_map(scheduler.get("plugin_weights")),
        "starvation_prevention_aging_policy": policy.get("starvation_prevention_aging_policy") is True,
        "scheduler_state_persistence_replay": isinstance(
            scheduler.get("scheduler_state_version"), int
        )
        and scheduler.get("scheduler_state_version") > 0
        and isinstance(scheduler.get("replay_cursor"), str)
        and scheduler.get("replay_cursor").strip() != "",
        "scheduler_replay_consistency": _coherent_replay_state(scheduler),
        "fairness_wait_time_telemetry_published": _valid_fairness_score(fairness_score)
        and isinstance(p95_wait_ms, int)
        and p95_wait_ms >= 0
        and _valid_wait_map(telemetry.get("class_wait_p95_ms"))
        and _wait_keys_align(scheduler, telemetry)
        and _p95_coherent_with_class_waits(telemetry),
        "safe_admin_weight_tuning_controls": isinstance(admin_range, dict)
        and isinstance(admin_range.get("min"), int)
        and isinstance(admin_range.get("max"), int)
        and admin_range.get("min") > 0
        and admin_range.get("max") >= admin_range.get("min")
        and policy.get("safe_admin_weight_tuning_controls") is True
        and isinstance(policy.get("last_admin_change_ticket"), str)
        and policy.get("last_admin_change_ticket").startswith("CAB-"),
        "mixed_load_stress_validation": telemetry.get("mixed_load_stress_validation") is True
        and isinstance(telemetry.get("mixed_load_samples"), int)
        and telemetry.get("mixed_load_samples") > 0,
        "deterministic_scheduler_tests": policy.get("deterministic_scheduler_tests") is True
        and isinstance(policy.get("deterministic_trace_hash"), str)
        and policy.get("deterministic_trace_hash").strip() != "",
        "runtime_weighted_scheduling_enforced": len(execution["weighting_violations"]) == 0,
        "runtime_starvation_prevented": len(execution["starvation_violations"]) == 0,
        "runtime_drop_fairness_enforced": execution["max_tenant_drop_share"] <= 0.7,
        "runtime_deterministic_replay_verified": execution["deterministic_replay_ok"] is True,
        "runtime_fairness_score_enforced": execution["fairness_score_ok"] is True,
    }


def evaluate_weighted_queue_fairness_gate(
    *,
    run_id: str,
    mode: str,
    scheduler: dict[str, Any],
    telemetry: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    execution = execute_weighted_scheduler_runtime(scheduler=scheduler, telemetry=telemetry)
    checks = summarize_weighted_queue_fairness_health(
        scheduler=scheduler, telemetry=telemetry, policy=policy
    )
    failed_gates = [name for name, passed in checks.items() if passed is not True]
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": WEIGHTED_QUEUE_FAIRNESS_SCHEMA,
        "schema_version": WEIGHTED_QUEUE_FAIRNESS_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "release_blocked": status == "fail",
        "checks": checks,
        "execution": execution,
        "failed_gates": failed_gates,
        "weighted_queue_fairness_contract": build_weighted_queue_fairness_contract(),
        "evidence": {
            "scheduler_ref": "data/weighted_queue_fairness/scheduler_state.json",
            "telemetry_ref": "data/weighted_queue_fairness/telemetry.json",
            "policy_ref": "data/weighted_queue_fairness/policy.json",
            "history_ref": "data/weighted_queue_fairness/trend_history.jsonl",
            "events_ref": "data/weighted_queue_fairness/scheduler_events.jsonl",
        },
    }


def update_weighted_queue_fairness_history(
    *, existing: list[dict[str, Any]], report: dict[str, Any]
) -> list[dict[str, Any]]:
    execution = report.get("execution")
    row = {
        "run_id": report["run_id"],
        "status": report["status"],
        "failed_gate_count": len(report["failed_gates"]),
        "events_processed": execution.get("events_processed") if isinstance(execution, dict) else None,
    }
    return [*existing, row]


def build_scheduler_event_rows(*, report: dict[str, Any]) -> list[dict[str, Any]]:
    execution = report.get("execution")
    if not isinstance(execution, dict):
        return []
    run_id = report.get("run_id")
    return [
        {"run_id": run_id, "signal": "events_processed", "value": execution.get("events_processed", 0)},
        {"run_id": run_id, "signal": "starvation_violations", "value": len(execution.get("starvation_violations", []))},
        {"run_id": run_id, "signal": "weighting_violations", "value": len(execution.get("weighting_violations", []))},
        {"run_id": run_id, "signal": "max_tenant_drop_share", "value": execution.get("max_tenant_drop_share", 0.0)},
    ]

