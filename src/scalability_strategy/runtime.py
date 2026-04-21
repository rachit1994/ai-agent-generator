"""Deterministic scalability strategy derivation."""

from __future__ import annotations

from typing import Any

from .contracts import SCALABILITY_STRATEGY_CONTRACT, SCALABILITY_STRATEGY_SCHEMA_VERSION


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def build_scalability_strategy(
    *,
    run_id: str,
    mode: str,
    parsed: dict[str, Any],
    events: list[dict[str, Any]],
    cto: dict[str, Any],
) -> dict[str, Any]:
    checks = parsed.get("checks")
    if not isinstance(checks, list):
        checks = []
    total_checks = len(checks)
    pass_checks = sum(1 for row in checks if isinstance(row, dict) and row.get("passed") is True)
    event_scaling_score = _clamp01((pass_checks / total_checks) if total_checks else 0.0)
    finals = [row for row in events if isinstance(row, dict) and row.get("stage") == "finalize"]
    finalize_pass = 0
    retry_count = 0
    for row in finals:
        score = row.get("score")
        if isinstance(score, dict) and score.get("passed") is True:
            finalize_pass += 1
        retry = row.get("retry_count")
        if isinstance(retry, int) and not isinstance(retry, bool) and retry > 0:
            retry_count += 1
    finalize_rate = _clamp01((finalize_pass / len(finals)) if finals else 0.0)
    replay_scaling_score = _clamp01(1.0 - ((retry_count / len(finals)) if finals else 0.0))
    hard_stops = cto.get("hard_stops")
    hard_stop_failures = 0
    if isinstance(hard_stops, list):
        hard_stop_failures = sum(
            1 for row in hard_stops if isinstance(row, dict) and row.get("passed") is not True
        )
    balanced = cto.get("balanced_gates")
    balanced_ready = bool(isinstance(balanced, dict) and balanced.get("validation_ready") is True)
    memory_scaling_score = _clamp01(0.7 * finalize_rate + 0.3 * (1.0 if balanced_ready else 0.0))
    multi_agent_scaling_score = _clamp01(0.6 * replay_scaling_score + 0.4 * event_scaling_score)
    overall_scaling_score = _clamp01(
        0.3 * event_scaling_score
        + 0.2 * memory_scaling_score
        + 0.2 * replay_scaling_score
        + 0.3 * multi_agent_scaling_score
    )
    status = "scalable" if hard_stop_failures == 0 and overall_scaling_score >= 0.7 else "constrained"
    return {
        "schema": SCALABILITY_STRATEGY_CONTRACT,
        "schema_version": SCALABILITY_STRATEGY_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "scores": {
            "event_scaling_score": event_scaling_score,
            "memory_scaling_score": memory_scaling_score,
            "replay_scaling_score": replay_scaling_score,
            "multi_agent_scaling_score": multi_agent_scaling_score,
            "overall_scaling_score": overall_scaling_score,
        },
        "evidence": {
            "summary_ref": "summary.json",
            "review_ref": "review.json",
            "scalability_ref": "strategy/scalability_strategy.json",
        },
    }

