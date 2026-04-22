from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_24_incident_runbooks_plugin_outage_saturation_auth import (
    build_incident_runbooks_contract,
    evaluate_incident_runbooks_gate,
    update_incident_runbooks_history,
    validate_incident_runbooks_report_dict,
)


def _runbooks() -> dict[str, object]:
    return {
        "production_incident_runbooks_authored": True,
        "executable_steps_scripts_added": True,
        "incident_types": ["outage", "saturation", "auth"],
    }


def _operations() -> dict[str, object]:
    return {
        "ownership_escalation_metadata_attached": True,
        "escalation_policy_version": "2026.04",
        "runbooks_connected_alerts_dashboards": True,
        "runbooks_versioned_change_control_reviewed": True,
    }


def _drills() -> dict[str, object]:
    return {
        "runbooks_validated_with_gameday_drills": True,
        "validated_incident_types": ["outage", "saturation", "auth"],
        "escalation_policy_version": "2026.04",
        "drill_evidence_captured_for_audit": True,
        "post_incident_feedback_integrated_into_revisions": True,
    }


def test_incident_runbooks_gate_passes_for_complete_inputs() -> None:
    report = evaluate_incident_runbooks_gate(
        run_id="run-feature-24-pass",
        mode="ci",
        runbooks=_runbooks(),
        operations=_operations(),
        drills=_drills(),
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert validate_incident_runbooks_report_dict(report) == []


def test_incident_runbooks_gate_fail_closes_on_missing_escalation_metadata() -> None:
    operations = _operations()
    operations["ownership_escalation_metadata_attached"] = False
    report = evaluate_incident_runbooks_gate(
        run_id="run-feature-24-fail",
        mode="preflight",
        runbooks=_runbooks(),
        operations=operations,
        drills=_drills(),
    )
    assert report["status"] == "fail"
    assert "ownership_escalation_metadata_attached" in report["failed_gates"]


def test_incident_runbooks_gate_fail_closes_on_incomplete_incident_type_coverage() -> None:
    drills = _drills()
    drills["validated_incident_types"] = ["outage", "auth"]
    report = evaluate_incident_runbooks_gate(
        run_id="run-feature-24-drill-coverage-gap",
        mode="preflight",
        runbooks=_runbooks(),
        operations=_operations(),
        drills=drills,
    )
    assert report["status"] == "fail"
    assert "runbooks_validated_with_gameday_drills" in report["failed_gates"]


def test_incident_runbooks_gate_fail_closes_on_escalation_policy_version_drift() -> None:
    drills = _drills()
    drills["escalation_policy_version"] = "2026.05"
    report = evaluate_incident_runbooks_gate(
        run_id="run-feature-24-escalation-policy-drift",
        mode="preflight",
        runbooks=_runbooks(),
        operations=_operations(),
        drills=drills,
    )
    assert report["status"] == "fail"
    assert "ownership_escalation_metadata_attached" in report["failed_gates"]


def test_incident_runbooks_contract_is_deterministic() -> None:
    assert build_incident_runbooks_contract() == build_incident_runbooks_contract()


def test_incident_runbooks_history_appends_row() -> None:
    report = evaluate_incident_runbooks_gate(
        run_id="run-feature-24-history",
        mode="ci",
        runbooks=_runbooks(),
        operations=_operations(),
        drills=_drills(),
    )
    history = update_incident_runbooks_history(existing=[], report=report)
    assert history[0]["run_id"] == "run-feature-24-history"

