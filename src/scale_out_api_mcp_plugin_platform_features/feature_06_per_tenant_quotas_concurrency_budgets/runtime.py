"""Runtime for feature 06 tenant quotas and concurrency budgets."""

from __future__ import annotations

from typing import Any

from .contracts import TENANT_QUOTA_SCHEMA, TENANT_QUOTA_SCHEMA_VERSION


def build_tenant_quota_contract() -> dict[str, object]:
    return {
        "tenant_identity_required": True,
        "quota_storage": "durable",
        "concurrency_ceiling": "hard_limit",
        "fairness_policy": "weighted_round_robin",
        "quota_refill_window": "fixed_interval",
        "admin_controls": ["set_quota", "set_concurrency", "set_refill_window"],
    }


def _valid_rejection_reasons(scheduler_state: dict[str, Any]) -> bool:
    reasons = scheduler_state.get("rejection_reason_codes")
    if not isinstance(reasons, list) or not reasons:
        return False
    seen: set[str] = set()
    for reason in reasons:
        if not isinstance(reason, str) or not reason.strip():
            return False
        if reason in seen:
            return False
        seen.add(reason)
    return True


def _rejection_reasons_observable(scheduler_state: dict[str, Any], observability: dict[str, Any]) -> bool:
    scheduler_reasons = scheduler_state.get("rejection_reason_codes")
    observable_reasons = observability.get("tracked_rejection_reason_codes")
    return (
        isinstance(scheduler_reasons, list)
        and isinstance(observable_reasons, list)
        and sorted(scheduler_reasons) == sorted(observable_reasons)
    )


def _policy_version_aligned(
    quota_state: dict[str, Any], scheduler_state: dict[str, Any], observability: dict[str, Any]
) -> bool:
    quota_policy_version = quota_state.get("quota_policy_version")
    scheduler_policy_version = scheduler_state.get("quota_policy_version")
    observability_policy_version = observability.get("quota_policy_version")
    return (
        isinstance(quota_policy_version, str)
        and quota_policy_version.strip() != ""
        and quota_policy_version == scheduler_policy_version
        and quota_policy_version == observability_policy_version
    )


def _refill_window_aligned(
    quota_state: dict[str, Any], scheduler_state: dict[str, Any], observability: dict[str, Any]
) -> bool:
    quota_refill_window_seconds = quota_state.get("refill_window_seconds")
    scheduler_refill_window_seconds = scheduler_state.get("refill_window_seconds")
    observability_refill_window_seconds = observability.get("refill_window_seconds")
    return (
        isinstance(quota_refill_window_seconds, int)
        and quota_refill_window_seconds > 0
        and quota_refill_window_seconds == scheduler_refill_window_seconds
        and quota_refill_window_seconds == observability_refill_window_seconds
    )


def _tenant_scope_aligned(
    quota_state: dict[str, Any], scheduler_state: dict[str, Any], observability: dict[str, Any]
) -> bool:
    quota_tenant_scope = quota_state.get("tenant_scope")
    scheduler_tenant_scope = scheduler_state.get("tenant_scope")
    observability_tenant_scope = observability.get("tenant_scope")
    return (
        isinstance(quota_tenant_scope, str)
        and quota_tenant_scope.strip() != ""
        and quota_tenant_scope == scheduler_tenant_scope
        and quota_tenant_scope == observability_tenant_scope
    )


def _valid_admission_event(event: Any) -> bool:
    if not isinstance(event, dict):
        return False
    required = ("event_id", "tenant_id", "requested_slots", "status")
    if not all(key in event for key in required):
        return False
    if not isinstance(event.get("tenant_id"), str) or not event.get("tenant_id").strip():
        return False
    if not isinstance(event.get("requested_slots"), int) or event.get("requested_slots") <= 0:
        return False
    return event.get("status") in {"admitted", "rejected"}


def _collect_admission_events(scheduler_state: dict[str, Any]) -> list[dict[str, Any]]:
    events = scheduler_state.get("admission_events")
    if not isinstance(events, list):
        return []
    return [event for event in events if _valid_admission_event(event)]


def _quota_limits_for_tenant(
    *, tenant: str, quota_state: dict[str, Any], policy_scope: Any
) -> tuple[int | None, int | None, bool]:
    if isinstance(policy_scope, str) and tenant != policy_scope:
        return None, None, False
    limits = quota_state.get("tenant_limits")
    usage = quota_state.get("tenant_usage")
    tenant_limit = limits.get(tenant) if isinstance(limits, dict) else None
    tenant_usage = usage.get(tenant) if isinstance(usage, dict) else None
    return tenant_limit, tenant_usage, True


def _apply_admission_event(
    *,
    event: dict[str, Any],
    quota_state: dict[str, Any],
    policy_scope: Any,
    cap_violations: list[str],
    missing_reason_violations: list[str],
) -> int:
    tenant = event["tenant_id"]
    tenant_limit, tenant_usage, in_scope = _quota_limits_for_tenant(
        tenant=tenant, quota_state=quota_state, policy_scope=policy_scope
    )
    if not in_scope or not isinstance(tenant_limit, int) or not isinstance(tenant_usage, int):
        cap_violations.append(event["event_id"])
        return 0
    would_exceed = tenant_usage + event["requested_slots"] > tenant_limit
    if would_exceed and event["status"] == "admitted":
        cap_violations.append(event["event_id"])
    if event["status"] != "rejected":
        return 0
    reason = event.get("reason_code")
    if not isinstance(reason, str) or not reason.strip():
        missing_reason_violations.append(event["event_id"])
    return 1


