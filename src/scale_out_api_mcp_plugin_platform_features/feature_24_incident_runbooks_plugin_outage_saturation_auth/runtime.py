"""Runtime for feature 24 incident runbooks gate."""

from __future__ import annotations

from typing import Any

from .contracts import INCIDENT_RUNBOOKS_SCHEMA, INCIDENT_RUNBOOKS_SCHEMA_VERSION


def build_incident_runbooks_contract() -> dict[str, object]:
    return {
        "production_runbooks_outage_saturation_auth": True,
        "executable_steps_scripts_per_runbook": True,
        "ownership_and_escalation_metadata": True,
        "alerts_dashboards_linkage": True,
        "versioned_change_control_review": True,
        "gameday_drill_validation": True,
        "drill_evidence_capture_auditability": True,
        "post_incident_feedback_revision_loop": True,
    }


def _valid_incident_types(value: Any) -> bool:
    expected = {"outage", "saturation", "auth"}
    return isinstance(value, list) and set(value) == expected


def _escalation_policy_aligned(operations: dict[str, Any], drills: dict[str, Any]) -> bool:
    operations_policy_version = operations.get("escalation_policy_version")
    drills_policy_version = drills.get("escalation_policy_version")
    return (
        isinstance(operations_policy_version, str)
        and operations_policy_version.strip() != ""
        and operations_policy_version == drills_policy_version
    )


def summarize_incident_runbooks_health(
    *, runbooks: dict[str, Any], operations: dict[str, Any], drills: dict[str, Any]
) -> dict[str, bool]:
    return {
        "production_incident_runbooks_authored": runbooks.get("production_incident_runbooks_authored")
        is True
        and _valid_incident_types(runbooks.get("incident_types")),
        "executable_steps_scripts_added": runbooks.get("executable_steps_scripts_added") is True,
        "ownership_escalation_metadata_attached": operations.get(
            "ownership_escalation_metadata_attached"
        )
        is True
        and _escalation_policy_aligned(operations, drills),
        "runbooks_connected_alerts_dashboards": operations.get("runbooks_connected_alerts_dashboards")
        is True,
        "runbooks_versioned_change_control_reviewed": operations.get(
            "runbooks_versioned_change_control_reviewed"
        )
        is True,
        "runbooks_validated_with_gameday_drills": drills.get("runbooks_validated_with_gameday_drills")
        is True
        and _valid_incident_types(drills.get("validated_incident_types")),
        "drill_evidence_captured_for_audit": drills.get("drill_evidence_captured_for_audit")
        is True,
        "post_incident_feedback_integrated_into_revisions": drills.get(
            "post_incident_feedback_integrated_into_revisions"
        )
        is True,
    }


def evaluate_incident_runbooks_gate(
    *,
    run_id: str,
    mode: str,
    runbooks: dict[str, Any],
    operations: dict[str, Any],
    drills: dict[str, Any],
) -> dict[str, Any]:
    checks = summarize_incident_runbooks_health(
        runbooks=runbooks, operations=operations, drills=drills
    )
    failed_gates = [name for name, passed in checks.items() if passed is not True]
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": INCIDENT_RUNBOOKS_SCHEMA,
        "schema_version": INCIDENT_RUNBOOKS_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "release_blocked": status == "fail",
        "checks": checks,
        "failed_gates": failed_gates,
        "incident_runbooks_contract": build_incident_runbooks_contract(),
        "evidence": {
            "runbooks_ref": "data/incident_runbooks/runbooks.json",
            "ops_ref": "data/incident_runbooks/operations.json",
            "drills_ref": "data/incident_runbooks/drills.json",
            "history_ref": "data/incident_runbooks/trend_history.jsonl",
        },
    }


def update_incident_runbooks_history(
    *, existing: list[dict[str, Any]], report: dict[str, Any]
) -> list[dict[str, Any]]:
    row = {
        "run_id": report["run_id"],
        "status": report["status"],
        "failed_gate_count": len(report["failed_gates"]),
    }
    return [*existing, row]

