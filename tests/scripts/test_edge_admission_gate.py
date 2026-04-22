from __future__ import annotations

import json
import subprocess


def test_edge_admission_gate_script_passes_for_healthy_payloads(tmp_path) -> None:
    policy = {
        "edge_middleware_present": True,
        "scoped_limits_present": True,
        "scope_keys": ["tenant_id", "user_id", "api_key", "route"],
        "burst_sustained_budgets": True,
        "burst_limit_per_minute": 60,
        "sustained_limit_per_hour": 600,
        "outage_policy_defined": True,
        "outage_mode": "fail_closed",
        "dynamic_policy_updates_safe": True,
        "policy_version": "edge-policy-v1",
        "max_retry_after_seconds": 60,
    }
    counters = {
        "deny_throttle_metrics": True,
        "deny_count": 1,
        "throttle_count": 1,
        "sampled_requests": 3,
    }
    traffic = {
        "retry_after_compliant": True,
        "retry_after_seconds": 15,
        "integration_load_tests_present": True,
        "load_test_profile": "burst-and-sustained-traffic",
        "request_events": [
            {
                "event_id": "edge-evt-001",
                "tenant_id": "tenant-a",
                "user_id": "user-1",
                "api_key": "key-1",
                "route": "/v1/chat",
                "decision": "allow",
                "retry_after_seconds": 0,
            },
            {
                "event_id": "edge-evt-002",
                "tenant_id": "tenant-a",
                "user_id": "user-1",
                "api_key": "key-1",
                "route": "/v1/chat",
                "decision": "throttle",
                "retry_after_seconds": 15,
            },
            {
                "event_id": "edge-evt-003",
                "tenant_id": "tenant-a",
                "user_id": "user-2",
                "api_key": "key-2",
                "route": "/v1/tools",
                "decision": "deny",
                "retry_after_seconds": 30,
            },
        ],
    }
    policy_path = tmp_path / "policy.json"
    counters_path = tmp_path / "counters.json"
    traffic_path = tmp_path / "traffic.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    counters_path.write_text(json.dumps(counters), encoding="utf-8")
    traffic_path.write_text(json.dumps(traffic), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/edge_admission_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-05-ci",
            "--policy",
            str(policy_path),
            "--counters",
            str(counters_path),
            "--traffic",
            str(traffic_path),
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
    events_path = tmp_path / "admission_events.jsonl"
    assert events_path.read_text(encoding="utf-8").strip()

