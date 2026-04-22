"""Runtime for feature 20 per-plugin/per-tenant cost attribution and caps."""

from __future__ import annotations

from typing import Any

from .contracts import COST_ATTRIBUTION_SCHEMA, COST_ATTRIBUTION_SCHEMA_VERSION


def build_cost_attribution_contract() -> dict[str, object]:
    return {
        "metering_pipeline": ["per_plugin", "per_tenant", "normalized_units"],
        "near_realtime_aggregation": True,
        "hard_soft_caps": True,
        "admission_cap_enforcement": True,
        "cap_breach_response_contracts": True,
        "cost_reports_audit_exports": True,
        "anomaly_burn_rate_detection": True,
        "concurrency_cap_tests": True,
    }


def _valid_metering_shape(metering: dict[str, Any]) -> bool:
    return (
        isinstance(metering.get("plugin_id_field"), str)
        and metering.get("plugin_id_field").strip() != ""
        and isinstance(metering.get("tenant_id_field"), str)
        and metering.get("tenant_id_field").strip() != ""
        and isinstance(metering.get("billable_unit"), str)
        and metering.get("billable_unit").strip() != ""
        and isinstance(metering.get("unit_scale"), int)
        and metering.get("unit_scale") > 0
    )


def _valid_aggregation_shape(aggregation: dict[str, Any]) -> bool:
    interval_seconds = aggregation.get("aggregation_interval_seconds")
    staleness_budget_seconds = aggregation.get("staleness_budget_seconds")
    return (
        isinstance(interval_seconds, int)
        and interval_seconds > 0
        and isinstance(staleness_budget_seconds, int)
        and staleness_budget_seconds >= interval_seconds
    )


def _valid_caps_shape(caps: dict[str, Any]) -> bool:
    soft_cap_usd = caps.get("soft_cap_usd")
    hard_cap_usd = caps.get("hard_cap_usd")
    return (
        isinstance(soft_cap_usd, (int, float))
        and soft_cap_usd > 0
        and isinstance(hard_cap_usd, (int, float))
        and hard_cap_usd >= soft_cap_usd
        and caps.get("breach_action") in {"deny", "throttle"}
    )


def _caps_aggregation_coherence(aggregation: dict[str, Any], caps: dict[str, Any]) -> bool:
    interval_seconds = aggregation.get("aggregation_interval_seconds")
    cap_window_seconds = caps.get("cap_window_seconds")
    return (
        isinstance(interval_seconds, int)
        and interval_seconds > 0
        and isinstance(cap_window_seconds, int)
        and cap_window_seconds >= interval_seconds
    )


def _pricing_model_aligned(metering: dict[str, Any], aggregation: dict[str, Any]) -> bool:
    metering_version = metering.get("pricing_model_version")
    aggregation_version = aggregation.get("pricing_model_version")
    return (
        isinstance(metering_version, str)
        and metering_version.strip() != ""
        and metering_version == aggregation_version
    )


def _staleness_within_cap_window(aggregation: dict[str, Any], caps: dict[str, Any]) -> bool:
    staleness_budget_seconds = aggregation.get("staleness_budget_seconds")
    cap_window_seconds = caps.get("cap_window_seconds")
    return (
        isinstance(staleness_budget_seconds, int)
        and staleness_budget_seconds >= 0
        and isinstance(cap_window_seconds, int)
        and cap_window_seconds > 0
        and staleness_budget_seconds <= cap_window_seconds
    )


def _valid_burst_limit(caps: dict[str, Any]) -> bool:
    max_burst_requests = caps.get("max_burst_requests")
    cap_window_seconds = caps.get("cap_window_seconds")
    return (
        isinstance(max_burst_requests, int)
        and max_burst_requests > 0
        and isinstance(cap_window_seconds, int)
        and cap_window_seconds > 0
        and max_burst_requests <= cap_window_seconds
    )


def _valid_usage_event(event: Any) -> bool:
    if not isinstance(event, dict):
        return False
    required = ("event_id", "tenant_id", "plugin_id", "units", "estimated_cost_usd", "status")
    if not all(key in event for key in required):
        return False
    if not isinstance(event.get("tenant_id"), str) or not event.get("tenant_id").strip():
        return False
    if not isinstance(event.get("plugin_id"), str) or not event.get("plugin_id").strip():
        return False
    if not isinstance(event.get("units"), int) or event.get("units") <= 0:
        return False
    if not isinstance(event.get("estimated_cost_usd"), (int, float)) or event.get("estimated_cost_usd") <= 0:
        return False
    return event.get("status") in {"admitted", "throttled", "denied"}


def _collect_usage_events(metering: dict[str, Any]) -> list[dict[str, Any]]:
    events = metering.get("usage_events")
    if not isinstance(events, list):
        return []
    return [event for event in events if _valid_usage_event(event)]


def _apply_usage_event(
    *,
    event: dict[str, Any],
    tenant_totals: dict[str, float],
    plugin_totals: dict[str, float],
    cap_violations: list[str],
    hard_cap: float,
    breach_action: Any,
) -> None:
    tenant_id = event["tenant_id"]
    plugin_id = event["plugin_id"]
    cost = float(event["estimated_cost_usd"])
    tenant_totals[tenant_id] = tenant_totals.get(tenant_id, 0.0) + cost
    plugin_totals[plugin_id] = plugin_totals.get(plugin_id, 0.0) + cost
    if tenant_totals[tenant_id] > hard_cap and event["status"] == "admitted":
        cap_violations.append(event["event_id"])
    if event["status"] == "denied" and breach_action != "deny":
        cap_violations.append(event["event_id"])


