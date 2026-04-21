"""Deterministic local capability model runtime."""

from __future__ import annotations

from typing import Any

from .contracts import CAPABILITY_SCHEMA_VERSION


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
        return _clamp01(float(value))
    return 0.0


def _finalize_passed(events: list[dict[str, Any]]) -> bool:
    finals = [row for row in events if isinstance(row, dict) and row.get("stage") == "finalize"]
    if not finals:
        return False
    score = finals[-1].get("score")
    return isinstance(score, dict) and score.get("passed") is True


def _check_pass_ratio(parsed: dict[str, Any]) -> float:
    checks = parsed.get("checks")
    if not isinstance(checks, list) or not checks:
        return 0.0
    good = 0
    total = 0
    for row in checks:
        if not isinstance(row, dict) or "passed" not in row:
            continue
        total += 1
        passed = row.get("passed")
        good += 1 if isinstance(passed, bool) and passed else 0
    if total == 0:
        return 0.0
    return _clamp01(good / total)


def build_skill_nodes(
    *, run_id: str, parsed: dict[str, Any], events: list[dict[str, Any]]
) -> dict[str, Any]:
    check_ratio = _check_pass_ratio(parsed)
    finalize_ok = 1.0 if _finalize_passed(events) else 0.0
    refusal = parsed.get("refusal")
    refusal_penalty = 0.2 if isinstance(refusal, dict) else 0.0
    score = _clamp01((0.7 * check_ratio) + (0.3 * finalize_ok) - refusal_penalty)
    confidence = _clamp01((0.5 * check_ratio) + (0.5 * finalize_ok))
    return {
        "schema_version": CAPABILITY_SCHEMA_VERSION,
        "nodes": [
            {
                "skill_id": "delivery.structured_output",
                "score": score,
                "confidence": confidence,
                "evidence_ref": f"evt-{run_id}-traces",
            }
        ],
    }


def build_promotion_package(
    *,
    run_id: str,
    parsed: dict[str, Any],
    events: list[dict[str, Any]],
    skill_nodes: dict[str, Any],
) -> dict[str, Any]:
    _ = parsed
    _ = events
    nodes = skill_nodes.get("nodes") if isinstance(skill_nodes, dict) else None
    node = nodes[0] if isinstance(nodes, list) and nodes and isinstance(nodes[0], dict) else {}
    score = _score_or_zero(node.get("score", 0.0))
    if score >= 0.9:
        current_stage = "senior"
        proposed_stage = "architect"
    elif score >= 0.7:
        current_stage = "mid"
        proposed_stage = "senior"
    elif score >= 0.5:
        current_stage = "junior"
        proposed_stage = "mid"
    else:
        current_stage = "junior"
        proposed_stage = "junior"
    return {
        "schema_version": "1.0",
        "aggregate_id": run_id,
        "current_stage": current_stage,
        "proposed_stage": proposed_stage,
        "independent_evaluator_signal_ids": [f"capability-score:{score:.3f}"],
        "evidence_window": [run_id],
    }

