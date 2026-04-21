"""Deterministic closure/security/reliability/scalability plan derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    CLOSURE_SECURITY_RELIABILITY_SCALABILITY_PLANS_CONTRACT,
    CLOSURE_SECURITY_RELIABILITY_SCALABILITY_PLANS_SCHEMA_VERSION,
)


def _plan_status(value: bool) -> str:
    return "ready" if value else "blocked"


def _is_true(value: Any) -> bool:
    return value is True


def build_closure_security_reliability_scalability_plans(
    *,
    run_id: str,
    mode: str,
    summary: dict[str, Any],
    review: dict[str, Any],
    readiness: dict[str, Any],
    scalability: dict[str, Any],
    boundaries: dict[str, Any],
    storage: dict[str, Any],
    policy_bundle_valid: bool,
) -> dict[str, Any]:
    review_pass = str(review.get("status", "")) == "completed_review_pass"
    validation_ready = _is_true(summary.get("quality", {}).get("validation_ready"))
    closure_ok = bool(readiness.get("status") == "ready" and review_pass and validation_ready)
    security_ok = bool(policy_bundle_valid and review_pass and validation_ready)
    reliability_metrics = summary.get("metrics", {}) if isinstance(summary.get("metrics"), dict) else {}
    reliability_ok = bool(
        (float(reliability_metrics.get("reliability", 0.0)) >= 0.8)
        and (float(reliability_metrics.get("retryFrequency", 1.0)) <= 0.4)
    )
    scalability_ok = bool(
        str(scalability.get("status", "")) == "scalable"
        and str(boundaries.get("status", "")) == "bounded"
        and str(storage.get("status", "")) == "consistent"
    )
    plans = {
        "closure": {"status": _plan_status(closure_ok), "ok": closure_ok},
        "security": {"status": _plan_status(security_ok), "ok": security_ok},
        "reliability": {
            "status": _plan_status(reliability_ok),
            "ok": reliability_ok,
            "metrics": {
                "pass_rate": float(reliability_metrics.get("passRate", 0.0)),
                "reliability": float(reliability_metrics.get("reliability", 0.0)),
                "retry_frequency": float(reliability_metrics.get("retryFrequency", 1.0)),
            },
        },
        "scalability": {"status": _plan_status(scalability_ok), "ok": scalability_ok},
    }
    ready_count = sum(1 for item in plans.values() if bool(item.get("ok")))
    status = "ready" if ready_count == 4 else "not_ready"
    return {
        "schema": CLOSURE_SECURITY_RELIABILITY_SCALABILITY_PLANS_CONTRACT,
        "schema_version": CLOSURE_SECURITY_RELIABILITY_SCALABILITY_PLANS_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "plans": plans,
        "summary": {"plans_ready": ready_count, "plans_total": 4, "overall_score": round(ready_count / 4.0, 4)},
        "evidence": {
            "summary_ref": "summary.json",
            "review_ref": "review.json",
            "readiness_ref": "program/production_readiness.json",
            "closure_plan_ref": "program/closure_security_reliability_scalability_plans.json",
        },
    }

