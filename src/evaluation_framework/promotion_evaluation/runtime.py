"""Deterministic promotion-evaluation derivation."""

from __future__ import annotations

from typing import Any

from .contracts import PROMOTION_EVALUATION_CONTRACT, PROMOTION_EVALUATION_SCHEMA_VERSION


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def _finalize_pass_rate(events: list[dict[str, Any]]) -> float:
    finals = [row for row in events if isinstance(row, dict) and row.get("stage") == "finalize"]
    if not finals:
        return 0.0
    passed = 0
    for row in finals:
        score = row.get("score")
        if isinstance(score, dict) and bool(score.get("passed")):
            passed += 1
    return _clamp01(passed / len(finals))


def build_promotion_evaluation(
    *,
    run_id: str,
    promotion_package: dict[str, Any],
    review: dict[str, Any],
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    readiness = promotion_package.get("readiness") if isinstance(promotion_package, dict) else {}
    if not isinstance(readiness, dict):
        readiness = {}
    readiness_score = readiness.get("score")
    score = float(readiness_score) if isinstance(readiness_score, (int, float)) and not isinstance(readiness_score, bool) else 0.0
    finalize_rate = _finalize_pass_rate(events)
    review_pass = bool(review.get("status") == "completed_review_pass") if isinstance(review, dict) else False
    confidence = _clamp01((score * 0.6) + (finalize_rate * 0.4))
    decision = "promote" if review_pass and confidence >= 0.8 else "hold"
    return {
        "schema": PROMOTION_EVALUATION_CONTRACT,
        "schema_version": PROMOTION_EVALUATION_SCHEMA_VERSION,
        "run_id": run_id,
        "decision": decision,
        "confidence": confidence,
        "signals": {
            "promotion_readiness_score": _clamp01(score),
            "finalize_pass_rate": finalize_rate,
            "review_pass": review_pass,
        },
        "evidence": {
            "promotion_package_ref": "lifecycle/promotion_package.json",
            "review_ref": "review.json",
            "traces_ref": "traces.jsonl",
            "promotion_evaluation_ref": "learning/promotion_evaluation.json",
        },
    }
