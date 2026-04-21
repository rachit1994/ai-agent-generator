"""Deterministic regression-testing-surface runtime derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    REGRESSION_TESTING_SURFACE_CONTRACT,
    REGRESSION_TESTING_SURFACE_SCHEMA_VERSION,
)


def build_regression_testing_surface(
    *,
    run_id: str,
    anchor_errors: list[str],
    promotion_evaluation: dict[str, Any],
    online_evaluation: dict[str, Any],
    summary: dict[str, Any],
) -> dict[str, Any]:
    anchor_validation_passed = len(anchor_errors) == 0
    has_promotion_eval = bool(promotion_evaluation)
    has_online_eval = bool(online_evaluation)
    has_eval_summary = isinstance(summary.get("metrics"), dict)
    all_checks = anchor_validation_passed and has_promotion_eval and has_online_eval and has_eval_summary
    status = "ready" if all_checks else "degraded"
    return {
        "schema": REGRESSION_TESTING_SURFACE_CONTRACT,
        "schema_version": REGRESSION_TESTING_SURFACE_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "metrics": {
            "anchor_validation_passed": anchor_validation_passed,
            "has_promotion_eval": has_promotion_eval,
            "has_online_eval": has_online_eval,
            "has_eval_summary": has_eval_summary,
        },
        "anchor_validation_errors": list(anchor_errors),
        "evidence": {
            "promotion_evaluation_ref": "learning/promotion_evaluation.json",
            "online_evaluation_ref": "learning/online_evaluation_shadow_canary.json",
            "summary_ref": "summary.json",
            "surface_ref": "learning/regression_testing_surface.json",
        },
    }
