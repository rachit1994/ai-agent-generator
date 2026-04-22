"""Runtime for feature 18 cross-tenant isolation."""

from __future__ import annotations

from typing import Any

from .contracts import CROSS_TENANT_SCHEMA, CROSS_TENANT_SCHEMA_VERSION


def build_cross_tenant_contract() -> dict[str, object]:
    return {
        "tenant_identity_required": True,
        "runtime_queue_storage_isolated": True,
        "cache_artifact_reuse_blocked": True,
        "tenant_keys_policy_controls": True,
        "tenant_budgets_guardrails": True,
        "continuous_isolation_audit": True,
        "adversarial_leakage_tests": True,
        "incident_containment_actions": True,
    }


def _tenant_id_aligned(
    execution_context: dict[str, Any], isolation_state: dict[str, Any], audit_signals: dict[str, Any]
) -> bool:
    execution_tenant_id = execution_context.get("tenant_id")
    isolation_tenant_id = isolation_state.get("tenant_id")
    audit_tenant_id = audit_signals.get("tenant_id")
    return (
        isinstance(execution_tenant_id, str)
        and execution_tenant_id.strip() != ""
        and execution_tenant_id == isolation_tenant_id
        and execution_tenant_id == audit_tenant_id
    )


def _key_policy_version_aligned(isolation_state: dict[str, Any], audit_signals: dict[str, Any]) -> bool:
    isolation_version = isolation_state.get("tenant_key_policy_version")
    audit_version = audit_signals.get("tenant_key_policy_version")
    return (
        isinstance(isolation_version, str)
        and isolation_version.strip() != ""
        and isolation_version == audit_version
    )


def _budget_profile_aligned(
    execution_context: dict[str, Any], isolation_state: dict[str, Any], audit_signals: dict[str, Any]
) -> bool:
    execution_budget_profile_id = execution_context.get("tenant_budget_profile_id")
    isolation_budget_profile_id = isolation_state.get("tenant_budget_profile_id")
    audit_budget_profile_id = audit_signals.get("tenant_budget_profile_id")
    return (
        isinstance(execution_budget_profile_id, str)
        and execution_budget_profile_id.strip() != ""
        and execution_budget_profile_id == isolation_budget_profile_id
        and execution_budget_profile_id == audit_budget_profile_id
    )


def _valid_execution_event(event: Any) -> bool:
    if not isinstance(event, dict):
        return False
    required = ("event_id", "tenant_id", "plugin_id", "queue_namespace", "storage_namespace", "cache_namespace")
    return all(isinstance(event.get(key), str) and event.get(key).strip() != "" for key in required)


def _collect_execution_events(execution_context: dict[str, Any]) -> list[dict[str, str]]:
    rows = execution_context.get("execution_events")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if _valid_execution_event(row)]


def _event_violations(event: dict[str, str], tenant_id: str) -> tuple[list[str], list[str], list[str]]:
    leakage_attempts: list[str] = []
    namespace_violations: list[str] = []
    key_scope_violations: list[str] = []
    event_tenant = event["tenant_id"]
    if event_tenant != tenant_id:
        leakage_attempts.append(event["event_id"])
    for ns_key in ("queue_namespace", "storage_namespace", "cache_namespace"):
        namespace = event[ns_key]
        if not namespace.startswith(f"{event_tenant}/"):
            namespace_violations.append(f"{event['event_id']}:{ns_key}")
    key_scope = event.get("key_scope")
    if isinstance(key_scope, str) and key_scope.strip():
        if not key_scope.startswith(f"{event_tenant}:"):
            key_scope_violations.append(event["event_id"])
    return leakage_attempts, namespace_violations, key_scope_violations


def _adversarial_status(execution_context: dict[str, Any]) -> tuple[int, bool]:
    adversarial_tests = execution_context.get("adversarial_tests")
    if not isinstance(adversarial_tests, list):
        return 0, False
    adversarial_pass = True
    for test in adversarial_tests:
        if not isinstance(test, dict):
            adversarial_pass = False
            continue
        if test.get("result") != "blocked":
            adversarial_pass = False
    return len(adversarial_tests), adversarial_pass


