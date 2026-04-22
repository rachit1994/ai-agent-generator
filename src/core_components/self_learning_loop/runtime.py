"""Deterministic self-learning loop derivation."""

from __future__ import annotations

from typing import Any

from .contracts import SELF_LEARNING_LOOP_CONTRACT, SELF_LEARNING_LOOP_SCHEMA_VERSION
from .policy_defaults import (
    GATE_ID_CONTRADICTION_RATE,
    GATE_ID_MIN_EXAMPLES,
    GATE_ID_NOVELTY_SCORE,
    GATE_ID_REGRESSION_RATE,
    GATE_ID_VERIFIER_PASS_RATE,
    MANDATORY_GATE_IDS,
    MAX_CONTRADICTION_RATE,
    MAX_REGRESSION_RATE,
    MIN_ELIGIBLE_EXAMPLES,
    MIN_NOVELTY_SCORE,
    MIN_VERIFIER_PASS_RATE,
)


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
        if isinstance(score, dict) and score.get("passed") is True:
            passed += 1
    return _clamp01(passed / len(finals))


def _gate_order(gate_id: str) -> int:
    return MANDATORY_GATE_IDS.index(gate_id) if gate_id in MANDATORY_GATE_IDS else len(MANDATORY_GATE_IDS)


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
    if isinstance(nodes, list):
        valid_scores = [
            float(node.get("score"))
            for node in nodes
            if isinstance(node, dict)
            and isinstance(node.get("score"), (int, float))
            and not isinstance(node.get("score"), bool)
        ]
        if valid_scores:
            capability_score = _clamp01(max(valid_scores))
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
    eligible_examples = len([row for row in events if isinstance(row, dict)])
    regression_rate = _clamp01(1.0 - practice_readiness)
    novelty_score = _clamp01((transfer_efficiency + growth_signal) / 2.0)
    contradiction_rate = _clamp01(abs(capability_score - practice_readiness))
    signals = {
        "finalize_pass_rate": _finalize_pass_rate(events),
        "capability_score": capability_score,
        "transfer_efficiency": transfer_efficiency,
        "growth_signal": growth_signal,
        "practice_readiness": practice_readiness,
    }
    failed_gates: list[str] = []
    reason_codes: list[str] = []
    if eligible_examples < MIN_ELIGIBLE_EXAMPLES:
        failed_gates.append(GATE_ID_MIN_EXAMPLES)
        reason_codes.append("self_learning_loop_contract:gate_min_examples_unmet")
    verifier_pass_rate = signals["finalize_pass_rate"]
    if verifier_pass_rate < MIN_VERIFIER_PASS_RATE:
        failed_gates.append(GATE_ID_VERIFIER_PASS_RATE)
        reason_codes.append("self_learning_loop_contract:gate_verifier_pass_rate_below_threshold")
    if regression_rate > MAX_REGRESSION_RATE:
        failed_gates.append(GATE_ID_REGRESSION_RATE)
        reason_codes.append("self_learning_loop_contract:gate_regression_rate_exceeded")
    if novelty_score < MIN_NOVELTY_SCORE:
        failed_gates.append(GATE_ID_NOVELTY_SCORE)
        reason_codes.append("self_learning_loop_contract:gate_novelty_score_below_threshold")
    if contradiction_rate > MAX_CONTRADICTION_RATE:
        failed_gates.append(GATE_ID_CONTRADICTION_RATE)
        reason_codes.append("self_learning_loop_contract:gate_contradiction_rate_exceeded")
    failed_gates = sorted(failed_gates, key=_gate_order)
    hard_failure = GATE_ID_REGRESSION_RATE in failed_gates or GATE_ID_CONTRADICTION_RATE in failed_gates
    decision = "promote"
    next_action = "open_promotion_review"
    if failed_gates:
        decision = "reject" if hard_failure else "hold"
        next_action = "run_practice_cycle" if decision == "hold" else "halt_and_repair"
    return {
        "schema": SELF_LEARNING_LOOP_CONTRACT,
        "schema_version": SELF_LEARNING_LOOP_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "signals": signals,
        "decision": {
            "decision": decision,
            "loop_state": decision,
            "failed_gates": failed_gates,
            "decision_reasons": reason_codes,
            "next_action": next_action,
            "primary_reason": reason_codes[0] if reason_codes else "self_learning_loop_contract:all_gates_passed",
        },
        "evidence": {
            "traces_ref": "traces.jsonl",
            "skill_nodes_ref": "capability/skill_nodes.json",
            "practice_engine_ref": "practice/practice_engine.json",
            "transfer_learning_metrics_ref": "learning/transfer_learning_metrics.json",
            "capability_growth_metrics_ref": "learning/capability_growth_metrics.json",
            "self_learning_candidates_ref": "learning/self_learning_candidates.jsonl",
            "self_learning_loop_ref": "learning/self_learning_loop.json",
        },
    }
