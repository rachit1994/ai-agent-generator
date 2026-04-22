from __future__ import annotations

import json
import subprocess


def test_trust_bulkheads_gate_script_passes_for_healthy_payloads(tmp_path) -> None:
    policy = {
        "trust_classes_defined_enforced": True,
        "trust_classes": ["trusted", "sandboxed", "untrusted"],
        "class_quotas": {"trusted": 10, "sandboxed": 5, "untrusted": 3},
        "boundary_policy_audit_controls": True,
        "trust_reclassification_safe": True,
    }
    runtime = {
        "execution_pools_segmented": True,
        "class_quotas_isolation_enforced": True,
        "cross_class_leakage_blocked": True,
        "boundary_containment_tests_present": True,
        "dispatch_events": [
            {
                "event_id": "evt-01",
                "plugin_id": "plugin-a",
                "trust_class": "trusted",
                "pool_id": "trusted-pool-1",
                "resource_units": 4,
            },
            {
                "event_id": "evt-02",
                "plugin_id": "plugin-b",
                "trust_class": "sandboxed",
                "pool_id": "sandboxed-pool-1",
                "resource_units": 3,
            },
            {
                "event_id": "evt-03",
                "plugin_id": "plugin-c",
                "trust_class": "untrusted",
                "pool_id": "untrusted-pool-1",
                "resource_units": 1,
            },
        ],
        "reclassifications": [{"plugin_id": "plugin-b", "approved": True, "ticket": "CAB-127"}],
    }
    telemetry = {
        "trust_class_telemetry_present": True,
        "class_event_counts": {"trusted": 4, "sandboxed": 3, "untrusted": 1},
    }
    policy_path = tmp_path / "policy.json"
    runtime_path = tmp_path / "runtime.json"
    telemetry_path = tmp_path / "telemetry.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    runtime_path.write_text(json.dumps(runtime), encoding="utf-8")
    telemetry_path.write_text(json.dumps(telemetry), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/trust_bulkheads_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-12-ci",
            "--policy",
            str(policy_path),
            "--runtime",
            str(runtime_path),
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
    assert report["execution"]["events_processed"] == 3
    events_path = out_path.parent / "bulkhead_events.jsonl"
    assert events_path.is_file()
    assert history_path.read_text(encoding="utf-8").strip()

