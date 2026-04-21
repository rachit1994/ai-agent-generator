"""Deterministic strategy overlay derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    STRATEGY_OVERLAY_RUNTIME_CONTRACT,
    STRATEGY_OVERLAY_RUNTIME_SCHEMA_VERSION,
)


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def _finalize_pass(events: list[dict[str, Any]]) -> bool:
    for row in events:
        if not isinstance(row, dict):
            continue
        if row.get("stage") != "finalize":
            continue
        score = row.get("score")
        if isinstance(score, dict):
            return bool(score.get("passed"))
    return False


def build_strategy_overlay_runtime(
    *,
    run_id: str,
    mode: str,
    proposal: dict[str, Any],
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    promotion_required = bool(proposal.get("requires_promotion_package"))
    autonomy_applied = bool(proposal.get("applied_autonomy"))
    finalize_passed = _finalize_pass(events)
    strategy_name = "hold"
    confidence = 0.4
    rationale = "insufficient_delivery_signal"
    if finalize_passed and promotion_required and not autonomy_applied:
        strategy_name = "stabilize"
        confidence = 0.75
        rationale = "promotion_guarded_progress"
    if finalize_passed and not promotion_required and autonomy_applied:
        strategy_name = "accelerate"
        confidence = 0.9
        rationale = "autonomy_path_clear"
    return {
        "schema": STRATEGY_OVERLAY_RUNTIME_CONTRACT,
        "schema_version": STRATEGY_OVERLAY_RUNTIME_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "strategy_name": strategy_name,
        "confidence": _clamp01(confidence),
        "rationale": rationale,
        "gates": {
            "promotion_required": promotion_required,
            "autonomy_applied": autonomy_applied,
            "finalize_passed": finalize_passed,
        },
        "evidence": {
            "proposal_ref": "strategy/proposal.json",
            "overlay_ref": "strategy/overlay.json",
            "traces_ref": "traces.jsonl",
        },
    }