def _billing_export_violations(aggregation: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    exports = aggregation.get("billing_exports")
    if not isinstance(exports, list) or not exports:
        return ["billing_exports_missing"]
    for row in exports:
        if not isinstance(row, dict):
            violations.append("billing_export_row_invalid")
            continue
        if not isinstance(row.get("tenant_id"), str) or not isinstance(row.get("cost_usd"), (int, float)):
            violations.append("billing_export_row_invalid")
    return violations


def execute_cost_attribution_runtime(
    *, metering: dict[str, Any], aggregation: dict[str, Any], caps: dict[str, Any]
) -> dict[str, Any]:
    events = _collect_usage_events(metering)
    tenant_totals: dict[str, float] = {}
    plugin_totals: dict[str, float] = {}
    cap_violations: list[str] = []
    hard_cap = float(caps.get("hard_cap_usd", 0.0)) if isinstance(caps.get("hard_cap_usd"), (int, float)) else 0.0
    breach_action = caps.get("breach_action")
    for event in events:
        _apply_usage_event(
            event=event,
            tenant_totals=tenant_totals,
            plugin_totals=plugin_totals,
            cap_violations=cap_violations,
            hard_cap=hard_cap,
            breach_action=breach_action,
        )
    billing_export_violations = _billing_export_violations(aggregation)
    return {
        "events_processed": len(events),
        "tenant_totals": tenant_totals,
        "plugin_totals": plugin_totals,
        "cap_violations": cap_violations,
        "billing_export_violations": billing_export_violations,
    }


def summarize_cost_attribution_health(
    *, metering: dict[str, Any], aggregation: dict[str, Any], caps: dict[str, Any]
) -> dict[str, bool]:
    execution = execute_cost_attribution_runtime(metering=metering, aggregation=aggregation, caps=caps)
    return {
        "plugin_tenant_metering_pipeline": metering.get("plugin_tenant_metering_pipeline") is True
        and _valid_metering_shape(metering),
        "normalized_cost_model_billable_units": metering.get("normalized_cost_model_billable_units") is True
        and isinstance(metering.get("pricing_model_version"), str)
        and metering.get("pricing_model_version").strip() != ""
        and _pricing_model_aligned(metering, aggregation),
        "near_realtime_attribution_aggregation": aggregation.get("near_realtime_attribution_aggregation")
        is True
        and _valid_aggregation_shape(aggregation),
        "hard_soft_caps_admission_enforced": caps.get("hard_soft_caps_admission_enforced") is True
        and _valid_caps_shape(caps)
        and _caps_aggregation_coherence(aggregation, caps)
        and _staleness_within_cap_window(aggregation, caps)
        and _valid_burst_limit(caps),
        "cap_breach_response_contracts_defined": caps.get("cap_breach_response_contracts_defined") is True,
        "cost_reports_audit_exports_generated": aggregation.get("cost_reports_audit_exports_generated") is True,
        "cost_anomaly_burn_rate_detected": aggregation.get("cost_anomaly_burn_rate_detected") is True,
        "concurrency_cap_enforcement_tested": caps.get("concurrency_cap_enforcement_tested") is True,
        "runtime_cap_enforcement_consistent": len(execution["cap_violations"]) == 0,
        "runtime_billing_exports_valid": len(execution["billing_export_violations"]) == 0,
    }


def evaluate_cost_attribution_gate(
    *,
    run_id: str,
    mode: str,
    metering: dict[str, Any],
    aggregation: dict[str, Any],
    caps: dict[str, Any],
) -> dict[str, Any]:
    execution = execute_cost_attribution_runtime(metering=metering, aggregation=aggregation, caps=caps)
    checks = summarize_cost_attribution_health(metering=metering, aggregation=aggregation, caps=caps)
    failed_gates = [name for name, passed in checks.items() if passed is not True]
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": COST_ATTRIBUTION_SCHEMA,
        "schema_version": COST_ATTRIBUTION_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "release_blocked": status == "fail",
        "checks": checks,
        "execution": execution,
        "failed_gates": failed_gates,
        "cost_contract": build_cost_attribution_contract(),
        "evidence": {
            "metering_ref": "data/cost_attribution/metering.json",
            "aggregation_ref": "data/cost_attribution/aggregation.json",
            "caps_ref": "data/cost_attribution/caps.json",
            "history_ref": "data/cost_attribution/trend_history.jsonl",
            "events_ref": "data/cost_attribution/cost_events.jsonl",
        },
    }


def update_cost_attribution_history(
    *, existing: list[dict[str, Any]], report: dict[str, Any]
) -> list[dict[str, Any]]:
    execution = report.get("execution")
    row = {
        "run_id": report["run_id"],
        "status": report["status"],
        "failed_gate_count": len(report["failed_gates"]),
        "events_processed": execution.get("events_processed") if isinstance(execution, dict) else None,
    }
    return [*existing, row]


def build_cost_event_rows(*, report: dict[str, Any]) -> list[dict[str, Any]]:
    execution = report.get("execution")
    if not isinstance(execution, dict):
        return []
    run_id = report.get("run_id")
    return [
        {"run_id": run_id, "signal": "events_processed", "value": execution.get("events_processed", 0)},
        {"run_id": run_id, "signal": "cap_violations", "value": len(execution.get("cap_violations", []))},
        {
            "run_id": run_id,
            "signal": "billing_export_violations",
            "value": len(execution.get("billing_export_violations", [])),
        },
    ]

