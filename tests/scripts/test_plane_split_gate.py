from __future__ import annotations

import json
import subprocess


def test_plane_split_gate_script_passes_for_isolated_payloads(tmp_path) -> None:
    control = {
        "service_name": "control-plane-api",
        "scaling_policy": "control-cpu_target_60",
        "auth_boundary": "service-token",
        "telemetry_channel": "control-traces",
        "owner_team": "platform-control",
        "rollback_runbook": "RB-CONTROL-003",
        "dispatch_events": [
            {
                "event_id": "evt-001",
                "run_id": "run-feature-03-ci",
                "from_plane": "control",
                "to_plane": "data",
                "route": "schedule_job",
                "status": "dispatched",
            }
        ],
    }
    data = {
        "service_name": "data-plane-worker",
        "scaling_policy": "data-queue_depth_target",
        "auth_boundary": "service-token",
        "telemetry_channel": "data-traces",
        "control_dependency": False,
        "owner_team": "platform-data",
    }
    control_path = tmp_path / "control.json"
    data_path = tmp_path / "data.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    control_path.write_text(json.dumps(control), encoding="utf-8")
    data_path.write_text(json.dumps(data), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/plane_split_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-03-ci",
            "--control",
            str(control_path),
            "--data",
            str(data_path),
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
    events_path = tmp_path / "plane_events.jsonl"
    assert events_path.read_text(encoding="utf-8").strip()

