from __future__ import annotations

import json
import subprocess


def test_plugin_registry_gate_script_passes_for_healthy_payloads(tmp_path) -> None:
    registry = {
        "registry_service_present": True,
        "metadata_version_contract_enforced": True,
        "provenance_signature_verified": True,
        "publish_events": [
            {
                "event_id": "reg-evt-001",
                "plugin_id": "plugin-x",
                "version": "1.4.0",
                "signature_valid": True,
                "compatibility_pass": True,
                "decision": "published",
            },
            {
                "event_id": "reg-evt-002",
                "plugin_id": "plugin-y",
                "version": "2.0.0",
                "signature_valid": True,
                "compatibility_pass": False,
                "decision": "rejected",
            },
        ],
    }
    compatibility = {
        "compatibility_matrix_automated": True,
        "incompatible_rejection_tests_present": True,
        "compatibility_matrix_version": "2026.04",
        "tested_plugins": ["plugin-x", "plugin-y"],
    }
    governance = {
        "publish_rollout_gated": True,
        "canary_percent": 10,
        "rollout_strategy": "canary",
        "compatibility_matrix_version": "2026.04",
        "deprecation_rollback_governed": True,
        "governance_audit_history_persisted": True,
    }
    registry_path = tmp_path / "registry.json"
    compatibility_path = tmp_path / "compatibility.json"
    governance_path = tmp_path / "governance.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    compatibility_path.write_text(json.dumps(compatibility), encoding="utf-8")
    governance_path.write_text(json.dumps(governance), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/plugin_registry_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-11-ci",
            "--registry",
            str(registry_path),
            "--compatibility",
            str(compatibility_path),
            "--governance",
            str(governance_path),
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
    events_path = tmp_path / "registry_events.jsonl"
    assert events_path.read_text(encoding="utf-8").strip()

