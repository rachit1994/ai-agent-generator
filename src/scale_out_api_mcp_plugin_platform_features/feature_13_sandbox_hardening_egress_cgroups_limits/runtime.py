"""Runtime for feature 13 sandbox hardening."""

from __future__ import annotations

from typing import Any

from .contracts import SANDBOX_HARDENING_SCHEMA, SANDBOX_HARDENING_SCHEMA_VERSION


def build_sandbox_policy_contract() -> dict[str, object]:
    return {
        "default_egress": "deny",
        "allowlist_enforced": True,
        "resource_limits": ["cpu", "memory", "pids", "fds"],
        "filesystem_isolation": True,
        "syscall_filtering": True,
        "timeout_kill_semantics": True,
        "escape_kill_switch": True,
        "startup_policy_validation": True,
        "deny_audit_schema": "sandbox.v1.deny_event",
        "policy_versioned_validated": True,
    }


def _has_positive_limit(runtime_state: dict[str, Any], key: str) -> bool:
    value = runtime_state.get(key)
    return isinstance(value, int) and value > 0


def _valid_deny_event(event: Any) -> tuple[bool, str, str]:
    if not isinstance(event, dict):
        return False, "", ""
    action = event.get("action")
    reason = event.get("reason")
    timestamp = event.get("timestamp")
    event_id = event.get("event_id")
    allowed_reasons = {
        "egress_allowlist_violation",
        "syscall_filtered",
        "filesystem_violation",
        "resource_limit_exceeded",
    }
    if not isinstance(action, str) or not action.strip():
        return False, "", ""
    if not isinstance(reason, str) or reason not in allowed_reasons:
        return False, "", ""
    if not isinstance(timestamp, str) or "T" not in timestamp or not timestamp.endswith("Z"):
        return False, "", ""
    if not isinstance(event_id, str) or not event_id.strip():
        return False, "", ""
    return True, timestamp, event_id


def _structured_deny_events(audit_logs: dict[str, Any]) -> bool:
    denied_events = audit_logs.get("denied_events")
    if not isinstance(denied_events, list) or not denied_events:
        return False
    previous_timestamp = ""
    seen_event_ids: set[str] = set()
    for event in denied_events:
        valid_event, timestamp, event_id = _valid_deny_event(event)
        if not valid_event:
            return False
        if previous_timestamp and timestamp < previous_timestamp:
            return False
        if event_id in seen_event_ids:
            return False
        seen_event_ids.add(event_id)
        previous_timestamp = timestamp
    return True


