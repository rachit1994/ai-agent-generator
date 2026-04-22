from __future__ import annotations

import json
import subprocess


def test_idempotency_gate_script_passes(tmp_path) -> None:
    api_state = {
        "invocation_path_idempotency": True,
        "idempotency_key": "idem-tenant-a-order-42",
        "api_key_validation_replay_semantics": True,
        "replay_status": "hit",
        "conflict_response_semantics": True,
        "conflict_code": "IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_PAYLOAD",
    }
    ledger_state = {
        "global_dedupe_ledger_services_plugins": True,
        "ledger_partition": "tenant-a:plugin-orders",
        "concurrent_duplicate_write_safety": True,
        "dedupe_lock_held_ms": 18,
        "ttl_replay_policy": True,
        "ttl_seconds": 86400,
    }
    side_effects_state = {
        "external_side_effect_deduplication_outbox": True,
        "outbox_events": ["evt-1001"],
        "idempotency_metrics_alerts": True,
        "metrics": {"hits": 24, "misses": 8, "conflicts": 1, "total_requests": 33},
    }
    api_path = tmp_path / "api.json"
    ledger_path = tmp_path / "ledger.json"
    effects_path = tmp_path / "effects.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    api_path.write_text(json.dumps(api_state), encoding="utf-8")
    ledger_path.write_text(json.dumps(ledger_state), encoding="utf-8")
    effects_path.write_text(json.dumps(side_effects_state), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/idempotency_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-07-ci",
            "--api",
            str(api_path),
            "--ledger",
            str(ledger_path),
            "--effects",
            str(effects_path),
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
