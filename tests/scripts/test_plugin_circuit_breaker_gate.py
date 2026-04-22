from __future__ import annotations

import json
import subprocess


def test_plugin_circuit_breaker_gate_script_passes(tmp_path) -> None:
    runtime = {
        "plugin_level_circuit_breaker_runtime": True,
        "plugin_id": "plugin-x",
        "current_state": "closed",
        "plugin_level_retry_budget_enforcement": True,
        "retry_budget_policy_version": "2026.04",
        "retry_budget_remaining": 7,
        "retry_budget_limit": 10,
        "bulkhead_blast_radius_containment": True,
    }
    policy = {
        "failure_classification_for_transitions": True,
        "failure_classes": ["transient", "permanent", "throttle"],
        "retry_budget_policy_version": "2026.04",
        "transition_policy_version": "2026.04",
        "fallback_behavior_for_open_circuits": True,
        "fallback_mode": "serve_cached",
        "cooldown_seconds": 30,
        "half_open_probe_count": 2,
        "operator_safe_breaker_controls": True,
        "operator_approval_ticket": "CAB-2026-0177",
    }
    telemetry = {
        "plugin_id": "plugin-x",
        "state_transition_telemetry": True,
        "transition_policy_version": "2026.04",
        "transition_counts": {"open": 2, "half_open": 3, "closed": 4},
        "transition_events": [
            {
                "event_id": "evt-01",
                "from_state": "closed",
                "to_state": "open",
                "failure_class": "throttle",
                "retry_attempt": 1,
            },
            {
                "event_id": "evt-02",
                "from_state": "open",
                "to_state": "half_open",
                "failure_class": "transient",
                "retry_attempt": 1,
            },
            {
                "event_id": "evt-03",
                "from_state": "half_open",
                "to_state": "closed",
                "failure_class": "transient",
                "retry_attempt": 0,
            },
        ],
        "degraded_plugin_end_to_end_tests": True,
        "degraded_test_run_id": "cb-degraded-09-001",
    }
    runtime_path = tmp_path / "runtime.json"
    policy_path = tmp_path / "policy.json"
    telemetry_path = tmp_path / "telemetry.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    runtime_path.write_text(json.dumps(runtime), encoding="utf-8")
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    telemetry_path.write_text(json.dumps(telemetry), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/plugin_circuit_breaker_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-09-ci",
            "--runtime",
            str(runtime_path),
            "--policy",
            str(policy_path),
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
    assert report["breaker_execution"]["events_processed"] == 3
