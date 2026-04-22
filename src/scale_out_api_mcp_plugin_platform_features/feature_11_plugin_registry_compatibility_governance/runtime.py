"""Runtime for feature 11 plugin registry compatibility governance."""

from __future__ import annotations

from typing import Any

from .contracts import PLUGIN_REGISTRY_SCHEMA, PLUGIN_REGISTRY_SCHEMA_VERSION


def build_plugin_registry_contract() -> dict[str, object]:
    return {
        "registry_service": True,
        "metadata_contract": ["plugin_id", "version", "capabilities", "signature"],
        "compatibility_policy": "semver+matrix",
        "publish_gates": ["metadata_valid", "compatibility_pass", "signature_verified"],
        "governance_controls": ["deprecate", "rollback_safe", "audit_history"],
    }


def _valid_rollout_governance(governance: dict[str, Any]) -> bool:
    canary_percent = governance.get("canary_percent")
    rollout_strategy = governance.get("rollout_strategy")
    return (
        isinstance(canary_percent, int)
        and 0 < canary_percent <= 100
        and isinstance(rollout_strategy, str)
        and rollout_strategy in {"canary", "progressive"}
    )


def _compatibility_version_aligned(
    compatibility_matrix: dict[str, Any], governance: dict[str, Any]
) -> bool:
    compatibility_version = compatibility_matrix.get("compatibility_matrix_version")
    governance_version = governance.get("compatibility_matrix_version")
    return (
        isinstance(compatibility_version, str)
        and compatibility_version.strip() != ""
        and compatibility_version == governance_version
    )


def _valid_publish_event(event: Any) -> bool:
    if not isinstance(event, dict):
        return False
    required = ("event_id", "plugin_id", "version", "signature_valid", "compatibility_pass", "decision")
    if not all(key in event for key in required):
        return False
    if not isinstance(event.get("plugin_id"), str) or not event.get("plugin_id").strip():
        return False
    if not isinstance(event.get("version"), str) or not event.get("version").strip():
        return False
    if not isinstance(event.get("signature_valid"), bool):
        return False
    if not isinstance(event.get("compatibility_pass"), bool):
        return False
    return event.get("decision") in {"published", "rejected"}


def _collect_publish_events(registry_state: dict[str, Any]) -> list[dict[str, Any]]:
    events = registry_state.get("publish_events")
    if not isinstance(events, list):
        return []
    return [event for event in events if _valid_publish_event(event)]


def execute_plugin_registry_runtime(
    *, registry_state: dict[str, Any], compatibility_matrix: dict[str, Any], governance: dict[str, Any]
) -> dict[str, Any]:
    events = _collect_publish_events(registry_state)
    decision_violations: list[str] = []
    canary_violations: list[str] = []
    strategy = governance.get("rollout_strategy")
    canary_percent = governance.get("canary_percent")
    for event in events:
        if (event["signature_valid"] is False or event["compatibility_pass"] is False) and event["decision"] == "published":
            decision_violations.append(event["event_id"])
        if strategy == "canary" and (
            not isinstance(canary_percent, int) or canary_percent <= 0 or canary_percent > 100
        ):
            canary_violations.append(event["event_id"])
    tested_plugins = compatibility_matrix.get("tested_plugins")
    matrix_coverage_ok = isinstance(tested_plugins, list) and bool(tested_plugins) and all(
        event.get("plugin_id") in tested_plugins for event in events
    )
    return {
        "events_processed": len(events),
        "decision_violations": decision_violations,
        "canary_violations": canary_violations,
        "matrix_coverage_ok": matrix_coverage_ok,
    }


def summarize_plugin_registry_governance(
    *, registry_state: dict[str, Any], compatibility_matrix: dict[str, Any], governance: dict[str, Any]
) -> dict[str, bool]:
    execution = execute_plugin_registry_runtime(
        registry_state=registry_state, compatibility_matrix=compatibility_matrix, governance=governance
    )
    return {
        "registry_service_present": registry_state.get("registry_service_present") is True,
        "metadata_version_contract_enforced": registry_state.get("metadata_version_contract_enforced") is True,
        "compatibility_matrix_automated": compatibility_matrix.get("compatibility_matrix_automated")
        is True
        and _compatibility_version_aligned(compatibility_matrix, governance),
        "publish_rollout_gated": governance.get("publish_rollout_gated") is True
        and _valid_rollout_governance(governance),
        "deprecation_rollback_governed": governance.get("deprecation_rollback_governed") is True,
        "provenance_signature_verified": registry_state.get("provenance_signature_verified") is True,
        "governance_audit_history_persisted": governance.get("governance_audit_history_persisted") is True,
        "incompatible_rejection_tests_present": compatibility_matrix.get("incompatible_rejection_tests_present") is True,
        "runtime_publish_decisions_valid": len(execution["decision_violations"]) == 0,
        "runtime_canary_config_valid": len(execution["canary_violations"]) == 0,
        "runtime_matrix_coverage_valid": execution["matrix_coverage_ok"] is True,
    }


def evaluate_plugin_registry_gate(
    *,
    run_id: str,
    mode: str,
    registry_state: dict[str, Any],
    compatibility_matrix: dict[str, Any],
    governance: dict[str, Any],
) -> dict[str, Any]:
    execution = execute_plugin_registry_runtime(
        registry_state=registry_state, compatibility_matrix=compatibility_matrix, governance=governance
    )
    checks = summarize_plugin_registry_governance(
        registry_state=registry_state,
        compatibility_matrix=compatibility_matrix,
        governance=governance,
    )
    failed_gates = [name for name, passed in checks.items() if passed is not True]
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": PLUGIN_REGISTRY_SCHEMA,
        "schema_version": PLUGIN_REGISTRY_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "release_blocked": status == "fail",
        "checks": checks,
        "execution": execution,
        "failed_gates": failed_gates,
        "registry_contract": build_plugin_registry_contract(),
        "evidence": {
            "registry_ref": "data/plugin_registry/registry_state.json",
            "compatibility_ref": "data/plugin_registry/compatibility_matrix.json",
            "governance_ref": "data/plugin_registry/governance.json",
            "history_ref": "data/plugin_registry/trend_history.jsonl",
            "events_ref": "data/plugin_registry/registry_events.jsonl",
        },
    }


def update_plugin_registry_history(
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


def build_registry_event_rows(*, report: dict[str, Any]) -> list[dict[str, Any]]:
    execution = report.get("execution")
    if not isinstance(execution, dict):
        return []
    run_id = report.get("run_id")
    return [
        {"run_id": run_id, "signal": "events_processed", "value": execution.get("events_processed", 0)},
        {"run_id": run_id, "signal": "decision_violations", "value": len(execution.get("decision_violations", []))},
        {"run_id": run_id, "signal": "canary_violations", "value": len(execution.get("canary_violations", []))},
    ]

