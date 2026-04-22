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


def _capability_score(skill_nodes: dict[str, Any]) -> float:
    nodes = skill_nodes.get("nodes") if isinstance(skill_nodes, dict) else []
    if not isinstance(nodes, list):
        return 0.0
    valid_scores = [
        float(node.get("score"))
        for node in nodes
        if isinstance(node, dict)
        and isinstance(node.get("score"), (int, float))
        and not isinstance(node.get("score"), bool)
    ]
    return _clamp01(max(valid_scores)) if valid_scores else 0.0


def _score_from_metrics(metrics_payload: dict[str, Any], score_key: str) -> float:
    scores = metrics_payload.get("scores") if isinstance(metrics_payload, dict) else {}
    if not isinstance(scores, dict):
        return 0.0
    value = scores.get(score_key)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return _clamp01(float(value))
    return 0.0


def _evaluate_failed_gates(*, eligible_examples: int, verifier_pass_rate: float, regression_rate: float, novelty_score: float, contradiction_rate: float) -> tuple[list[str], list[str]]:
    failed_gates: list[str] = []
    reason_codes: list[str] = []
    if eligible_examples < MIN_ELIGIBLE_EXAMPLES:
        failed_gates.append(GATE_ID_MIN_EXAMPLES)
        reason_codes.append("self_learning_loop_contract:gate_min_examples_unmet")
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
    return sorted(failed_gates, key=_gate_order), reason_codes


def _decision_from_failed_gates(failed_gates: list[str]) -> tuple[str, str]:
    hard_failure = GATE_ID_REGRESSION_RATE in failed_gates or GATE_ID_CONTRADICTION_RATE in failed_gates
    if not failed_gates:
        return "promote", "open_promotion_review"
    if hard_failure:
        return "reject", "halt_and_repair"
    return "hold", "run_practice_cycle"


def execute_self_learning_loop_runtime(
    *,
    events: list[dict[str, Any]],
    practice_engine: dict[str, Any],
    transfer_learning_metrics: dict[str, Any],
    capability_growth_metrics: dict[str, Any],
) -> dict[str, Any]:
    finalize_events = [row for row in events if isinstance(row, dict) and row.get("stage") == "finalize"]
    malformed_event_rows = len(events) - len([row for row in events if isinstance(row, dict)])
    missing_signal_sources: list[str] = []
    practice_scores = practice_engine.get("scores") if isinstance(practice_engine, dict) else None
    if not isinstance(practice_scores, dict) or "readiness_signal" not in practice_scores:
        missing_signal_sources.append("practice_engine")
    transfer_scores = transfer_learning_metrics.get("scores") if isinstance(transfer_learning_metrics, dict) else None
    if not isinstance(transfer_scores, dict) or "transfer_efficiency" not in transfer_scores:
        missing_signal_sources.append("transfer_learning_metrics")
    growth_scores = capability_growth_metrics.get("scores") if isinstance(capability_growth_metrics, dict) else None
    if not isinstance(growth_scores, dict) or "capability_growth_rate" not in growth_scores:
        missing_signal_sources.append("capability_growth_metrics")
    if len(finalize_events) == 0:
        missing_signal_sources.append("finalize_events")
    return {
        "events_processed": len(events),
        "finalize_events_processed": len(finalize_events),
        "malformed_event_rows": malformed_event_rows,
        "missing_signal_sources": missing_signal_sources,
    }


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
    execution = execute_self_learning_loop_runtime(
        events=events,
        practice_engine=practice_engine,
        transfer_learning_metrics=transfer_learning_metrics,
        capability_growth_metrics=capability_growth_metrics,
    )
    capability_score = _capability_score(skill_nodes)
    transfer_efficiency = _score_from_metrics(transfer_learning_metrics, "transfer_efficiency")
    growth_signal = _score_from_metrics(capability_growth_metrics, "capability_growth_rate")
    practice_readiness = _score_from_metrics(practice_engine, "readiness_signal")
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
    verifier_pass_rate = signals["finalize_pass_rate"]
    failed_gates, reason_codes = _evaluate_failed_gates(
        eligible_examples=eligible_examples,
        verifier_pass_rate=verifier_pass_rate,
        regression_rate=regression_rate,
        novelty_score=novelty_score,
        contradiction_rate=contradiction_rate,
    )
    decision, next_action = _decision_from_failed_gates(failed_gates)
    return {
        "schema": SELF_LEARNING_LOOP_CONTRACT,
        "schema_version": SELF_LEARNING_LOOP_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "execution": execution,
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
