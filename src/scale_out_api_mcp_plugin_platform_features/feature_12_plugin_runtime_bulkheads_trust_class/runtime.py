"""Runtime for feature 12 plugin/runtime bulkheads by trust class."""

from __future__ import annotations

from typing import Any

from .contracts import BULKHEADS_SCHEMA, BULKHEADS_SCHEMA_VERSION


def build_trust_bulkhead_contract() -> dict[str, object]:
    return {
        "trust_classes": ["trusted", "sandboxed", "untrusted"],
        "routing_policy": "dispatch_by_trust_class",
        "pool_isolation": True,
        "class_resource_quotas": True,
        "cross_class_guardrails": True,
        "reclassification_policy": True,
    }


def _trust_class_telemetry_aligned(policy: dict[str, Any], telemetry: dict[str, Any]) -> bool:
    trust_classes = policy.get("trust_classes")
    class_event_counts = telemetry.get("class_event_counts")
    if not isinstance(trust_classes, list) or not trust_classes:
        return False
    normalized_classes: list[str] = []
    for trust_class in trust_classes:
        if not isinstance(trust_class, str) or not trust_class.strip():
            return False
        normalized_classes.append(trust_class)
    if not isinstance(class_event_counts, dict):
        return False
    if set(class_event_counts.keys()) != set(normalized_classes):
        return False
    return all(isinstance(value, int) and value >= 0 for value in class_event_counts.values())


def _valid_dispatch_event(event: Any) -> bool:
    if not isinstance(event, dict):
        return False
    required = ("event_id", "plugin_id", "trust_class", "pool_id", "resource_units")
    if not all(key in event for key in required):
        return False
    if event.get("trust_class") not in {"trusted", "sandboxed", "untrusted"}:
        return False
    if not isinstance(event.get("event_id"), str) or not event["event_id"].strip():
        return False
    if not isinstance(event.get("plugin_id"), str) or not event["plugin_id"].strip():
        return False
    if not isinstance(event.get("pool_id"), str) or not event["pool_id"].strip():
        return False
    return isinstance(event.get("resource_units"), int) and event["resource_units"] > 0


def _collect_dispatch_events(runtime_state: dict[str, Any]) -> list[dict[str, Any]]:
    rows = runtime_state.get("dispatch_events")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if _valid_dispatch_event(row)]


def _evaluate_dispatch_event(
    *,
    event: dict[str, Any],
    usage: dict[str, int],
    quotas: dict[str, Any],
) -> tuple[list[str], list[str], list[str]]:
    leakage_events: list[str] = []
    quota_breaches: list[str] = []
    pool_violations: list[str] = []
    trust_class = event["trust_class"]
    usage.setdefault(trust_class, 0)
    usage[trust_class] += int(event["resource_units"])
    pool_id = event["pool_id"]
    if not pool_id.startswith(f"{trust_class}-"):
        pool_violations.append(event["event_id"])
    max_units = quotas.get(trust_class)
    if isinstance(max_units, int) and usage[trust_class] > max_units:
        quota_breaches.append(trust_class)
    target_class = event.get("target_class")
    if isinstance(target_class, str) and target_class.strip() and target_class != trust_class:
        leakage_events.append(event["event_id"])
    return leakage_events, quota_breaches, pool_violations


def _reclassification_safe(runtime_state: dict[str, Any]) -> tuple[int, bool]:
    reclassifications = runtime_state.get("reclassifications")
    if not isinstance(reclassifications, list):
        return 0, False
    reclass_safe = True
    for row in reclassifications:
        if not isinstance(row, dict):
            reclass_safe = False
            continue
        if row.get("approved") is not True or not isinstance(row.get("ticket"), str):
            reclass_safe = False
    return len(reclassifications), reclass_safe


