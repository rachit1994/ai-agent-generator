"""Runtime for feature 05 edge admission control."""

from __future__ import annotations

from typing import Any

from .contracts import EDGE_ADMISSION_SCHEMA, EDGE_ADMISSION_SCHEMA_VERSION


def build_edge_policy_contract() -> dict[str, object]:
    return {
        "status_code": 429,
        "retry_after_header": "seconds",
        "scope_keys": ["tenant_id", "user_id", "api_key", "route"],
        "budget_types": ["burst", "sustained"],
        "outage_policy": "fail_closed",
    }


def _valid_scope_keys(value: Any) -> bool:
    expected = {"tenant_id", "user_id", "api_key", "route"}
    return isinstance(value, list) and set(value) == expected


def _valid_budgets(policy: dict[str, Any]) -> bool:
    burst = policy.get("burst_limit_per_minute")
    sustained = policy.get("sustained_limit_per_hour")
    return (
        isinstance(burst, int)
        and isinstance(sustained, int)
        and burst > 0
        and sustained >= burst
    )


def _valid_counters(counters: dict[str, Any]) -> bool:
    deny = counters.get("deny_count")
    throttle = counters.get("throttle_count")
    sampled = counters.get("sampled_requests")
    return (
        isinstance(deny, int)
        and deny >= 0
        and isinstance(throttle, int)
        and throttle >= 0
        and isinstance(sampled, int)
        and sampled >= (deny + throttle)
    )


def _valid_retry_after(policy: dict[str, Any], traffic_sample: dict[str, Any]) -> bool:
    retry_after_seconds = traffic_sample.get("retry_after_seconds")
    max_retry_after_seconds = policy.get("max_retry_after_seconds")
    return (
        isinstance(retry_after_seconds, int)
        and retry_after_seconds > 0
        and isinstance(max_retry_after_seconds, int)
        and max_retry_after_seconds > 0
        and retry_after_seconds <= max_retry_after_seconds
    )


def _valid_request_event(event: Any) -> bool:
    if not isinstance(event, dict):
        return False
    required = ("event_id", "tenant_id", "user_id", "api_key", "route", "decision", "retry_after_seconds")
    if not all(key in event for key in required):
        return False
    if event.get("decision") not in {"allow", "throttle", "deny"}:
        return False
    return isinstance(event.get("retry_after_seconds"), int) and event.get("retry_after_seconds") >= 0


def _collect_request_events(traffic_sample: dict[str, Any]) -> list[dict[str, Any]]:
    events = traffic_sample.get("request_events")
    if not isinstance(events, list):
        return []
    return [event for event in events if _valid_request_event(event)]


def _event_has_scopes(event: dict[str, Any]) -> bool:
    return all(isinstance(event.get(key), str) and event.get(key).strip() for key in ("tenant_id", "user_id", "api_key", "route"))


def _event_retry_after_valid(event: dict[str, Any], max_retry_after: Any) -> bool:
    decision = event["decision"]
    retry_after = event["retry_after_seconds"]
    if decision == "allow":
        return retry_after == 0
    if decision in {"throttle", "deny"}:
        return isinstance(max_retry_after, int) and retry_after > 0 and retry_after <= max_retry_after
    return False


def _event_decision_counts(event: dict[str, Any]) -> tuple[int, int]:
    decision = event["decision"]
    if decision == "deny":
        return (1, 0)
    if decision == "throttle":
        return (0, 1)
    return (0, 0)


def execute_edge_admission_runtime(
    *, policy: dict[str, Any], counters: dict[str, Any], traffic_sample: dict[str, Any]
) -> dict[str, Any]:
    events = _collect_request_events(traffic_sample)
    retry_after_violations: list[str] = []
    scope_violations: list[str] = []
    deny_count = 0
    throttle_count = 0
    max_retry_after = policy.get("max_retry_after_seconds")
    for event in events:
        if not _event_has_scopes(event):
            scope_violations.append(event["event_id"])
        if not _event_retry_after_valid(event, max_retry_after):
            retry_after_violations.append(event["event_id"])
        deny_delta, throttle_delta = _event_decision_counts(event)
        deny_count += deny_delta
        throttle_count += throttle_delta
    counter_coherent = (
        isinstance(counters.get("deny_count"), int)
        and isinstance(counters.get("throttle_count"), int)
        and counters.get("deny_count") == deny_count
        and counters.get("throttle_count") == throttle_count
    )
    return {
        "events_processed": len(events),
        "retry_after_violations": retry_after_violations,
        "scope_violations": scope_violations,
        "counter_coherent": counter_coherent,
    }


