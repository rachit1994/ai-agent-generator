from __future__ import annotations

import json
import subprocess


def test_sandbox_hardening_gate_script_passes_for_healthy_payloads(tmp_path) -> None:
    policy = {
        "default_egress": "deny",
        "egress_allowlist": ["api.openai.com", "storage.internal"],
        "max_timeout_ms": 60000,
        "startup_policy_validation_enforced": True,
        "policy_versioned_validated": True,
        "policy_version": "1.2.0",
        "syscall_allowlist": ["read", "write", "close"],
        "read_only_mounts": ["/usr", "/bin"],
        "syscall_default_action": "deny",
    }
    runtime = {
        "sandbox_isolation_runtime_present": True,
        "applied_policy_version": "1.2.0",
        "cpu_limit_millis": 1500,
        "memory_limit_mb": 512,
        "pid_limit": 128,
        "fd_limit": 512,
        "filesystem_syscall_restricted": True,
        "timeouts_hard_kill_enforced": True,
        "timeout_ms": 30000,
        "kill_signal": "SIGKILL",
        "escape_detection_kill_switch_enforced": True,
        "escape_exhaustion_tests_present": True,
        "runtime_events": [
            {
                "event_id": "rt-001",
                "type": "egress_attempt",
                "host": "malicious.example",
                "status": "denied",
                "timestamp": "2026-04-22T10:00:10Z",
            },
            {
                "event_id": "rt-002",
                "type": "resource_sample",
                "cpu_millis": 1200,
                "memory_mb": 420,
                "status": "ok",
                "timestamp": "2026-04-22T10:00:11Z",
            },
            {
                "event_id": "rt-003",
                "type": "escape_probe",
                "status": "denied",
                "timestamp": "2026-04-22T10:00:12Z",
            },
        ],
    }
    audit = {
        "denied_ops_count": 2,
        "denied_events": [
            {
                "event_id": "deny-001",
                "action": "network.connect",
                "reason": "egress_allowlist_violation",
                "timestamp": "2026-04-22T10:01:00Z",
            },
            {
                "event_id": "deny-002",
                "action": "syscall.unshare",
                "reason": "syscall_filtered",
                "timestamp": "2026-04-22T10:02:00Z",
            },
        ],
    }
    policy_path = tmp_path / "policy.json"
    runtime_path = tmp_path / "runtime.json"
    audit_path = tmp_path / "audit.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    runtime_path.write_text(json.dumps(runtime), encoding="utf-8")
    audit_path.write_text(json.dumps(audit), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/sandbox_hardening_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-13-ci",
            "--policy",
            str(policy_path),
            "--runtime",
            str(runtime_path),
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
    events_path = tmp_path / "runtime_events.jsonl"
    assert events_path.read_text(encoding="utf-8").strip()

