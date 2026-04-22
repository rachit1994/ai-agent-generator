from __future__ import annotations

import json
import subprocess


def test_cross_tenant_isolation_gate_script_passes_for_healthy_payloads(tmp_path) -> None:
    execution = {
        "tenant_identity_full_path": True,
        "tenant_id": "tenant-a",
        "tenant_budget_profile_id": "budget-standard-v1",
        "execution_events": [
            {
                "event_id": "evt-01",
                "tenant_id": "tenant-a",
                "plugin_id": "plugin-x",
                "queue_namespace": "tenant-a/queue",
                "storage_namespace": "tenant-a/storage",
                "cache_namespace": "tenant-a/cache",
                "key_scope": "tenant-a:key-v1",
            },
            {
                "event_id": "evt-02",
                "tenant_id": "tenant-a",
                "plugin_id": "plugin-y",
                "queue_namespace": "tenant-a/queue",
                "storage_namespace": "tenant-a/storage",
                "cache_namespace": "tenant-a/cache",
                "key_scope": "tenant-a:key-v1",
            },
        ],
        "adversarial_tests": [
            {"name": "cross-tenant-cache-poison", "result": "blocked"},
            {"name": "cross-tenant-queue-replay", "result": "blocked"},
        ],
    }
    isolation = {
        "tenant_id": "tenant-a",
        "tenant_budget_profile_id": "budget-standard-v1",
        "tenant_key_policy_version": "2026.04.1",
        "runtime_queue_storage_isolated": True,
        "cache_artifact_reuse_blocked": True,
        "tenant_keys_policy_controls_applied": True,
        "tenant_budgets_guardrails_enforced": True,
        "adversarial_leakage_tests_present": True,
    }
    audit = {
        "tenant_id": "tenant-a",
        "tenant_budget_profile_id": "budget-standard-v1",
        "tenant_key_policy_version": "2026.04.1",
        "continuous_isolation_audit_present": True,
        "incident_containment_actions_defined": True,
        "containment_actions": ["kill-tenant-workers", "revoke-tenant-keys"],
    }
    execution_path = tmp_path / "execution.json"
    isolation_path = tmp_path / "isolation.json"
    audit_path = tmp_path / "audit.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    execution_path.write_text(json.dumps(execution), encoding="utf-8")
    isolation_path.write_text(json.dumps(isolation), encoding="utf-8")
    audit_path.write_text(json.dumps(audit), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/cross_tenant_isolation_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-18-ci",
            "--execution",
            str(execution_path),
            "--isolation",
            str(isolation_path),
            "--audit",
            str(audit_path),
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
    assert report["execution"]["events_processed"] == 2
    events_path = out_path.parent / "isolation_events.jsonl"
    assert events_path.is_file()
    assert history_path.read_text(encoding="utf-8").strip()

