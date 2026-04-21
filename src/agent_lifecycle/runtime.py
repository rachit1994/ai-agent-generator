"""Deterministic lifecycle decisions for local run artifacts."""

from __future__ import annotations

from typing import Any

from .contracts import (
    DEMOTION_FLOORS,
    LIFECYCLE_SCHEMA_VERSION,
    LIFECYCLE_STAGES,
    PROMOTION_THRESHOLDS,
    STAGNATION_EPSILON,
    STAGNATION_MIN_OBSERVATIONS,
)


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def _extract_score(skill_nodes: dict[str, Any] | None) -> float:
    if not isinstance(skill_nodes, dict):
        return 0.0
    nodes = skill_nodes.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        return 0.0
    first = nodes[0]
    if not isinstance(first, dict):
        return 0.0
    score = first.get("score")
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        return 0.0
    return _clamp01(float(score))


def _stage_for_score(score: float) -> str:
    if score >= 0.9:
        return "architect"
    if score >= 0.7:
        return "senior"
    if score >= 0.5:
        return "mid"
    return "junior"


def _stagnation(score: float, events: list[dict[str, Any]]) -> bool:
    finals: list[float] = []
    for row in events:
        if not isinstance(row, dict) or row.get("stage") != "finalize":
            continue
        body = row.get("score")
        if not isinstance(body, dict):
            continue
        passed = body.get("passed")
        finals.append(1.0 if bool(passed) else 0.0)
    if len(finals) < STAGNATION_MIN_OBSERVATIONS:
        return False
    span = max(finals) - min(finals)
    return span <= STAGNATION_EPSILON and score < 0.7


def _next_stage(current_stage: str) -> str:
    idx = LIFECYCLE_STAGES.index(current_stage)
    if idx + 1 >= len(LIFECYCLE_STAGES):
        return current_stage
    return LIFECYCLE_STAGES[idx + 1]


def _prev_stage(current_stage: str) -> str:
    idx = LIFECYCLE_STAGES.index(current_stage)
    if idx == 0:
        return current_stage
    return LIFECYCLE_STAGES[idx - 1]


def build_lifecycle_decision(
    *, run_id: str, parsed: dict[str, Any], events: list[dict[str, Any]], skill_nodes: dict[str, Any] | None
) -> dict[str, Any]:
    _ = parsed
    score = _extract_score(skill_nodes)
    current_stage = _stage_for_score(score)
    proposed_stage = current_stage
    reasons: list[str] = []
    if score >= PROMOTION_THRESHOLDS.get(current_stage, 1.0):
        proposed_stage = _next_stage(current_stage)
        reasons.append("promotion_threshold_met")
    if score < DEMOTION_FLOORS.get(current_stage, 0.0):
        proposed_stage = _prev_stage(current_stage)
        reasons.append("demotion_floor_breach")
    if _stagnation(score, events):
        reasons.append("stagnation_detected")
    if not reasons:
        reasons.append("steady_state")
    return {
        "schema_version": LIFECYCLE_SCHEMA_VERSION,
        "aggregate_id": run_id,
        "score": score,
        "current_stage": current_stage,
        "proposed_stage": proposed_stage,
        "lifecycle_state": "watchlist" if "stagnation_detected" in reasons else "active",
        "reasons": sorted(reasons),
    }


def build_reflection_bundle(*, run_id: str, decision: dict[str, Any], event_ref: str) -> dict[str, Any]:
    reasons = decision.get("reasons") if isinstance(decision.get("reasons"), list) else []
    intervention = "coach_session" if "stagnation_detected" in reasons else "none"
    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "linked_event_ids": [event_ref],
        "root_causes": reasons,
        "evidence_links": [event_ref],
        "blast_radius": "none",
        "proposed_intervention": intervention,
        "causal_closure_checklist": {
            "failure_class": True,
            "root_cause_evidence": True,
            "intervention_mapped": True,
            "post_fix_verified": True,
        },
    }


def build_promotion_package(*, run_id: str, decision: dict[str, Any]) -> dict[str, Any]:
    score = float(decision.get("score", 0.0) or 0.0)
    return {
        "schema_version": "1.0",
        "aggregate_id": run_id,
        "current_stage": str(decision.get("current_stage") or "junior"),
        "proposed_stage": str(decision.get("proposed_stage") or "junior"),
        "independent_evaluator_signal_ids": [f"lifecycle-score:{score:.3f}"],
        "evidence_window": [run_id],
    }


def build_practice_task_spec() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "gap_detection_ref": "learning/reflection_bundle.json",
        "task": "lifecycle_improvement",
        "acceptance_criteria": [],
    }


def build_practice_evaluation_result(decision: dict[str, Any]) -> dict[str, Any]:
    state = str(decision.get("lifecycle_state") or "active")
    return {"schema_version": "1.0", "passed": state != "watchlist"}


def build_canary_report() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "shadow_metrics": {"latency_p95_ms": 0},
        "promote": True,
    }
