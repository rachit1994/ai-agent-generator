from __future__ import annotations

import json
import subprocess


def test_cost_attribution_gate_script_passes_for_healthy_payloads(tmp_path) -> None:
    metering = {
        "plugin_tenant_metering_pipeline": True,
        "normalized_cost_model_billable_units": True,
        "plugin_id_field": "plugin_id",
        "tenant_id_field": "tenant_id",
        "billable_unit": "token",
        "unit_scale": 1000,
        "pricing_model_version": "2026-04",
        "usage_events": [
            {
                "event_id": "cost-evt-001",
                "tenant_id": "tenant-a",
                "plugin_id": "plugin-x",
                "units": 180000,
                "estimated_cost_usd": 120.0,
                "status": "admitted",
            },
            {
                "event_id": "cost-evt-002",
                "tenant_id": "tenant-a",
                "plugin_id": "plugin-y",
                "units": 140000,
                "estimated_cost_usd": 90.0,
                "status": "admitted",
            },
            {
                "event_id": "cost-evt-003",
                "tenant_id": "tenant-b",
                "plugin_id": "plugin-y",
                "units": 110000,
                "estimated_cost_usd": 70.0,
                "status": "denied",
            },
        ],
    }
    aggregation = {
        "near_realtime_attribution_aggregation": True,
        "cost_reports_audit_exports_generated": True,
        "cost_anomaly_burn_rate_detected": True,
        "aggregation_interval_seconds": 60,
        "staleness_budget_seconds": 120,
        "pricing_model_version": "2026-04",
        "billing_exports": [
            {"tenant_id": "tenant-a", "cost_usd": 210.0},
            {"tenant_id": "tenant-b", "cost_usd": 70.0},
        ],
    }
    caps = {
        "hard_soft_caps_admission_enforced": True,
        "cap_breach_response_contracts_defined": True,
        "concurrency_cap_enforcement_tested": True,
        "soft_cap_usd": 250.0,
        "hard_cap_usd": 500.0,
        "cap_window_seconds": 300,
        "max_burst_requests": 200,
        "breach_action": "deny",
    }
    metering_path = tmp_path / "metering.json"
    aggregation_path = tmp_path / "aggregation.json"
    caps_path = tmp_path / "caps.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    metering_path.write_text(json.dumps(metering), encoding="utf-8")
    aggregation_path.write_text(json.dumps(aggregation), encoding="utf-8")
    caps_path.write_text(json.dumps(caps), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/cost_attribution_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-20-ci",
            "--metering",
            str(metering_path),
            "--aggregation",
            str(aggregation_path),
            "--caps",
            str(caps_path),
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
    events_path = tmp_path / "cost_events.jsonl"
    assert events_path.read_text(encoding="utf-8").strip()

