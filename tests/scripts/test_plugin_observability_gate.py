from __future__ import annotations

import json
import subprocess


def test_plugin_observability_gate_script_passes_for_healthy_payloads(tmp_path) -> None:
    spans = {
        "correlation_ids_propagated_api_mcp_runtime": True,
        "stage_level_spans_events_emitted": True,
        "error_outcome_taxonomy_normalized": True,
        "cross_boundary_trace_stitching": True,
        "span_events": [
            {
                "event_id": "evt-01",
                "correlation_id": "corr-1",
                "plugin_id": "plugin-x",
                "tenant_id": "tenant-a",
                "stage": "api",
                "outcome": "ok",
            },
            {
                "event_id": "evt-02",
                "correlation_id": "corr-1",
                "plugin_id": "plugin-x",
                "tenant_id": "tenant-a",
                "stage": "mcp",
                "outcome": "ok",
            },
            {
                "event_id": "evt-03",
                "correlation_id": "corr-1",
                "plugin_id": "plugin-x",
                "tenant_id": "tenant-a",
                "stage": "runtime",
                "outcome": "error",
            },
        ],
    }
    metrics = {
        "plugin_tenant_slis_slos_tracked": True,
        "dashboards_alerts_shipped": True,
        "observability_continuity_tests_present": True,
        "dashboard_ids": ["dash-plugin-latency"],
        "alert_rule_ids": ["alert-plugin-errors"],
    }
    retention = {
        "logs_traces_retention_policies_applied": True,
        "retention_days": 14,
        "sampling_rate": 0.5,
    }
    spans_path = tmp_path / "spans.json"
    metrics_path = tmp_path / "metrics.json"
    retention_path = tmp_path / "retention.json"
    out_path = tmp_path / "report.json"
    history_path = tmp_path / "trend_history.jsonl"
    spans_path.write_text(json.dumps(spans), encoding="utf-8")
    metrics_path.write_text(json.dumps(metrics), encoding="utf-8")
    retention_path.write_text(json.dumps(retention), encoding="utf-8")
    result = subprocess.run(
        [
            "python",
            "scripts/plugin_observability_gate.py",
            "--mode",
            "ci",
            "--run-id",
            "run-feature-19-ci",
            "--spans",
            str(spans_path),
            "--metrics",
            str(metrics_path),
            "--retention",
            str(retention_path),
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
    assert report["execution"]["event_count"] == 3
    events_path = out_path.parent / "observability_events.jsonl"
    assert events_path.is_file()
    assert history_path.read_text(encoding="utf-8").strip()