def _valid_semver(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parts = value.split(".")
    return len(parts) == 3 and all(part.isdigit() for part in parts)


def _valid_str_list(value: Any) -> bool:
    return isinstance(value, list) and len(value) > 0 and all(
        isinstance(item, str) and item.strip() for item in value
    )


def _valid_egress_allowlist(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    seen: set[str] = set()
    for host in value:
        if not isinstance(host, str):
            return False
        normalized = host.strip()
        if not normalized or "." not in normalized or " " in normalized:
            return False
        if normalized in seen:
            return False
        seen.add(normalized)
    return True


def _valid_mount_paths(value: Any) -> bool:
    if not _valid_str_list(value):
        return False
    return all(isinstance(path, str) and path.startswith("/") for path in value)


def _policy_version_applied(policy: dict[str, Any], runtime_state: dict[str, Any]) -> bool:
    policy_version = policy.get("policy_version")
    applied_policy_version = runtime_state.get("applied_policy_version")
    return (
        isinstance(policy_version, str)
        and policy_version.strip() != ""
        and isinstance(applied_policy_version, str)
        and applied_policy_version == policy_version
    )


def _timeout_within_policy(policy: dict[str, Any], runtime_state: dict[str, Any]) -> bool:
    timeout_ms = runtime_state.get("timeout_ms")
    max_timeout_ms = policy.get("max_timeout_ms")
    return (
        isinstance(timeout_ms, int)
        and timeout_ms > 0
        and isinstance(max_timeout_ms, int)
        and max_timeout_ms > 0
        and timeout_ms <= max_timeout_ms
    )


def _valid_runtime_event(event: Any) -> bool:
    if not isinstance(event, dict):
        return False
    required = ("event_id", "type", "status", "timestamp")
    if not all(isinstance(event.get(key), str) and event.get(key).strip() for key in required):
        return False
    if event["type"] not in {"egress_attempt", "resource_sample", "escape_probe", "timeout_enforcement"}:
        return False
    return event["status"] in {"allowed", "denied", "triggered", "ok"}


def _collect_runtime_events(runtime_state: dict[str, Any]) -> list[dict[str, Any]]:
    events = runtime_state.get("runtime_events")
    if not isinstance(events, list):
        return []
    return [event for event in events if _valid_runtime_event(event)]


def _egress_event_violation(event: dict[str, Any], allowed_hosts: set[str]) -> bool:
    host = event.get("host")
    if not isinstance(host, str):
        return True
    normalized_host = host.strip()
    if normalized_host in allowed_hosts:
        return event["status"] == "denied"
    return event["status"] != "denied"


def _resource_event_violation(event: dict[str, Any], runtime_state: dict[str, Any]) -> bool:
    cpu = event.get("cpu_millis")
    memory = event.get("memory_mb")
    if not isinstance(cpu, int) or not isinstance(memory, int):
        return True
    cpu_limit = int(runtime_state.get("cpu_limit_millis", 0))
    memory_limit = int(runtime_state.get("memory_limit_mb", 0))
    return cpu > cpu_limit or memory > memory_limit


def _record_runtime_violations(
    *, events: list[dict[str, Any]], allowed_hosts: set[str], runtime_state: dict[str, Any]
) -> tuple[list[str], list[str], list[str]]:
    egress_violations: list[str] = []
    resource_violations: list[str] = []
    escape_violations: list[str] = []
    for event in events:
        event_type = event["type"]
        if event_type == "egress_attempt" and _egress_event_violation(event, allowed_hosts):
            egress_violations.append(event["event_id"])
        elif event_type == "resource_sample" and _resource_event_violation(event, runtime_state):
            resource_violations.append(event["event_id"])
        elif event_type == "escape_probe" and event["status"] != "denied":
            escape_violations.append(event["event_id"])
    return egress_violations, resource_violations, escape_violations


def execute_sandbox_runtime(
    *, policy: dict[str, Any], runtime_state: dict[str, Any], audit_logs: dict[str, Any]
) -> dict[str, Any]:
    events = _collect_runtime_events(runtime_state)
    allowed_hosts = {
        host.strip()
        for host in policy.get("egress_allowlist", [])
        if isinstance(host, str) and host.strip()
    }
    egress_violations, resource_violations, escape_violations = _record_runtime_violations(
        events=events,
        allowed_hosts=allowed_hosts,
        runtime_state=runtime_state,
    )
    deny_count = audit_logs.get("denied_ops_count")
    deny_events = audit_logs.get("denied_events")
    deny_event_count = len(deny_events) if isinstance(deny_events, list) else 0
    return {
        "events_processed": len(events),
        "egress_violations": egress_violations,
        "resource_violations": resource_violations,
        "escape_violations": escape_violations,
        "audit_count_coherent": isinstance(deny_count, int) and deny_count == deny_event_count,
    }


def summarize_sandbox_hardening(
    *, policy: dict[str, Any], runtime_state: dict[str, Any], audit_logs: dict[str, Any]
) -> dict[str, bool]:
    execution = execute_sandbox_runtime(policy=policy, runtime_state=runtime_state, audit_logs=audit_logs)
    egress_allowlist = policy.get("egress_allowlist")
    valid_allowlist = _valid_egress_allowlist(egress_allowlist)
    return {
        "sandbox_isolation_runtime_present": runtime_state.get("sandbox_isolation_runtime_present") is True,
        "egress_allowlist_enforced": policy.get("default_egress") == "deny" and valid_allowlist,
        "cgroup_resource_limits_enforced": all(
            _has_positive_limit(runtime_state, key)
            for key in ("cpu_limit_millis", "memory_limit_mb", "pid_limit", "fd_limit")
        ),
        "filesystem_syscall_restricted": runtime_state.get("filesystem_syscall_restricted") is True,
        "timeouts_hard_kill_enforced": runtime_state.get("timeouts_hard_kill_enforced") is True
        and _timeout_within_policy(policy, runtime_state)
        and runtime_state.get("kill_signal") in {"SIGKILL", "SIGTERM"},
        "escape_detection_kill_switch_enforced": runtime_state.get("escape_detection_kill_switch_enforced")
        is True,
        "startup_policy_validation_enforced": policy.get("startup_policy_validation_enforced") is True,
        "denied_ops_logged": isinstance(audit_logs.get("denied_ops_count"), int)
        and audit_logs.get("denied_ops_count") > 0
        and isinstance(audit_logs.get("denied_events"), list)
        and audit_logs.get("denied_ops_count") == len(audit_logs.get("denied_events")),
        "deny_audit_events_structured": _structured_deny_events(audit_logs),
        "escape_exhaustion_tests_present": runtime_state.get("escape_exhaustion_tests_present") is True,
        "policy_versioned_validated": policy.get("policy_versioned_validated") is True
        and _valid_semver(policy.get("policy_version"))
        and _valid_str_list(policy.get("syscall_allowlist"))
        and _valid_mount_paths(policy.get("read_only_mounts"))
        and policy.get("syscall_default_action") == "deny"
        and _policy_version_applied(policy, runtime_state),
        "runtime_egress_isolation_enforced": len(execution["egress_violations"]) == 0,
        "runtime_resource_budget_enforced": len(execution["resource_violations"]) == 0,
        "runtime_escape_contained": len(execution["escape_violations"]) == 0,
        "audit_count_coherent": execution["audit_count_coherent"] is True,
    }


def evaluate_sandbox_hardening_gate(
    *,
    run_id: str,
    mode: str,
    policy: dict[str, Any],
    runtime_state: dict[str, Any],
    audit_logs: dict[str, Any],
) -> dict[str, Any]:
    execution = execute_sandbox_runtime(policy=policy, runtime_state=runtime_state, audit_logs=audit_logs)
    checks = summarize_sandbox_hardening(policy=policy, runtime_state=runtime_state, audit_logs=audit_logs)
    failed_gates = [name for name, passed in checks.items() if passed is not True]
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": SANDBOX_HARDENING_SCHEMA,
        "schema_version": SANDBOX_HARDENING_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "release_blocked": status == "fail",
        "checks": checks,
        "execution": execution,
        "failed_gates": failed_gates,
        "policy_contract": build_sandbox_policy_contract(),
        "evidence": {
            "policy_ref": "data/sandbox_hardening/policy.json",
            "runtime_ref": "data/sandbox_hardening/runtime_state.json",
            "audit_ref": "data/sandbox_hardening/audit_logs.json",
            "history_ref": "data/sandbox_hardening/trend_history.jsonl",
            "events_ref": "data/sandbox_hardening/runtime_events.jsonl",
        },
    }


def update_sandbox_hardening_history(
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


def build_runtime_event_rows(*, report: dict[str, Any]) -> list[dict[str, Any]]:
    execution = report.get("execution")
    if not isinstance(execution, dict):
        return []
    run_id = report.get("run_id")
    return [
        {"run_id": run_id, "signal": "events_processed", "value": execution.get("events_processed", 0)},
        {"run_id": run_id, "signal": "egress_violations", "value": len(execution.get("egress_violations", []))},
        {"run_id": run_id, "signal": "resource_violations", "value": len(execution.get("resource_violations", []))},
        {"run_id": run_id, "signal": "escape_violations", "value": len(execution.get("escape_violations", []))},
    ]

