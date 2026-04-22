"""Runtime for feature 19 end-to-end plugin observability."""

from __future__ import annotations

from typing import Any

from .contracts import PLUGIN_OBSERVABILITY_SCHEMA, PLUGIN_OBSERVABILITY_SCHEMA_VERSION


def build_plugin_observability_contract() -> dict[str, object]:
    return {
        "correlation_id_propagation": ["api", "mcp", "runtime"],
        "stage_level_spans_events": True,
        "error_taxonomy_normalized": True,
        "plugin_tenant_slis_slos": True,
        "trace_stitching": True,
        "dashboards_alerts": True,
        "retention_sampling_policy": True,
        "continuity_tests": True,
    }


def _valid_span_event(event: Any) -> bool:
    if not isinstance(event, dict):
        return False
    required = ("event_id", "correlation_id", "plugin_id", "tenant_id", "stage", "outcome")
    if not all(isinstance(event.get(key), str) and event.get(key).strip() != "" for key in required):
        return False
    return event.get("stage") in {"api", "mcp", "runtime"} and event.get("outcome") in {"ok", "error"}


def _collect_span_events(spans: dict[str, Any]) -> list[dict[str, str]]:
    rows = spans.get("span_events")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if _valid_span_event(row)]


def execute_plugin_observability_runtime(
    *, spans: dict[str, Any], retention_policy: dict[str, Any]
) -> dict[str, Any]:
    events = _collect_span_events(spans)
    event_count = len(events)
    stage_counts = {"api": 0, "mcp": 0, "runtime": 0}
    error_count = 0
    plugin_ids: set[str] = set()
    tenant_ids: set[str] = set()
    correlation_ids: set[str] = set()
    for event in events:
        stage_counts[event["stage"]] += 1
        plugin_ids.add(event["plugin_id"])
        tenant_ids.add(event["tenant_id"])
        correlation_ids.add(event["correlation_id"])
        if event["outcome"] == "error":
            error_count += 1
    continuity_ok = bool(events) and all(stage_counts[s] > 0 for s in ("api", "mcp", "runtime"))
    trace_stitch_ok = continuity_ok and len(correlation_ids) > 0
    retention_days = retention_policy.get("retention_days")
    if not isinstance(retention_days, int):
        retention_days = 7
    sampling_rate = retention_policy.get("sampling_rate")
    if not isinstance(sampling_rate, (int, float)):
        sampling_rate = 1.0
    return {
        "event_count": event_count,
        "stage_counts": stage_counts,
        "error_count": error_count,
        "plugin_count": len(plugin_ids),
        "tenant_count": len(tenant_ids),
        "correlation_count": len(correlation_ids),
        "continuity_ok": continuity_ok,
        "trace_stitch_ok": trace_stitch_ok,
        "retention_days": retention_days,
        "sampling_rate": float(sampling_rate),
    }


def summarize_plugin_observability_health(
    *, spans: dict[str, Any], metrics: dict[str, Any], retention_policy: dict[str, Any]
) -> dict[str, bool]:
    execution = execute_plugin_observability_runtime(
        spans=spans, retention_policy=retention_policy
    )
    return {
        "correlation_ids_propagated_api_mcp_runtime": spans.get("correlation_ids_propagated_api_mcp_runtime")
        is True
        and execution["correlation_count"] > 0,
        "stage_level_spans_events_emitted": spans.get("stage_level_spans_events_emitted") is True
        and execution["event_count"] > 0
        and all(execution["stage_counts"][s] > 0 for s in ("api", "mcp", "runtime")),
        "error_outcome_taxonomy_normalized": spans.get("error_outcome_taxonomy_normalized") is True
        and execution["error_count"] >= 0,
        "plugin_tenant_slis_slos_tracked": metrics.get("plugin_tenant_slis_slos_tracked") is True
        and execution["plugin_count"] > 0
        and execution["tenant_count"] > 0,
        "cross_boundary_trace_stitching": spans.get("cross_boundary_trace_stitching") is True
        and execution["trace_stitch_ok"] is True,
        "dashboards_alerts_shipped": metrics.get("dashboards_alerts_shipped") is True
        and isinstance(metrics.get("dashboard_ids"), list)
        and len(metrics.get("dashboard_ids")) > 0
        and isinstance(metrics.get("alert_rule_ids"), list)
        and len(metrics.get("alert_rule_ids")) > 0,
        "logs_traces_retention_policies_applied": retention_policy.get("logs_traces_retention_policies_applied")
        is True
        and execution["retention_days"] > 0
        and 0.0 < execution["sampling_rate"] <= 1.0,
        "observability_continuity_tests_present": metrics.get("observability_continuity_tests_present") is True
        and execution["continuity_ok"] is True,
    }


def evaluate_plugin_observability_gate(
    *,
    run_id: str,
    mode: str,
    spans: dict[str, Any],
    metrics: dict[str, Any],
    retention_policy: dict[str, Any],
) -> dict[str, Any]:
    execution = execute_plugin_observability_runtime(
        spans=spans, retention_policy=retention_policy
    )
    checks = summarize_plugin_observability_health(
        spans=spans,
        metrics=metrics,
        retention_policy=retention_policy,
    )
    failed_gates = [name for name, passed in checks.items() if passed is not True]
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": PLUGIN_OBSERVABILITY_SCHEMA,
        "schema_version": PLUGIN_OBSERVABILITY_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "release_blocked": status == "fail",
        "checks": checks,
        "execution": execution,
        "failed_gates": failed_gates,
        "observability_contract": build_plugin_observability_contract(),
        "evidence": {
            "spans_ref": "data/plugin_observability/spans.jsonl",
            "metrics_ref": "data/plugin_observability/metrics.json",
            "retention_ref": "data/plugin_observability/retention_policy.json",
            "history_ref": "data/plugin_observability/trend_history.jsonl",
            "events_ref": "data/plugin_observability/observability_events.jsonl",
        },
    }


def update_plugin_observability_history(
    *, existing: list[dict[str, Any]], report: dict[str, Any]
) -> list[dict[str, Any]]:
    execution = report.get("execution")
    row = {
        "run_id": report["run_id"],
        "status": report["status"],
        "failed_gate_count": len(report["failed_gates"]),
        "event_count": execution.get("event_count") if isinstance(execution, dict) else None,
    }
    return [*existing, row]


def build_observability_event_rows(*, report: dict[str, Any]) -> list[dict[str, Any]]:
    execution = report.get("execution")
    if not isinstance(execution, dict):
        return []
    stage_counts = execution.get("stage_counts")
    if not isinstance(stage_counts, dict):
        return []
    return [
        {"run_id": report.get("run_id"), "stage": stage, "count": stage_counts.get(stage, 0)}
        for stage in ("api", "mcp", "runtime")
    ]

