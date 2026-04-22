from __future__ import annotations

import json
import subprocess


def test_local_prod_parity_gate_script_passes_for_healthy_payloads(tmp_path) -> None:
    payload = {
        "semantic_outputs": {"decision": "allow", "code": 200},
        "state_transitions": ["queued", "active", "done"],
        "errors": [],
        "authz": {"scope": "tenant:read", "decision": "allow"},
        "idempotency": {"replay_safe": True},
    }
    local_path = tmp_path / "local.json"
    prod_path = tmp_path / "prod.json"
    diff_path = tmp_path / "diff.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    local_path.write_text(json.dumps(payload), encoding="utf-8")
    prod_path.write_text(json.dumps(payload), encoding="utf-8")
    diff_path.write_text(json.dumps({"diagnostics": []}), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/local_prod_parity_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-14-ci",
            "--local",
            str(local_path),
            "--prod",
            str(prod_path),
            "--diff",
            str(diff_path),
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