def execute_trust_bulkhead_runtime(
    *, policy: dict[str, Any], runtime_state: dict[str, Any], telemetry: dict[str, Any]
) -> dict[str, Any]:
    events = _collect_dispatch_events(runtime_state)
    trust_classes = policy.get("trust_classes")
    if not isinstance(trust_classes, list):
        trust_classes = []
    quotas = policy.get("class_quotas")
    if not isinstance(quotas, dict):
        quotas = {}
    usage = {cls: 0 for cls in trust_classes if isinstance(cls, str)}
    leakage_events: list[str] = []
    quota_breaches: list[str] = []
    pool_violations: list[str] = []
    for event in events:
        leak, breach, pool = _evaluate_dispatch_event(
            event=event,
            usage=usage,
            quotas=quotas,
        )
        leakage_events.extend(leak)
        quota_breaches.extend(breach)
        pool_violations.extend(pool)
    reclass_count, reclass_safe = _reclassification_safe(runtime_state)
    telemetry_counts = telemetry.get("class_event_counts")
    telemetry_consistent = isinstance(telemetry_counts, dict) and all(
        telemetry_counts.get(cls) == usage.get(cls, 0) for cls in usage
    )
    return {
        "events_processed": len(events),
        "usage_by_class": usage,
        "leakage_events": leakage_events,
        "quota_breaches": sorted(set(quota_breaches)),
        "pool_violations": pool_violations,
        "reclassifications_count": reclass_count,
        "reclassification_safe": reclass_safe,
        "telemetry_consistent": telemetry_consistent,
    }


def summarize_bulkhead_health(
    *, policy: dict[str, Any], runtime_state: dict[str, Any], telemetry: dict[str, Any]
) -> dict[str, bool]:
    execution = execute_trust_bulkhead_runtime(
        policy=policy, runtime_state=runtime_state, telemetry=telemetry
    )
    return {
        "trust_classes_defined_enforced": policy.get("trust_classes_defined_enforced") is True
        and execution["events_processed"] > 0,
        "execution_pools_segmented": runtime_state.get("execution_pools_segmented") is True
        and len(execution["pool_violations"]) == 0,
        "class_quotas_isolation_enforced": runtime_state.get("class_quotas_isolation_enforced") is True
        and len(execution["quota_breaches"]) == 0,
        "cross_class_leakage_blocked": runtime_state.get("cross_class_leakage_blocked") is True
        and len(execution["leakage_events"]) == 0,
        "boundary_policy_audit_controls": policy.get("boundary_policy_audit_controls") is True,
        "boundary_containment_tests_present": runtime_state.get("boundary_containment_tests_present") is True,
        "trust_reclassification_safe": policy.get("trust_reclassification_safe") is True
        and execution["reclassification_safe"] is True,
        "trust_class_telemetry_present": telemetry.get("trust_class_telemetry_present") is True
        and _trust_class_telemetry_aligned(policy, telemetry)
        and execution["telemetry_consistent"] is True,
    }


def evaluate_bulkheads_gate(
    *,
    run_id: str,
    mode: str,
    policy: dict[str, Any],
    runtime_state: dict[str, Any],
    telemetry: dict[str, Any],
) -> dict[str, Any]:
    execution = execute_trust_bulkhead_runtime(
        policy=policy, runtime_state=runtime_state, telemetry=telemetry
    )
    checks = summarize_bulkhead_health(policy=policy, runtime_state=runtime_state, telemetry=telemetry)
    failed_gates = [name for name, passed in checks.items() if passed is not True]
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": BULKHEADS_SCHEMA,
        "schema_version": BULKHEADS_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "release_blocked": status == "fail",
        "checks": checks,
        "execution": execution,
        "failed_gates": failed_gates,
        "bulkhead_contract": build_trust_bulkhead_contract(),
        "evidence": {
            "policy_ref": "data/trust_bulkheads/policy.json",
            "runtime_ref": "data/trust_bulkheads/runtime_state.json",
            "telemetry_ref": "data/trust_bulkheads/telemetry.json",
            "history_ref": "data/trust_bulkheads/trend_history.jsonl",
            "events_ref": "data/trust_bulkheads/bulkhead_events.jsonl",
        },
    }


def update_bulkheads_history(*, existing: list[dict[str, Any]], report: dict[str, Any]) -> list[dict[str, Any]]:
    execution = report.get("execution")
    row = {
        "run_id": report["run_id"],
        "status": report["status"],
        "failed_gate_count": len(report["failed_gates"]),
        "events_processed": execution.get("events_processed") if isinstance(execution, dict) else None,
    }
    return [*existing, row]


def build_bulkhead_event_rows(*, report: dict[str, Any]) -> list[dict[str, Any]]:
    execution = report.get("execution")
    if not isinstance(execution, dict):
        return []
    usage = execution.get("usage_by_class")
    if not isinstance(usage, dict):
        return []
    rows: list[dict[str, Any]] = []
    for trust_class in ("trusted", "sandboxed", "untrusted"):
        rows.append(
            {
                "run_id": report.get("run_id"),
                "trust_class": trust_class,
                "resource_units": usage.get(trust_class, 0),
            }
        )
    return rows

