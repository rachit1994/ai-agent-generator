from __future__ import annotations

import json
import subprocess


def test_local_non_regression_gate_script_passes_for_healthy_input(tmp_path) -> None:
    current = {
        "startup_ms_cold_p95": 980.0,
        "startup_ms_warm_p95": 210.0,
        "workflow_p95_ms": 1400.0,
        "workflow_success_rate": 0.995,
        "workflow_recovery_rate": 0.99,
        "developer_error_rate": 0.003,
        "cpu_peak_percent": 71.0,
        "memory_peak_mb": 820.0,
    }
    baseline = {
        "startup_ms_cold_p95": 1000.0,
        "startup_ms_warm_p95": 230.0,
        "workflow_p95_ms": 1500.0,
        "workflow_success_rate": 0.996,
        "workflow_recovery_rate": 0.991,
        "developer_error_rate": 0.004,
        "cpu_peak_percent": 75.0,
        "memory_peak_mb": 900.0,
    }
    current_path = tmp_path / "current.json"
    baseline_path = tmp_path / "baseline.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    current_path.write_text(json.dumps(current), encoding="utf-8")
    baseline_path.write_text(json.dumps(baseline), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/local_non_regression_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-01-ci",
            "--current",
            str(current_path),
            "--baseline",
            str(baseline_path),
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

