"""Composite balanced_gates scores and strict readiness."""

from __future__ import annotations

from typing import Any


def _to_float_or_zero(value: Any) -> float:
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        raw = value.strip()
        if raw == "":
            return 0.0
        try:
            return float(raw)
        except ValueError:
            return 0.0
    return 0.0


def _to_int_or_zero(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        raw = value.strip()
        if raw == "":
            return 0
        try:
            return int(float(raw))
        except ValueError:
            return 0
    return 0


def compute_balanced_gates(
    metrics: dict[str, Any],
    hard_stops: list[dict[str, Any]],
    *,
    review_status: str,
    manifest_complete: bool,
) -> dict[str, Any]:
    reliability = int(round(100 * _to_float_or_zero(metrics.get("reliability", 0))))
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
    reliability = _to_int_or_zero(balanced.get("reliability"))
    delivery = _to_int_or_zero(balanced.get("delivery"))
    governance = _to_int_or_zero(balanced.get("governance"))
    composite = _to_int_or_zero(balanced.get("composite"))
    if reliability < 85 or delivery < 85 or governance < 85:
        return False
    if composite < 90:
        return False
    return all(h.get("passed") for h in balanced.get("hard_stops", []))
