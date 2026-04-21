"""Deterministic core evaluation-service runtime derivation."""

from __future__ import annotations

from typing import Any

from .contracts import EVALUATION_SERVICE_CONTRACT, EVALUATION_SERVICE_SCHEMA_VERSION


def build_evaluation_service(
    *,
    run_id: str,
    summary: dict[str, Any],
    online_eval: dict[str, Any],
    promotion_eval: dict[str, Any],
) -> dict[str, Any]:
    has_online_eval = bool(online_eval)
    has_promotion_eval = bool(promotion_eval)
    summary_has_metrics = isinstance(summary.get("metrics"), dict)
    all_checks_passed = has_online_eval and has_promotion_eval and summary_has_metrics
    status = "ready" if all_checks_passed else "degraded"
    return {
        "schema": EVALUATION_SERVICE_CONTRACT,
        "schema_version": EVALUATION_SERVICE_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
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