def summarize_edge_admission(
    *, policy: dict[str, Any], counters: dict[str, Any], traffic_sample: dict[str, Any]
) -> dict[str, bool]:
    execution = execute_edge_admission_runtime(policy=policy, counters=counters, traffic_sample=traffic_sample)
    return {
        "edge_middleware_present": policy.get("edge_middleware_present") is True,
        "scoped_limits_present": policy.get("scoped_limits_present") is True
        and _valid_scope_keys(policy.get("scope_keys")),
        "retry_after_compliant": traffic_sample.get("retry_after_compliant") is True
        and _valid_retry_after(policy, traffic_sample),
        "burst_sustained_budgets": policy.get("burst_sustained_budgets") is True
        and _valid_budgets(policy),
        "deny_throttle_metrics": counters.get("deny_throttle_metrics") is True
        and _valid_counters(counters),
        "outage_policy_defined": policy.get("outage_policy_defined") is True
        and policy.get("outage_mode") in {"fail_closed", "fail_open"},
        "integration_load_tests_present": traffic_sample.get("integration_load_tests_present") is True
        and isinstance(traffic_sample.get("load_test_profile"), str)
        and traffic_sample.get("load_test_profile").strip() != "",
        "dynamic_policy_updates_safe": policy.get("dynamic_policy_updates_safe") is True
        and isinstance(policy.get("policy_version"), str)
        and policy.get("policy_version").strip() != "",
        "runtime_retry_after_consistent": len(execution["retry_after_violations"]) == 0,
        "runtime_scope_keys_consistent": len(execution["scope_violations"]) == 0,
        "runtime_decision_counters_coherent": execution["counter_coherent"] is True,
    }


def evaluate_edge_admission_gate(
    *,
    run_id: str,
    mode: str,
    policy: dict[str, Any],
    counters: dict[str, Any],
    traffic_sample: dict[str, Any],
) -> dict[str, Any]:
    execution = execute_edge_admission_runtime(policy=policy, counters=counters, traffic_sample=traffic_sample)
    checks = summarize_edge_admission(policy=policy, counters=counters, traffic_sample=traffic_sample)
    failed_gates = [name for name, passed in checks.items() if passed is not True]
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": EDGE_ADMISSION_SCHEMA,
        "schema_version": EDGE_ADMISSION_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "release_blocked": status == "fail",
        "checks": checks,
        "execution": execution,
        "failed_gates": failed_gates,
        "policy_contract": build_edge_policy_contract(),
        "evidence": {
            "policy_ref": "data/edge_admission/policy.json",
            "counters_ref": "data/edge_admission/counters.json",
            "traffic_ref": "data/edge_admission/traffic_sample.json",
            "history_ref": "data/edge_admission/trend_history.jsonl",
            "events_ref": "data/edge_admission/admission_events.jsonl",
        },
    }


def update_edge_admission_history(*, existing: list[dict[str, Any]], report: dict[str, Any]) -> list[dict[str, Any]]:
    execution = report.get("execution")
    row = {
        "run_id": report["run_id"],
        "status": report["status"],
        "failed_gate_count": len(report["failed_gates"]),
        "events_processed": execution.get("events_processed") if isinstance(execution, dict) else None,
    }
    return [*existing, row]


def build_admission_event_rows(*, report: dict[str, Any]) -> list[dict[str, Any]]:
    execution = report.get("execution")
    if not isinstance(execution, dict):
        return []
    run_id = report.get("run_id")
    return [
        {"run_id": run_id, "signal": "events_processed", "value": execution.get("events_processed", 0)},
        {"run_id": run_id, "signal": "retry_after_violations", "value": len(execution.get("retry_after_violations", []))},
        {"run_id": run_id, "signal": "scope_violations", "value": len(execution.get("scope_violations", []))},
    ]

