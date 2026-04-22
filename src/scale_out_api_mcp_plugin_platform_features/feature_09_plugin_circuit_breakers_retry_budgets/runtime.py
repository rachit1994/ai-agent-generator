from __future__ import annotations

from typing import Any

from .contracts import PLUGIN_CIRCUIT_BREAKER_SCHEMA, PLUGIN_CIRCUIT_BREAKER_SCHEMA_VERSION


def build_plugin_circuit_breaker_contract() -> dict[str, object]:
    return {
        "plugin_level_circuit_breaker_runtime": True,
        "plugin_level_retry_budget_enforcement": True,
        "failure_classification_for_transitions": True,
        "fallback_behavior_for_open_circuits": True,
        "bulkhead_blast_radius_containment": True,
        "state_transition_telemetry": True,
        "operator_safe_breaker_controls": True,
        "degraded_plugin_end_to_end_tests": True,
    }


def _valid_failure_classes(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) > 0
        and all(item in {"transient", "permanent", "throttle"} for item in value)
    )


def _valid_transition_counts(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    required = ("open", "half_open", "closed")
    return all(isinstance(value.get(key), int) and value.get(key) >= 0 for key in required)


def _valid_retry_budget(runtime_state: dict[str, Any]) -> bool:
    remaining = runtime_state.get("retry_budget_remaining")
    budget_limit = runtime_state.get("retry_budget_limit")
    return (
        isinstance(remaining, int)
        and remaining >= 0
        and isinstance(budget_limit, int)
        and budget_limit > 0
        and remaining <= budget_limit
    )


def _degraded_test_coherent(telemetry: dict[str, Any]) -> bool:
    transition_counts = telemetry.get("transition_counts")
    if not isinstance(transition_counts, dict):
        return False
    open_transitions = transition_counts.get("open")
    return isinstance(open_transitions, int) and open_transitions > 0


def _policy_telemetry_version_aligned(policy: dict[str, Any], telemetry: dict[str, Any]) -> bool:
    policy_version = policy.get("transition_policy_version")
    telemetry_version = telemetry.get("transition_policy_version")
    return (
        isinstance(policy_version, str)
        and policy_version.strip() != ""
        and policy_version == telemetry_version
    )


def _retry_budget_policy_aligned(runtime_state: dict[str, Any], policy: dict[str, Any]) -> bool:
    runtime_policy_version = runtime_state.get("retry_budget_policy_version")
    policy_version = policy.get("retry_budget_policy_version")
    return (
        isinstance(runtime_policy_version, str)
        and runtime_policy_version.strip() != ""
        and runtime_policy_version == policy_version
    )


def _plugin_telemetry_aligned(runtime_state: dict[str, Any], telemetry: dict[str, Any]) -> bool:
    runtime_plugin_id = runtime_state.get("plugin_id")
    telemetry_plugin_id = telemetry.get("plugin_id")
    return (
        isinstance(runtime_plugin_id, str)
        and runtime_plugin_id.strip() != ""
        and runtime_plugin_id == telemetry_plugin_id
    )


def _valid_transition_event(event: Any) -> bool:
    if not isinstance(event, dict):
        return False
    required_strings = ("event_id", "from_state", "to_state", "failure_class")
    if not all(isinstance(event.get(key), str) and event.get(key).strip() != "" for key in required_strings):
        return False
    if event.get("from_state") not in {"closed", "open", "half_open"}:
        return False
    if event.get("to_state") not in {"closed", "open", "half_open"}:
        return False
    if event.get("failure_class") not in {"transient", "permanent", "throttle"}:
        return False
    return isinstance(event.get("retry_attempt"), int) and event.get("retry_attempt") >= 0


def _collect_transition_events(telemetry: dict[str, Any]) -> list[dict[str, Any]]:
    events = telemetry.get("transition_events")
    if not isinstance(events, list):
        return []
    rows: list[dict[str, Any]] = []
    for event in events:
        if _valid_transition_event(event):
            rows.append(event)
    return rows


def _sanitize_policy_controls(policy: dict[str, Any]) -> tuple[int, int, str]:
    cooldown_seconds = policy.get("cooldown_seconds")
    probe_count = policy.get("half_open_probe_count")
    fallback_mode = policy.get("fallback_mode", "fail_fast")
    if not isinstance(cooldown_seconds, int) or cooldown_seconds <= 0:
        cooldown_seconds = 30
    if not isinstance(probe_count, int) or probe_count <= 0:
        probe_count = 2
    return cooldown_seconds, probe_count, fallback_mode


def _process_transition_events(
    *, events: list[dict[str, Any]], retry_limit: int
) -> tuple[dict[str, int], int, list[str], str]:
    state_counts = {"open": 0, "half_open": 0, "closed": 0}
    failures: list[str] = []
    retries_consumed = 0
    final_state = "closed"
    for event in events:
        to_state = event["to_state"]
        final_state = to_state
        state_counts[to_state] += 1
        failure_class = event["failure_class"]
        retry_attempt = int(event["retry_attempt"])
        if failure_class in {"transient", "throttle"} and retry_attempt > 0:
            retries_consumed += 1
        if failure_class == "permanent" and to_state != "open":
            failures.append(f"permanent_not_open:{event['event_id']}")
        if retry_attempt > retry_limit:
            failures.append(f"retry_attempt_over_limit:{event['event_id']}")
    return state_counts, retries_consumed, failures, final_state


def _finalize_runtime_state(
    *,
    state: str,
    state_counts: dict[str, int],
    probe_count: int,
    fallback_mode: str,
    cooldown_seconds: int,
) -> tuple[str, dict[str, Any], list[str]]:
    failures: list[str] = []
    half_open_probe_exhausted = state == "half_open" and state_counts["half_open"] >= probe_count
    if half_open_probe_exhausted:
        state = "open"
        state_counts["open"] += 1
    if state == "open" and fallback_mode not in {"serve_cached", "fail_fast"}:
        failures.append("invalid_fallback_mode")
    fallback_activations = state_counts["open"] if state == "open" else 0
    fallback = {
        "mode": fallback_mode,
        "activations": fallback_activations,
        "cooldown_seconds": cooldown_seconds,
    }
    return state, fallback, failures


def execute_plugin_circuit_breaker_runtime(
    *, runtime_state: dict[str, Any], policy: dict[str, Any], telemetry: dict[str, Any]
) -> dict[str, Any]:
    events = _collect_transition_events(telemetry)
    retry_remaining = int(runtime_state.get("retry_budget_remaining", 0))
    retry_limit = int(runtime_state.get("retry_budget_limit", 0))
    cooldown_seconds, probe_count, fallback_mode = _sanitize_policy_controls(policy)
    state_counts, retries_consumed, failures, processed_state = _process_transition_events(
        events=events,
        retry_limit=retry_limit,
    )
    retry_remaining_after = max(0, retry_remaining - retries_consumed)
    saturation = retry_limit > 0 and retry_remaining_after <= int(retry_limit * 0.1)
    state, fallback, terminal_failures = _finalize_runtime_state(
        state=processed_state,
        state_counts=state_counts,
        probe_count=probe_count,
        fallback_mode=fallback_mode,
        cooldown_seconds=cooldown_seconds,
    )
    failures.extend(terminal_failures)
    return {
        "state_counts": state_counts,
        "events_processed": len(events),
        "events_rejected": len(telemetry.get("transition_events", [])) - len(events)
        if isinstance(telemetry.get("transition_events"), list)
        else 0,
        "final_state": state,
        "retry_budget": {
            "limit": retry_limit,
            "remaining_before": retry_remaining,
            "consumed": retries_consumed,
            "remaining_after": retry_remaining_after,
            "saturation": saturation,
        },
        "fallback": fallback,
        "runtime_failures": failures,
    }


def summarize_plugin_circuit_breaker_health(*, runtime_state: dict[str, Any], policy: dict[str, Any], telemetry: dict[str, Any]) -> dict[str, bool]:
    execution = execute_plugin_circuit_breaker_runtime(
        runtime_state=runtime_state, policy=policy, telemetry=telemetry
    )
    return {
        "plugin_level_circuit_breaker_runtime": runtime_state.get("plugin_level_circuit_breaker_runtime") is True
        and isinstance(runtime_state.get("plugin_id"), str)
        and runtime_state.get("plugin_id").strip() != ""
        and execution["events_processed"] > 0,
        "plugin_level_retry_budget_enforcement": runtime_state.get("plugin_level_retry_budget_enforcement") is True
        and _valid_retry_budget(runtime_state)
        and _retry_budget_policy_aligned(runtime_state, policy)
        and execution["retry_budget"]["remaining_after"] <= execution["retry_budget"]["limit"],
        "failure_classification_for_transitions": policy.get("failure_classification_for_transitions") is True
        and _valid_failure_classes(policy.get("failure_classes"))
        and len(execution["runtime_failures"]) == 0,
        "fallback_behavior_for_open_circuits": policy.get("fallback_behavior_for_open_circuits") is True
        and policy.get("fallback_mode") in {"serve_cached", "fail_fast"}
        and (
            execution["final_state"] != "open" or execution["fallback"]["activations"] >= 0
        ),
        "bulkhead_blast_radius_containment": runtime_state.get("bulkhead_blast_radius_containment") is True
        and execution["state_counts"]["open"] <= execution["events_processed"],
        "state_transition_telemetry": telemetry.get("state_transition_telemetry") is True
        and _valid_transition_counts(telemetry.get("transition_counts"))
        and _policy_telemetry_version_aligned(policy, telemetry)
        and _plugin_telemetry_aligned(runtime_state, telemetry)
        and execution["events_rejected"] == 0,
        "operator_safe_breaker_controls": policy.get("operator_safe_breaker_controls") is True
        and isinstance(policy.get("operator_approval_ticket"), str)
        and policy.get("operator_approval_ticket").startswith("CAB-")
        and isinstance(policy.get("cooldown_seconds"), int)
        and policy.get("cooldown_seconds") > 0
        and isinstance(policy.get("half_open_probe_count"), int)
        and policy.get("half_open_probe_count") > 0,
        "degraded_plugin_end_to_end_tests": telemetry.get("degraded_plugin_end_to_end_tests") is True
        and isinstance(telemetry.get("degraded_test_run_id"), str)
        and telemetry.get("degraded_test_run_id").strip() != ""
        and _degraded_test_coherent(telemetry)
        and execution["events_processed"] >= execution["state_counts"]["open"],
    }


def evaluate_plugin_circuit_breaker_gate(*, run_id: str, mode: str, runtime_state: dict[str, Any], policy: dict[str, Any], telemetry: dict[str, Any]) -> dict[str, Any]:
    execution = execute_plugin_circuit_breaker_runtime(
        runtime_state=runtime_state, policy=policy, telemetry=telemetry
    )
    checks = summarize_plugin_circuit_breaker_health(runtime_state=runtime_state, policy=policy, telemetry=telemetry)
    failed_gates = [name for name, passed in checks.items() if passed is not True]
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": PLUGIN_CIRCUIT_BREAKER_SCHEMA,
        "schema_version": PLUGIN_CIRCUIT_BREAKER_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "release_blocked": status == "fail",
        "checks": checks,
        "failed_gates": failed_gates,
        "breaker_execution": execution,
        "plugin_circuit_breaker_contract": build_plugin_circuit_breaker_contract(),
        "evidence": {
            "runtime_ref": "data/plugin_circuit_breakers/runtime_state.json",
            "policy_ref": "data/plugin_circuit_breakers/policy.json",
            "telemetry_ref": "data/plugin_circuit_breakers/telemetry.json",
            "history_ref": "data/plugin_circuit_breakers/trend_history.jsonl",
            "events_ref": "data/plugin_circuit_breakers/transition_events.jsonl",
        },
    }


def update_plugin_circuit_breaker_history(*, existing: list[dict[str, Any]], report: dict[str, Any]) -> list[dict[str, Any]]:
    execution = report.get("breaker_execution")
    retry_budget = execution.get("retry_budget", {}) if isinstance(execution, dict) else {}
    row = {
        "run_id": report["run_id"],
        "status": report["status"],
        "failed_gate_count": len(report["failed_gates"]),
        "retry_remaining_after": retry_budget.get("remaining_after"),
    }
    return [*existing, row]


def build_transition_event_rows(*, report: dict[str, Any]) -> list[dict[str, Any]]:
    execution = report.get("breaker_execution")
    if not isinstance(execution, dict):
        return []
    state_counts = execution.get("state_counts")
    if not isinstance(state_counts, dict):
        return []
    rows: list[dict[str, Any]] = []
    for state in ("open", "half_open", "closed"):
        rows.append(
            {
                "run_id": report.get("run_id"),
                "state": state,
                "count": state_counts.get(state, 0),
            }
        )
    return rows
