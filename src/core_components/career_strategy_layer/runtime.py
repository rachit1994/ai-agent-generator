"""Deterministic career strategy layer derivation."""

from __future__ import annotations

import math
from typing import Any

from .contracts import CAREER_STRATEGY_LAYER_CONTRACT, CAREER_STRATEGY_LAYER_SCHEMA_VERSION


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def _score_or_zero(value: Any) -> float:
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, (int, float)):
        numeric = float(value)
        if not math.isfinite(numeric):
            return 0.0
        return _clamp01(numeric)
    return 0.0


def build_career_strategy_layer(
    *,
    run_id: str,
    mode: str,
    summary: dict[str, Any],
    review: dict[str, Any],
    promotion_package: dict[str, Any],
    capability_growth: dict[str, Any],
    transfer_learning: dict[str, Any],
    error_reduction: dict[str, Any],
    scalability_strategy: dict[str, Any],
) -> dict[str, Any]:
    capability_score = _score_or_zero(capability_growth.get("metrics", {}).get("capability_growth_rate", 0.0))
    transfer_score = _score_or_zero(transfer_learning.get("metrics", {}).get("transfer_efficiency_score", 0.0))
    error_reduction_rate = _score_or_zero(error_reduction.get("metrics", {}).get("error_reduction_rate", 0.0))
    scale_score = _score_or_zero(scalability_strategy.get("scores", {}).get("overall_scaling_score", 0.0))
    signal = _clamp01(
        0.35 * capability_score + 0.25 * transfer_score + 0.2 * error_reduction_rate + 0.2 * scale_score
    )
    review_pass = str(review.get("status", "")) == "completed_review_pass"
    validation_ready = summary.get("quality", {}).get("validation_ready") is True
    readiness = signal
    if not review_pass:
        readiness = max(0.0, readiness - 0.15)
    if not validation_ready:
        readiness = max(0.0, readiness - 0.1)
    readiness = _clamp01(readiness)
    risk = _clamp01(1.0 - readiness)
    proposed_stage = str(promotion_package.get("proposed_stage", ""))
    focus = "promotion" if proposed_stage and proposed_stage != "junior" else "stabilization"
    status = "hold"
    if readiness >= 0.75 and review_pass and validation_ready:
        status = "ready"
    elif readiness >= 0.55:
        status = "watchlist"
    actions = ["close_review_blockers", "raise_validation_ready", "stabilize_transfer_metrics"]
    return {
        "schema": CAREER_STRATEGY_LAYER_CONTRACT,
        "schema_version": CAREER_STRATEGY_LAYER_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "focus": focus,
        "horizon": "next_cycle",
        "strategy": {
            "career_signal_score": signal,
            "readiness_score": readiness,
            "risk_score": risk,
            "priority": "advance" if status == "ready" else "stabilize",
            "recommended_actions": actions,
        },
        "evidence": {
            "summary_ref": "summary.json",
            "review_ref": "review.json",
            "promotion_package_ref": "lifecycle/promotion_package.json",
            "career_strategy_ref": "strategy/career_strategy_layer.json",
        },
    }