def execute_cross_tenant_isolation_runtime(
    *, execution_context: dict[str, Any], audit_signals: dict[str, Any]
) -> dict[str, Any]:
    tenant_id = execution_context.get("tenant_id")
    events = _collect_execution_events(execution_context)
    leakage_attempts: list[str] = []
    namespace_violations: list[str] = []
    key_scope_violations: list[str] = []
    for event in events:
        leak, ns, key = _event_violations(event, str(tenant_id))
        leakage_attempts.extend(leak)
        namespace_violations.extend(ns)
        key_scope_violations.extend(key)
    adversarial_count, adversarial_pass = _adversarial_status(execution_context)
    containment_actions = audit_signals.get("containment_actions")
    if not isinstance(containment_actions, list):
        containment_actions = []
    containment_ready = len(containment_actions) > 0 and all(
        isinstance(action, str) and action.strip() != "" for action in containment_actions
    )
    return {
        "events_processed": len(events),
        "leakage_attempts": leakage_attempts,
        "namespace_violations": namespace_violations,
        "key_scope_violations": key_scope_violations,
        "adversarial_tests_count": adversarial_count,
        "adversarial_pass": adversarial_pass,
        "containment_ready": containment_ready,
    }


def summarize_cross_tenant_isolation(
    *, execution_context: dict[str, Any], isolation_state: dict[str, Any], audit_signals: dict[str, Any]
) -> dict[str, bool]:
    execution = execute_cross_tenant_isolation_runtime(
        execution_context=execution_context,
        audit_signals=audit_signals,
    )
    return {
        "tenant_identity_full_path": execution_context.get("tenant_identity_full_path") is True
        and _tenant_id_aligned(execution_context, isolation_state, audit_signals)
        and execution["events_processed"] > 0,
        "runtime_queue_storage_isolated": isolation_state.get("runtime_queue_storage_isolated") is True
        and len(execution["namespace_violations"]) == 0,
        "cache_artifact_reuse_blocked": isolation_state.get("cache_artifact_reuse_blocked") is True
        and len(execution["leakage_attempts"]) == 0,
        "tenant_keys_policy_controls_applied": isolation_state.get("tenant_keys_policy_controls_applied")
        is True
        and _key_policy_version_aligned(isolation_state, audit_signals)
        and len(execution["key_scope_violations"]) == 0,
        "tenant_budgets_guardrails_enforced": isolation_state.get("tenant_budgets_guardrails_enforced") is True,
        "tenant_budget_profile_consistent": _budget_profile_aligned(
            execution_context, isolation_state, audit_signals
        ),
        "continuous_isolation_audit_present": audit_signals.get("continuous_isolation_audit_present") is True,
        "adversarial_leakage_tests_present": isolation_state.get("adversarial_leakage_tests_present") is True
        and execution["adversarial_tests_count"] > 0
        and execution["adversarial_pass"] is True,
        "incident_containment_actions_defined": audit_signals.get("incident_containment_actions_defined") is True
        and execution["containment_ready"] is True,
    }


def evaluate_cross_tenant_isolation_gate(
    *,
    run_id: str,
    mode: str,
    execution_context: dict[str, Any],
    isolation_state: dict[str, Any],
    audit_signals: dict[str, Any],
) -> dict[str, Any]:
    execution = execute_cross_tenant_isolation_runtime(
        execution_context=execution_context,
        audit_signals=audit_signals,
    )
    checks = summarize_cross_tenant_isolation(
        execution_context=execution_context,
        isolation_state=isolation_state,
        audit_signals=audit_signals,
    )
    failed_gates = [name for name, passed in checks.items() if passed is not True]
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": CROSS_TENANT_SCHEMA,
        "schema_version": CROSS_TENANT_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "release_blocked": status == "fail",
        "checks": checks,
        "execution": execution,
        "failed_gates": failed_gates,
        "isolation_contract": build_cross_tenant_contract(),
        "evidence": {
            "execution_ref": "data/cross_tenant_isolation/execution_context.json",
            "isolation_ref": "data/cross_tenant_isolation/isolation_state.json",
            "audit_ref": "data/cross_tenant_isolation/audit_signals.json",
            "history_ref": "data/cross_tenant_isolation/trend_history.jsonl",
            "events_ref": "data/cross_tenant_isolation/isolation_events.jsonl",
        },
    }


def update_cross_tenant_isolation_history(
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


def build_isolation_event_rows(*, report: dict[str, Any]) -> list[dict[str, Any]]:
    execution = report.get("execution")
    if not isinstance(execution, dict):
        return []
    return [
        {"run_id": report.get("run_id"), "signal": "events_processed", "value": execution.get("events_processed", 0)},
        {"run_id": report.get("run_id"), "signal": "leakage_attempts", "value": len(execution.get("leakage_attempts", []))},
        {"run_id": report.get("run_id"), "signal": "namespace_violations", "value": len(execution.get("namespace_violations", []))},
    ]