def execute_tenant_quota_runtime(
    *, quota_state: dict[str, Any], scheduler_state: dict[str, Any], observability: dict[str, Any]
) -> dict[str, Any]:
    events = _collect_admission_events(scheduler_state)
    policy_scope = quota_state.get("tenant_scope")
    cap_violations: list[str] = []
    missing_reason_violations: list[str] = []
    observed_rejections = 0
    for event in events:
        observed_rejections += _apply_admission_event(
            event=event,
            quota_state=quota_state,
            policy_scope=policy_scope,
            cap_violations=cap_violations,
            missing_reason_violations=missing_reason_violations,
        )
    tracked_rejections = observability.get("rejection_count")
    rejection_count_coherent = isinstance(tracked_rejections, int) and tracked_rejections == observed_rejections
    return {
        "events_processed": len(events),
        "cap_violations": cap_violations,
        "missing_reason_violations": missing_reason_violations,
        "rejection_count_coherent": rejection_count_coherent,
    }


def summarize_tenant_budget_health(
    *, quota_state: dict[str, Any], scheduler_state: dict[str, Any], observability: dict[str, Any]
) -> dict[str, bool]:
    execution = execute_tenant_quota_runtime(
        quota_state=quota_state, scheduler_state=scheduler_state, observability=observability
    )
    return {
        "tenant_identity_threaded": quota_state.get("tenant_identity_threaded") is True
        and _tenant_scope_aligned(quota_state, scheduler_state, observability),
        "durable_quota_state": quota_state.get("durable_quota_state") is True,
        "hard_limit_enforced": scheduler_state.get("hard_limit_enforced") is True,
        "fairness_policy_enforced": scheduler_state.get("fairness_policy_enforced") is True,
        "refill_window_supported": quota_state.get("refill_window_supported") is True
        and _refill_window_aligned(quota_state, scheduler_state, observability),
        "rejection_reasons_present": scheduler_state.get("rejection_reasons_present") is True
        and _valid_rejection_reasons(scheduler_state),
        "tenant_observability_present": observability.get("tenant_observability_present") is True
        and _rejection_reasons_observable(scheduler_state, observability),
        "admin_controls_present": quota_state.get("admin_controls_present") is True
        and _policy_version_aligned(quota_state, scheduler_state, observability),
        "runtime_cap_enforcement_consistent": len(execution["cap_violations"]) == 0,
        "runtime_rejection_reasons_complete": len(execution["missing_reason_violations"]) == 0,
        "runtime_rejection_metrics_coherent": execution["rejection_count_coherent"] is True,
    }


def evaluate_tenant_quota_gate(
    *,
    run_id: str,
    mode: str,
    quota_state: dict[str, Any],
    scheduler_state: dict[str, Any],
    observability: dict[str, Any],
) -> dict[str, Any]:
    execution = execute_tenant_quota_runtime(
        quota_state=quota_state, scheduler_state=scheduler_state, observability=observability
    )
    checks = summarize_tenant_budget_health(
        quota_state=quota_state,
        scheduler_state=scheduler_state,
        observability=observability,
    )
    failed_gates = [name for name, passed in checks.items() if passed is not True]
    status = "pass" if not failed_gates else "fail"
    return {
        "schema": TENANT_QUOTA_SCHEMA,
        "schema_version": TENANT_QUOTA_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "release_blocked": status == "fail",
        "checks": checks,
        "execution": execution,
        "failed_gates": failed_gates,
        "quota_contract": build_tenant_quota_contract(),
        "evidence": {
            "quota_ref": "data/tenant_quotas/quota_state.json",
            "scheduler_ref": "data/tenant_quotas/scheduler_state.json",
            "observability_ref": "data/tenant_quotas/observability.json",
            "history_ref": "data/tenant_quotas/trend_history.jsonl",
            "events_ref": "data/tenant_quotas/quota_events.jsonl",
        },
    }


def update_tenant_quota_history(*, existing: list[dict[str, Any]], report: dict[str, Any]) -> list[dict[str, Any]]:
    execution = report.get("execution")
    row = {
        "run_id": report["run_id"],
        "status": report["status"],
        "failed_gate_count": len(report["failed_gates"]),
        "events_processed": execution.get("events_processed") if isinstance(execution, dict) else None,
    }
    return [*existing, row]


def build_quota_event_rows(*, report: dict[str, Any]) -> list[dict[str, Any]]:
    execution = report.get("execution")
    if not isinstance(execution, dict):
        return []
    run_id = report.get("run_id")
    return [
        {"run_id": run_id, "signal": "events_processed", "value": execution.get("events_processed", 0)},
        {"run_id": run_id, "signal": "cap_violations", "value": len(execution.get("cap_violations", []))},
        {
            "run_id": run_id,
            "signal": "missing_reason_violations",
            "value": len(execution.get("missing_reason_violations", [])),
        },
    ]

