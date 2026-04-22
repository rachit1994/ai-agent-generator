from __future__ import annotations

import json
import subprocess


def test_config_overlay_gate_script_passes_for_healthy_payloads(tmp_path) -> None:
    base = {"shared_schema_present": True, "config_schema_version": "2026.04.1"}
    overlay = {
        "override_allowlist_enforced": True,
        "override_allowlist_hash": "sha256:allowlist-v1",
        "config_schema_version": "2026.04.1",
    }
    resolved = {
        "config_schema_version": "2026.04.1",
        "applied_precedence": ["base", "env_overlay", "runtime_override_allowlist"],
        "override_allowlist_hash": "sha256:allowlist-v1",
        "overlay_merge_deterministic": True,
        "invariants_fail_fast_enforced": True,
        "drift_detection_present": True,
        "secret_redaction_consistent": True,
        "versioned_migrations_supported": True,
        "adapter_overlay_tests_present": True,
    }
    base_path = tmp_path / "base.json"
    overlay_path = tmp_path / "overlay.json"
    resolved_path = tmp_path / "resolved.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    base_path.write_text(json.dumps(base), encoding="utf-8")
    overlay_path.write_text(json.dumps(overlay), encoding="utf-8")
    resolved_path.write_text(json.dumps(resolved), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/config_overlay_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-15-ci",
            "--base",
            str(base_path),
            "--overlay",
            str(overlay_path),
            "--resolved",
            str(resolved_path),
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

