from __future__ import annotations

import json
import subprocess


def test_semantic_parity_gate_script_passes_for_matching_payloads(tmp_path) -> None:
    payload = {
        "idempotency": [{"operation": "invoke", "request_hash": "a1", "result_hash": "r1", "replay_safe": True}],
        "authz": [{"role": "dev", "resource": "tool:x", "decision": "allow", "reason_code": "ok"}],
        "state_transitions": [
            {"operation": "run", "from_state": "queued", "to_state": "active", "transition_valid": True}
        ],
        "error_taxonomy": [{"operation": "invoke", "error_code": "none", "retryable": False, "class": "ok"}],
    }
    local_path = tmp_path / "local.json"
    server_path = tmp_path / "server.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    local_path.write_text(json.dumps(payload), encoding="utf-8")
    server_path.write_text(json.dumps(payload), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/semantic_parity_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-02-ci",
            "--local",
            str(local_path),
            "--server",
            str(server_path),
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

