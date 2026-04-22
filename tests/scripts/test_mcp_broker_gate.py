from __future__ import annotations

import json
import subprocess


def test_mcp_broker_gate_script_passes_for_healthy_payloads(tmp_path) -> None:
    broker = {
        "broker_service_present": True,
        "broker_instance_id": "broker-a1",
        "authz_boundary_enforced": True,
        "deterministic_routing_present": True,
    }
    sessions = {
        "session_lifecycle_api_present": True,
        "session_persistence_reclaim": True,
        "heartbeat_resume_supported": True,
        "disconnect_failover_tests_present": True,
    }
    telemetry = {"broker_observability_present": True, "broker_instance_id": "broker-a1"}
    broker_path = tmp_path / "broker.json"
    sessions_path = tmp_path / "sessions.json"
    telemetry_path = tmp_path / "telemetry.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    broker_path.write_text(json.dumps(broker), encoding="utf-8")
    sessions_path.write_text(json.dumps(sessions), encoding="utf-8")
    telemetry_path.write_text(json.dumps(telemetry), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/mcp_broker_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-10-ci",
            "--broker",
            str(broker_path),
            "--sessions",
            str(sessions_path),
            "--telemetry",
            str(telemetry_path),
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

