from __future__ import annotations

import json
import subprocess


def test_plugin_authz_gate_script_passes_for_healthy_payloads(tmp_path) -> None:
    taxonomy = {
        "scope_taxonomy_permission_model_defined": True,
        "policy_model_version": "2026.04",
        "scope_catalog": ["read:artifacts", "write:artifacts", "execute:tools"],
    }
    policy = {
        "least_privilege_policy_engine_implemented": True,
        "policy_model_version": "2026.04",
        "scope_checks_every_invocation": True,
        "deny_by_default_enforced": True,
        "policy_authoring_simulation_versioned": True,
        "escalation_scope_confusion_tests_present": True,
        "admin_policy_controls_present": True,
        "allowed_scopes_by_plugin": {
            "plugin-a": ["read:artifacts"],
            "plugin-b": ["read:artifacts", "execute:tools"],
        },
    }
    audit = {
        "allow_deny_decisions_audited": True,
        "allow_decisions": 1,
        "deny_decisions": 1,
        "total_decisions": 2,
        "decision_events": [
            {
                "event_id": "authz-evt-001",
                "plugin_id": "plugin-a",
                "scope": "read:artifacts",
                "decision": "allow",
            },
            {
                "event_id": "authz-evt-002",
                "plugin_id": "plugin-a",
                "scope": "write:artifacts",
                "decision": "deny",
            },
        ],
    }
    taxonomy_path = tmp_path / "taxonomy.json"
    policy_path = tmp_path / "policy.json"
    audit_path = tmp_path / "audit.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    taxonomy_path.write_text(json.dumps(taxonomy), encoding="utf-8")
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    audit_path.write_text(json.dumps(audit), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/plugin_authz_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-17-ci",
            "--taxonomy",
            str(taxonomy_path),
            "--policy",
            str(policy_path),
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
    assert history_path.read_text(encoding="utf-8").strip()
    events_path = tmp_path / "authz_events.jsonl"
    assert events_path.read_text(encoding="utf-8").strip()

