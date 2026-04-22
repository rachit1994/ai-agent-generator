"""Deterministic core evaluation-service runtime derivation."""

from __future__ import annotations

from typing import Any

from .contracts import EVALUATION_SERVICE_CONTRACT, EVALUATION_SERVICE_SCHEMA_VERSION


def _has_eval_signal(payload: dict[str, Any]) -> bool:
    status = payload.get("status")
    if isinstance(status, str) and bool(status.strip()):
        return True
    decision = payload.get("decision")
    return isinstance(decision, str) and decision in {"promote", "hold"}


def execute_evaluation_service_runtime(
    *,
    summary: dict[str, Any],
    online_eval: dict[str, Any],
    promotion_eval: dict[str, Any],
) -> dict[str, Any]:
    missing_signal_sources: list[str] = []
    if not _has_eval_signal(online_eval):
        missing_signal_sources.append("online_eval")
    if not _has_eval_signal(promotion_eval):
        missing_signal_sources.append("promotion_eval")
    summary_metrics_present = isinstance(summary.get("metrics"), dict)
    malformed_payloads = 0
    for payload in (summary, online_eval, promotion_eval):
        if not isinstance(payload, dict):
            malformed_payloads += 1
    return {
        "payloads_processed": 3,
        "missing_signal_sources": missing_signal_sources,
        "summary_metrics_present": summary_metrics_present,
        "malformed_payloads": malformed_payloads,
    }


def build_evaluation_service(
    *,
    run_id: str,
    summary: dict[str, Any],
    online_eval: dict[str, Any],
    promotion_eval: dict[str, Any],
) -> dict[str, Any]:
    execution = execute_evaluation_service_runtime(
        summary=summary, online_eval=online_eval, promotion_eval=promotion_eval
    )
    has_online_eval = _has_eval_signal(online_eval) if isinstance(online_eval, dict) else False
    has_promotion_eval = _has_eval_signal(promotion_eval) if isinstance(promotion_eval, dict) else False
    summary_has_metrics = isinstance(summary.get("metrics"), dict)
    all_checks_passed = has_online_eval and has_promotion_eval and summary_has_metrics
    status = "ready" if all_checks_passed else "degraded"
    return {
        "schema": EVALUATION_SERVICE_CONTRACT,
        "schema_version": EVALUATION_SERVICE_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "execution": execution,
        "metrics": {
            "has_online_eval": has_online_eval,
            "has_promotion_eval": has_promotion_eval,
            "summary_has_metrics": summary_has_metrics,
            "all_checks_passed": all_checks_passed,
        },
        "evidence": {
            "summary_ref": "summary.json",
            "online_eval_ref": "learning/online_evaluation_shadow_canary.json",
            "promotion_eval_ref": "learning/promotion_evaluation.json",
            "evaluation_service_ref": "evaluation/service_runtime.json",
        },
    }
