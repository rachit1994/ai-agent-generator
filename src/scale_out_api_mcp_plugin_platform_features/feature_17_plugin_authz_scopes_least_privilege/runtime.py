"""Runtime for feature 17 plugin authz scopes and least privilege."""

from __future__ import annotations

from typing import Any

from .contracts import PLUGIN_AUTHZ_SCHEMA, PLUGIN_AUTHZ_SCHEMA_VERSION


def build_plugin_authz_contract() -> dict[str, object]:
    return {
        "scope_taxonomy": True,
        "least_privilege_engine": True,
        "invocation_scope_binding": True,
        "deny_by_default": True,
        "policy_versioning_simulation": True,
        "allow_deny_audit_logging": True,
        "privilege_escalation_tests": True,
        "admin_policy_controls": True,
    }


def _valid_audit_metrics(audit_logs: dict[str, Any]) -> bool:
    allow_decisions = audit_logs.get("allow_decisions")
    deny_decisions = audit_logs.get("deny_decisions")
    total_decisions = audit_logs.get("total_decisions")
    return (
        isinstance(allow_decisions, int)
        and allow_decisions >= 0
        and isinstance(deny_decisions, int)
        and deny_decisions >= 0
        and isinstance(total_decisions, int)
        and total_decisions == (allow_decisions + deny_decisions)
        and total_decisions > 0
    )


def _taxonomy_policy_version_aligned(taxonomy: dict[str, Any], policy_state: dict[str, Any]) -> bool:
    taxonomy_version = taxonomy.get("policy_model_version")
    policy_version = policy_state.get("policy_model_version")
    return (
        isinstance(taxonomy_version, str)
        and taxonomy_version.strip() != ""
        and taxonomy_version == policy_version
    )


def _valid_decision_event(event: Any) -> bool:
    if not isinstance(event, dict):
        return False
    required = ("event_id", "plugin_id", "scope", "decision")
    if not all(key in event for key in required):
        return False
    if not isinstance(event.get("plugin_id"), str) or not event.get("plugin_id").strip():
        return False
    if not isinstance(event.get("scope"), str) or not event.get("scope").strip():
        return False
    return event.get("decision") in {"allow", "deny"}


def _collect_decision_events(audit_logs: dict[str, Any]) -> list[dict[str, Any]]:
    events = audit_logs.get("decision_events")
    if not isinstance(events, list):
        return []
    return [event for event in events if _valid_decision_event(event)]


def _allowed_for_event(event: dict[str, Any], policy_state: dict[str, Any]) -> bool:
    allowed_scopes = policy_state.get("allowed_scopes_by_plugin")
    plugin_scopes = allowed_scopes.get(event["plugin_id"]) if isinstance(allowed_scopes, dict) else None
    return isinstance(plugin_scopes, list) and event["scope"] in plugin_scopes


def _scope_known(event: dict[str, Any], taxonomy: dict[str, Any]) -> bool:
    scope_catalog = taxonomy.get("scope_catalog")
    return isinstance(scope_catalog, list) and event["scope"] in scope_catalog


def _evaluate_decision_event(
    *,
    event: dict[str, Any],
    taxonomy: dict[str, Any],
    policy_state: dict[str, Any],
) -> tuple[bool, bool]:
    decision_valid = True
    if _allowed_for_event(event, policy_state):
        decision_valid = event["decision"] == "allow"
    else:
        decision_valid = event["decision"] == "deny"
    scope_known = _scope_known(event, taxonomy)
    return decision_valid, scope_known


def execute_plugin_authz_runtime(
    *, taxonomy: dict[str, Any], policy_state: dict[str, Any], audit_logs: dict[str, Any]
) -> dict[str, Any]:
    events = _collect_decision_events(audit_logs)
    decision_violations: list[str] = []
    unknown_scope_violations: list[str] = []
    observed_allow = 0
    observed_deny = 0
    for event in events:
        decision_valid, scope_known = _evaluate_decision_event(
            event=event,
            taxonomy=taxonomy,
            policy_state=policy_state,
        )
        if not decision_valid:
            decision_violations.append(event["event_id"])
        if not scope_known:
            unknown_scope_violations.append(event["event_id"])
        observed_allow += 1 if event["decision"] == "allow" else 0
        observed_deny += 1 if event["decision"] == "deny" else 0
    counter_coherent = (
        isinstance(audit_logs.get("allow_decisions"), int)
        and isinstance(audit_logs.get("deny_decisions"), int)
        and audit_logs.get("allow_decisions") == observed_allow
        and audit_logs.get("deny_decisions") == observed_deny
    )
    return {
        "events_processed": len(events),
        "decision_violations": decision_violations,
        "unknown_scope_violations": unknown_scope_violations,
        "decision_counter_coherent": counter_coherent,
    }


