"""Deterministic self-learning loop derivation."""

from __future__ import annotations

from typing import Any

from .contracts import SELF_LEARNING_LOOP_CONTRACT, SELF_LEARNING_LOOP_SCHEMA_VERSION


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


def build_self_learning_loop(
    *,
    run_id: str,
    mode: str,
    events: list[dict[str, Any]],
    practice_engine: dict[str, Any],
    transfer_learning_metrics: dict[str, Any],
    capability_growth_metrics: dict[str, Any],
    skill_nodes: dict[str, Any],
) -> dict[str, Any]:
    capability_score = 0.0
    nodes = skill_nodes.get("nodes") if isinstance(skill_nodes, dict) else []
    if isinstance(nodes, list) and nodes and isinstance(nodes[0], dict):
        score = nodes[0].get("score")
        if isinstance(score, (int, float)) and not isinstance(score, bool):
            capability_score = _clamp01(float(score))
    transfer_efficiency = 0.0
    transfer_scores = (
        transfer_learning_metrics.get("scores")
        if isinstance(transfer_learning_metrics, dict)
        else {}
    )
    if isinstance(transfer_scores, dict):
        value = transfer_scores.get("transfer_efficiency")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            transfer_efficiency = _clamp01(float(value))
    growth_signal = 0.0
    growth_scores = (
        capability_growth_metrics.get("scores")
        if isinstance(capability_growth_metrics, dict)
        else {}
    )
    if isinstance(growth_scores, dict):
        value = growth_scores.get("capability_growth_rate")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            growth_signal = _clamp01(float(value))
    practice_readiness = 0.0
    practice_scores = practice_engine.get("scores") if isinstance(practice_engine, dict) else {}
    if isinstance(practice_scores, dict):
        value = practice_scores.get("readiness_signal")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            practice_readiness = _clamp01(float(value))
    signals = {
        "finalize_pass_rate": _finalize_pass_rate(events),
        "capability_score": capability_score,
        "transfer_efficiency": transfer_efficiency,
        "growth_signal": growth_signal,
        "practice_readiness": practice_readiness,
    }
    state = "hold"
    next_action = "run_practice_cycle"
    reason = "gate_blocked"
    if (
        signals["finalize_pass_rate"] >= 0.85
        and signals["capability_score"] >= 0.75
        and signals["practice_readiness"] >= 0.6
    ):
        state = "iterate"
        next_action = "targeted_improvement_cycle"
        reason = "progress_detected"
    if (
        signals["finalize_pass_rate"] >= 0.95
        and signals["capability_score"] >= 0.85
        and signals["transfer_efficiency"] >= 0.75
        and signals["growth_signal"] >= 0.65
        and signals["practice_readiness"] >= 0.8
    ):
        state = "promote"
        next_action = "open_promotion_review"
        reason = "promotion_ready"
    return {
        "schema": SELF_LEARNING_LOOP_CONTRACT,
        "schema_version": SELF_LEARNING_LOOP_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "signals": signals,
        "decision": {
            "loop_state": state,
            "next_action": next_action,
            "primary_reason": reason,
        },
        "evidence": {
            "traces_ref": "traces.jsonl",
            "skill_nodes_ref": "capability/skill_nodes.json",
            "practice_engine_ref": "practice/practice_engine.json",
            "transfer_learning_metrics_ref": "learning/transfer_learning_metrics.json",
            "capability_growth_metrics_ref": "learning/capability_growth_metrics.json",
            "self_learning_loop_ref": "learning/self_learning_loop.json",
        },
    }
