from __future__ import annotations

from scale_out_api_mcp_plugin_platform_features.feature_20_plugin_tenant_cost_attribution_caps import (
    build_cost_event_rows,
    build_cost_attribution_contract,
    evaluate_cost_attribution_gate,
    execute_cost_attribution_runtime,
    update_cost_attribution_history,
    validate_cost_attribution_report_dict,
)


def _metering() -> dict[str, object]:
    return {
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


def _aggregation() -> dict[str, object]:
    return {
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


def _caps() -> dict[str, object]:
    return {
        "hard_soft_caps_admission_enforced": True,
        "cap_breach_response_contracts_defined": True,
        "concurrency_cap_enforcement_tested": True,
        "soft_cap_usd": 250.0,
        "hard_cap_usd": 500.0,
        "cap_window_seconds": 300,
        "max_burst_requests": 200,
        "breach_action": "deny",
    }


def test_cost_attribution_gate_passes_for_healthy_payloads() -> None:
    report = evaluate_cost_attribution_gate(
        run_id="run-feature-20-pass",
        mode="ci",
        metering=_metering(),
        aggregation=_aggregation(),
        caps=_caps(),
    )
    assert report["status"] == "pass"
    assert report["release_blocked"] is False
    assert validate_cost_attribution_report_dict(report) == []


def test_cost_attribution_gate_fail_closes_on_cap_enforcement_gap() -> None:
    caps = _caps()
    caps["hard_soft_caps_admission_enforced"] = False
    report = evaluate_cost_attribution_gate(
        run_id="run-feature-20-cap-gap",
        mode="preflight",
        metering=_metering(),
        aggregation=_aggregation(),
        caps=caps,
    )
    assert report["status"] == "fail"
    assert "hard_soft_caps_admission_enforced" in report["failed_gates"]


def test_cost_attribution_gate_fail_closes_on_invalid_cap_ordering() -> None:
    caps = _caps()
    caps["soft_cap_usd"] = 700.0
    caps["hard_cap_usd"] = 500.0
    report = evaluate_cost_attribution_gate(
        run_id="run-feature-20-cap-order-invalid",
        mode="preflight",
        metering=_metering(),
        aggregation=_aggregation(),
        caps=caps,
    )
    assert report["status"] == "fail"
    assert "hard_soft_caps_admission_enforced" in report["failed_gates"]


def test_cost_attribution_gate_fail_closes_on_cap_window_under_aggregation_interval() -> None:
    caps = _caps()
    caps["cap_window_seconds"] = 30
    report = evaluate_cost_attribution_gate(
        run_id="run-feature-20-cap-window-too-small",
        mode="preflight",
        metering=_metering(),
        aggregation=_aggregation(),
        caps=caps,
    )
    assert report["status"] == "fail"
    assert "hard_soft_caps_admission_enforced" in report["failed_gates"]


def test_cost_attribution_gate_fail_closes_on_pricing_model_version_drift() -> None:
    aggregation = _aggregation()
    aggregation["pricing_model_version"] = "2026-05"
    report = evaluate_cost_attribution_gate(
        run_id="run-feature-20-pricing-model-drift",
        mode="preflight",
        metering=_metering(),
        aggregation=aggregation,
        caps=_caps(),
    )
    assert report["status"] == "fail"
    assert "normalized_cost_model_billable_units" in report["failed_gates"]


def test_cost_attribution_gate_fail_closes_on_staleness_budget_exceeding_cap_window() -> None:
    aggregation = _aggregation()
    caps = _caps()
    aggregation["staleness_budget_seconds"] = 600
    caps["cap_window_seconds"] = 300
    report = evaluate_cost_attribution_gate(
        run_id="run-feature-20-staleness-over-cap-window",
        mode="preflight",
        metering=_metering(),
        aggregation=aggregation,
        caps=caps,
    )
    assert report["status"] == "fail"
    assert "hard_soft_caps_admission_enforced" in report["failed_gates"]


def test_cost_attribution_gate_fail_closes_on_burst_limit_exceeding_cap_window() -> None:
    caps = _caps()
    caps["max_burst_requests"] = 400
    report = evaluate_cost_attribution_gate(
        run_id="run-feature-20-burst-limit-over-cap-window",
        mode="preflight",
        metering=_metering(),
        aggregation=_aggregation(),
        caps=caps,
    )
    assert report["status"] == "fail"
    assert "hard_soft_caps_admission_enforced" in report["failed_gates"]


def test_execute_cost_attribution_runtime_detects_cap_violation() -> None:
    metering = _metering()
    caps = _caps()
    caps["hard_cap_usd"] = 60.0
    caps["soft_cap_usd"] = 30.0
    metering["usage_events"][2]["status"] = "admitted"
    execution = execute_cost_attribution_runtime(
        metering=metering, aggregation=_aggregation(), caps=caps
    )
    assert "cost-evt-003" in execution["cap_violations"]


def test_cost_attribution_gate_fail_closes_on_billing_export_shape_gap() -> None:
    aggregation = _aggregation()
    aggregation["billing_exports"] = [{"tenant_id": "tenant-a"}]
    report = evaluate_cost_attribution_gate(
        run_id="run-feature-20-billing-export-shape-gap",
        mode="preflight",
        metering=_metering(),
        aggregation=aggregation,
        caps=_caps(),
    )
    assert report["status"] == "fail"
    assert "runtime_billing_exports_valid" in report["failed_gates"]


def test_cost_contract_is_deterministic() -> None:
    assert build_cost_attribution_contract() == build_cost_attribution_contract()


def test_cost_history_appends_snapshot() -> None:
    report = evaluate_cost_attribution_gate(
        run_id="run-feature-20-history",
        mode="ci",
        metering=_metering(),
        aggregation=_aggregation(),
        caps=_caps(),
    )
    history = update_cost_attribution_history(existing=[], report=report)
    assert len(history) == 1
    assert history[0]["run_id"] == "run-feature-20-history"
    assert history[0]["events_processed"] == 3


def test_build_cost_event_rows_contains_signals() -> None:
    report = evaluate_cost_attribution_gate(
        run_id="run-feature-20-events",
        mode="ci",
        metering=_metering(),
        aggregation=_aggregation(),
        caps=_caps(),
    )
    rows = build_cost_event_rows(report=report)
    assert len(rows) == 3

