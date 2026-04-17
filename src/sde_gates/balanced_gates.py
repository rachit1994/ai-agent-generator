"""Composite balanced_gates scores and strict readiness."""

from __future__ import annotations

from typing import Any


def compute_balanced_gates(
    metrics: dict[str, Any],
    hard_stops: list[dict[str, Any]],
    *,
    review_status: str,
    manifest_complete: bool,
) -> dict[str, Any]:
    reliability = int(round(100 * float(metrics.get("reliability", 0))))
    reliability = max(0, min(100, reliability))
    delivery = 100 if review_status == "completed_review_pass" and manifest_complete else 70
    if review_status == "completed_review_fail":
        delivery = 60
    if review_status == "incomplete":
        delivery = 40
    governance = 100 if all(h.get("passed") for h in hard_stops) else 50
    governance = max(0, min(100, governance))
    composite = int(round((reliability + delivery + governance) / 3))
    return {
        "reliability": reliability,
        "delivery": delivery,
        "governance": governance,
        "composite": composite,
        "threshold_profile": "strict",
        "hard_stops": hard_stops,
    }


def validation_ready(balanced: dict[str, Any]) -> bool:
    if balanced["reliability"] < 85 or balanced["delivery"] < 85 or balanced["governance"] < 85:
        return False
    if balanced["composite"] < 90:
        return False
    return all(h.get("passed") for h in balanced.get("hard_stops", []))
