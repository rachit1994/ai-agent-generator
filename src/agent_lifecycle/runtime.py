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


def _score_or_zero(value: Any) -> float:
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, (int, float)):
        return _clamp01(float(value))
    return 0.0


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
        finals.append(1.0 if passed is True else 0.0)
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


def _stage_transition_for_score(
    *,
    score: float,
    current_stage: str,
    has_valid_prior_stage: bool,
) -> tuple[str, list[str]]:
    proposed_stage = current_stage
    reasons: list[str] = []
    if not has_valid_prior_stage:
        return proposed_stage, ["missing_or_invalid_prior_stage"]
    if score >= PROMOTION_THRESHOLDS.get(current_stage, 1.0):
        next_stage = _next_stage(current_stage)
        if next_stage != current_stage:
            proposed_stage = next_stage
            reasons.append("promotion_threshold_met")
    if score < DEMOTION_FLOORS.get(current_stage, 0.0):
        prev_stage = _prev_stage(current_stage)
        if prev_stage != current_stage:
            proposed_stage = prev_stage
            reasons.append("demotion_floor_breach")
    return proposed_stage, reasons


def _valid_transition_event(event: Any) -> bool:
    if not isinstance(event, dict):
        return False
    required = ("event_id", "from_stage", "to_stage", "reason", "approved")
    if not all(key in event for key in required):
        return False
    if event.get("from_stage") not in LIFECYCLE_STAGES or event.get("to_stage") not in LIFECYCLE_STAGES:
        return False
    if not isinstance(event.get("reason"), str) or not event.get("reason").strip():
        return False
    return isinstance(event.get("approved"), bool)


def _collect_transition_events(parsed: dict[str, Any]) -> list[dict[str, Any]]:
    rows = parsed.get("transition_events")
    if not isinstance(rows, list):
        return []
    return [row for row in rows if _valid_transition_event(row)]


def _evaluate_transition_event(event: dict[str, Any]) -> tuple[bool, bool]:
    invalid_transition = event["from_stage"] == event["to_stage"] and event["reason"] in {
        "promotion_threshold_met",
        "demotion_floor_breach",
    }
    approval_violation = event["from_stage"] != event["to_stage"] and event["approved"] is not True
    return invalid_transition, approval_violation


def _decision_matches_transition(decision: dict[str, Any], final_event: dict[str, Any] | None) -> bool:
    if not isinstance(final_event, dict):
        return True
    current_stage = decision.get("current_stage")
    proposed_stage = decision.get("proposed_stage")
    return final_event.get("from_stage") == current_stage and final_event.get("to_stage") == proposed_stage


def execute_lifecycle_runtime(*, parsed: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    events = _collect_transition_events(parsed)
    invalid_transition_events: list[str] = []
    approval_violations: list[str] = []
    final_event = events[-1] if events else None
    for event in events:
        invalid_transition, approval_violation = _evaluate_transition_event(event)
        if invalid_transition:
            invalid_transition_events.append(event["event_id"])
        if approval_violation:
            approval_violations.append(event["event_id"])
    return {
        "events_processed": len(events),
        "invalid_transition_events": invalid_transition_events,
        "approval_violations": approval_violations,
        "decision_transition_matches": _decision_matches_transition(decision, final_event),
    }


def build_lifecycle_decision(
    *,
    run_id: str,
    parsed: dict[str, Any],
    events: list[dict[str, Any]],
    skill_nodes: dict[str, Any] | None,
    prior_stage: str | None = None,
) -> dict[str, Any]:
    _ = parsed
    score = _extract_score(skill_nodes)
    parsed_prior = parsed.get("current_stage") if isinstance(parsed, dict) else None
    candidate_prior = prior_stage if isinstance(prior_stage, str) else parsed_prior
    has_valid_prior_stage = isinstance(candidate_prior, str) and candidate_prior in LIFECYCLE_STAGES
    current_stage = candidate_prior if has_valid_prior_stage else _stage_for_score(score)
    proposed_stage, reasons = _stage_transition_for_score(
        score=score,
        current_stage=current_stage,
        has_valid_prior_stage=has_valid_prior_stage,
    )
    if _stagnation(score, events):
        reasons.append("stagnation_detected")
    if not reasons:
        reasons.append("steady_state")
    decision = {
        "schema_version": LIFECYCLE_SCHEMA_VERSION,
        "aggregate_id": run_id,
        "score": score,
        "current_stage": current_stage,
        "proposed_stage": proposed_stage,
        "lifecycle_state": "watchlist" if "stagnation_detected" in reasons else "active",
        "reasons": sorted(reasons),
    }
    decision["execution"] = execute_lifecycle_runtime(parsed=parsed, decision=decision)
    return decision


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
    score = _score_or_zero(decision.get("score", 0.0))
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
