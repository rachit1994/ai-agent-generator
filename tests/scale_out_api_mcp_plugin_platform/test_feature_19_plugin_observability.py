from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_19_end_to_end_plugin_observability import (
    build_observability_event_rows,
    build_plugin_observability_contract,
    execute_plugin_observability_runtime,
    evaluate_plugin_observability_gate,
    update_plugin_observability_history,
    validate_plugin_observability_report_dict,
)


def _spans() -> dict[str, object]:
    return {
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


def _metrics() -> dict[str, object]:
    return {
        "plugin_tenant_slis_slos_tracked": True,
        "dashboards_alerts_shipped": True,
        "observability_continuity_tests_present": True,
        "dashboard_ids": ["dash-plugin-latency"],
        "alert_rule_ids": ["alert-plugin-errors"],
    }


def _retention() -> dict[str, object]:
    return {
        "logs_traces_retention_policies_applied": True,
        "retention_days": 14,
        "sampling_rate": 0.5,
    }


def test_plugin_observability_gate_passes_for_healthy_payloads() -> None:
    report = evaluate_plugin_observability_gate(
        run_id="run-feature-19-pass",
        mode="ci",
        spans=_spans(),
        metrics=_metrics(),
        retention_policy=_retention(),
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert report["execution"]["event_count"] == 3
    assert validate_plugin_observability_report_dict(report) == []


def test_plugin_observability_gate_fail_closes_on_correlation_gap() -> None:
    spans = _spans()
    spans["correlation_ids_propagated_api_mcp_runtime"] = False
    report = evaluate_plugin_observability_gate(
        run_id="run-feature-19-correlation-gap",
        mode="preflight",
        spans=spans,
        metrics=_metrics(),
        retention_policy=_retention(),
    )
    assert report["status"] == "fail"
    assert "correlation_ids_propagated_api_mcp_runtime" in report["failed_gates"]


def test_plugin_observability_gate_fail_closes_on_missing_runtime_stage() -> None:
    spans = _spans()
    spans["span_events"] = spans["span_events"][:2]
    report = evaluate_plugin_observability_gate(
        run_id="run-feature-19-missing-stage",
        mode="preflight",
        spans=spans,
        metrics=_metrics(),
        retention_policy=_retention(),
    )
    assert report["status"] == "fail"
    assert "stage_level_spans_events_emitted" in report["failed_gates"]


def test_execute_plugin_observability_runtime_counts_errors() -> None:
    execution = execute_plugin_observability_runtime(
        spans=_spans(),
        retention_policy=_retention(),
    )
    assert execution["error_count"] == 1


def test_build_observability_event_rows_from_report() -> None:
    report = evaluate_plugin_observability_gate(
        run_id="run-feature-19-events",
        mode="ci",
        spans=_spans(),
        metrics=_metrics(),
        retention_policy=_retention(),
    )
    rows = build_observability_event_rows(report=report)
    assert len(rows) == 3
    assert rows[0]["run_id"] == "run-feature-19-events"


def test_plugin_observability_contract_is_deterministic() -> None:
    assert build_plugin_observability_contract() == build_plugin_observability_contract()


def test_plugin_observability_history_appends_snapshot() -> None:
    report = evaluate_plugin_observability_gate(
        run_id="run-feature-19-history",
        mode="ci",
        spans=_spans(),
        metrics=_metrics(),
        retention_policy=_retention(),
    )
    history = update_plugin_observability_history(existing=[], report=report)
    assert len(history) == 1
    assert history[0]["run_id"] == "run-feature-19-history"
    assert history[0]["event_count"] == 3

