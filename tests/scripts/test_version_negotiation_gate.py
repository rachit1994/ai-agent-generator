from __future__ import annotations

import json
import subprocess


def test_version_negotiation_gate_script_passes_for_healthy_payloads(tmp_path) -> None:
    handshake = {"handshake_implemented": True}
    compatibility = {
        "version_ranges_advertised_selected": True,
        "incompatible_rejections_deterministic": True,
        "dual_version_rollback_safe": True,
        "deprecation_windows_enforced_tested": True,
        "mixed_version_fleet_scenarios_tested": True,
        "rollout_gated_on_compat_failures": True,
    }
    telemetry = {"negotiated_version_telemetry_tracked": True}
    handshake_path = tmp_path / "handshake.json"
    compatibility_path = tmp_path / "compatibility.json"
    telemetry_path = tmp_path / "telemetry.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    handshake_path.write_text(json.dumps(handshake), encoding="utf-8")
    compatibility_path.write_text(json.dumps(compatibility), encoding="utf-8")
    telemetry_path.write_text(json.dumps(telemetry), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/version_negotiation_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-16-ci",
            "--handshake",
            str(handshake_path),
            "--compatibility",
            str(compatibility_path),
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