def summarize_plugin_authz_health(
    *, taxonomy: dict[str, Any], policy_state: dict[str, Any], audit_logs: dict[str, Any]
) -> dict[str, bool]:
    execution = execute_plugin_authz_runtime(
        taxonomy=taxonomy, policy_state=policy_state, audit_logs=audit_logs
    )
    return {
        "scope_taxonomy_permission_model_defined": taxonomy.get("scope_taxonomy_permission_model_defined")
        is True
        and _taxonomy_policy_version_aligned(taxonomy, policy_state),
        "least_privilege_policy_engine_implemented": policy_state.get("least_privilege_policy_engine_implemented") is True,
        "scope_checks_every_invocation": policy_state.get("scope_checks_every_invocation") is True,
        "deny_by_default_enforced": policy_state.get("deny_by_default_enforced") is True,
        "policy_authoring_simulation_versioned": policy_state.get("policy_authoring_simulation_versioned") is True,
        "allow_deny_decisions_audited": audit_logs.get("allow_deny_decisions_audited") is True
        and _valid_audit_metrics(audit_logs),
        "escalation_scope_confusion_tests_present": policy_state.get("escalation_scope_confusion_tests_present") is True,
        "admin_policy_controls_present": policy_state.get("admin_policy_controls_present") is True,
        "runtime_scope_decisions_valid": len(execution["decision_violations"]) == 0,
        "runtime_scope_catalog_valid": len(execution["unknown_scope_violations"]) == 0,
        "runtime_decision_counters_coherent": execution["decision_counter_coherent"] is True,
    }


def evaluate_plugin_authz_gate(
    *,
    run_id: str,
    mode: str,
    taxonomy: dict[str, Any],
    policy_state: dict[str, Any],
    audit_logs: dict[str, Any],
) -> dict[str, Any]:
    execution = execute_plugin_authz_runtime(
        taxonomy=taxonomy, policy_state=policy_state, audit_logs=audit_logs
    )
    checks = summarize_plugin_authz_health(taxonomy=taxonomy, policy_state=policy_state, audit_logs=audit_logs)
    failed_gates = [name for name, passed in checks.items() if passed is not True]
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": PLUGIN_AUTHZ_SCHEMA,
        "schema_version": PLUGIN_AUTHZ_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "release_blocked": status == "fail",
        "checks": checks,
        "execution": execution,
        "failed_gates": failed_gates,
        "authz_contract": build_plugin_authz_contract(),
        "evidence": {
            "taxonomy_ref": "data/plugin_authz/taxonomy.json",
            "policy_ref": "data/plugin_authz/policy_state.json",
            "audit_ref": "data/plugin_authz/audit_logs.json",
            "history_ref": "data/plugin_authz/trend_history.jsonl",
            "events_ref": "data/plugin_authz/authz_events.jsonl",
        },
    }


def update_plugin_authz_history(*, existing: list[dict[str, Any]], report: dict[str, Any]) -> list[dict[str, Any]]:
    execution = report.get("execution")
    row = {
        "run_id": report["run_id"],
        "status": report["status"],
        "failed_gate_count": len(report["failed_gates"]),
        "events_processed": execution.get("events_processed") if isinstance(execution, dict) else None,
    }
    return [*existing, row]


def build_authz_event_rows(*, report: dict[str, Any]) -> list[dict[str, Any]]:
    execution = report.get("execution")
    if not isinstance(execution, dict):
        return []
    run_id = report.get("run_id")
    return [
        {"run_id": run_id, "signal": "events_processed", "value": execution.get("events_processed", 0)},
        {"run_id": run_id, "signal": "decision_violations", "value": len(execution.get("decision_violations", []))},
        {
            "run_id": run_id,
            "signal": "unknown_scope_violations",
            "value": len(execution.get("unknown_scope_violations", [])),
        },
    ]

