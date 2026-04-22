from __future__ import annotations

import json
import subprocess


def test_incident_runbooks_gate_script_passes(tmp_path) -> None:
    runbooks = {
        "production_incident_runbooks_authored": True,
        "executable_steps_scripts_added": True,
        "incident_types": ["outage", "saturation", "auth"],
    }
    operations = {
        "ownership_escalation_metadata_attached": True,
        "escalation_policy_version": "2026.04",
        "runbooks_connected_alerts_dashboards": True,
        "runbooks_versioned_change_control_reviewed": True,
    }
    drills = {
        "runbooks_validated_with_gameday_drills": True,
        "validated_incident_types": ["outage", "saturation", "auth"],
        "escalation_policy_version": "2026.04",
        "drill_evidence_captured_for_audit": True,
        "post_incident_feedback_integrated_into_revisions": True,
    }
    runbooks_path = tmp_path / "runbooks.json"
    operations_path = tmp_path / "operations.json"
    drills_path = tmp_path / "drills.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    runbooks_path.write_text(json.dumps(runbooks), encoding="utf-8")
    operations_path.write_text(json.dumps(operations), encoding="utf-8")
    drills_path.write_text(json.dumps(drills), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/incident_runbooks_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-24-ci",
            "--runbooks",
            str(runbooks_path),
            "--operations",
            str(operations_path),
            "--drills",
            str(drills_path),
            "--out",
            str(out_path),
            "--history",
            str(history_path),
        ],
        check=False,
        text=True,
    )
    assert result.returncode == 0
    report = json.loads(out_path.read_text(encoding="utf-8"))
    assert report["status"] == "pass"
    assert history_path.read_text(encoding="utf-8").strip()

