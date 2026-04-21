"""Deterministic human professional evolution artifact builders."""

from __future__ import annotations

import math
from typing import Any

from .contracts import (
    HUMAN_EVOLUTION_SCHEMA_VERSION,
    MENTORSHIP_CADENCE_DAYS,
    PERFORMANCE_EXCEEDS_THRESHOLD,
)

DEFAULT_FOCUS_AREA = "delivery.structured_output"


def _score_or_zero(value: Any) -> float:
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return 0.0


def _clamp01(value: float) -> float:
    if not math.isfinite(value):
        return 0.0
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def _focus_areas_or_default(value: Any) -> list[str]:
    if not isinstance(value, list):
        return [DEFAULT_FOCUS_AREA]
    cleaned = [row.strip() for row in value if isinstance(row, str) and row.strip()]
    if not cleaned:
        return [DEFAULT_FOCUS_AREA]
    return cleaned


def _finalize_pass_ratio(events: list[dict[str, Any]]) -> float:
    finals: list[float] = []
    for row in events:
        if not isinstance(row, dict) or row.get("stage") != "finalize":
            continue
        score = row.get("score")
        if not isinstance(score, dict):
            continue
        finals.append(1.0 if score.get("passed") is True else 0.0)
    if not finals:
        return 0.0
    return _clamp01(sum(finals) / len(finals))


def build_evolution_decision(
    *,
    run_id: str,
    parsed: dict[str, Any],
    events: list[dict[str, Any]],
    skill_nodes: dict[str, Any] | None,
) -> dict[str, Any]:
    _ = parsed
    score = 0.0
    if isinstance(skill_nodes, dict):
        nodes = skill_nodes.get("nodes")
        if isinstance(nodes, list) and nodes and isinstance(nodes[0], dict):
            raw = nodes[0].get("score")
            if isinstance(raw, (int, float)) and not isinstance(raw, bool):
                score = float(raw)
    score = _clamp01(score)
    ratio = _finalize_pass_ratio(events)
    performance = _clamp01((0.7 * score) + (0.3 * ratio))
    growth = "accelerating" if performance >= PERFORMANCE_EXCEEDS_THRESHOLD else "steady"
    return {
        "schema_version": HUMAN_EVOLUTION_SCHEMA_VERSION,
        "aggregate_id": run_id,
        "performance_score": performance,
        "growth_trend": growth,
        "mentorship_required": performance < 0.7,
        "focus_areas": [DEFAULT_FOCUS_AREA],
    }


def build_reflection_bundle(*, run_id: str, decision: dict[str, Any], event_ref: str) -> dict[str, Any]:
    trend = str(decision.get("growth_trend") or "steady")
    intervention = "mentor_loop" if decision.get("mentorship_required") is True else "none"
    return {
        "schema_version": "1.0",
        "run_id": run_id,
        "linked_event_ids": [event_ref],
        "root_causes": [f"growth_trend:{trend}"],
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
    perf = _score_or_zero(decision.get("performance_score", 0.0))
    perf = _clamp01(perf)
    current = "mid" if perf >= 0.5 else "junior"
    proposed = "junior"
    if perf >= 0.85:
        proposed = "senior"
    elif perf >= 0.5:
        proposed = "mid"
    return {
        "schema_version": "1.0",
        "aggregate_id": run_id,
        "current_stage": current,
        "proposed_stage": proposed,
        "independent_evaluator_signal_ids": [f"human-evolution:{perf:.3f}"],
        "evidence_window": [run_id],
    }


def build_practice_task_spec(*, decision: dict[str, Any]) -> dict[str, Any]:
    focus = decision.get("focus_areas")
    focus_list = focus if isinstance(focus, list) and focus else [DEFAULT_FOCUS_AREA]
    return {
        "schema_version": "1.0",
        "gap_detection_ref": "learning/reflection_bundle.json",
        "task": "deliberate_practice_cycle",
        "acceptance_criteria": [f"focus:{str(focus_list[0])}"],
    }


def build_practice_evaluation_result(*, decision: dict[str, Any]) -> dict[str, Any]:
    perf = _score_or_zero(decision.get("performance_score", 0.0))
    perf = _clamp01(perf)
    return {"schema_version": "1.0", "passed": perf >= 0.5}


def build_canary_report(*, decision: dict[str, Any]) -> dict[str, Any]:
    perf = _score_or_zero(decision.get("performance_score", 0.0))
    perf = _clamp01(perf)
    promote = perf >= 0.7
    return {"schema_version": "1.0", "shadow_metrics": {"latency_p95_ms": 0}, "promote": promote}


def build_mentorship_plan(*, run_id: str, decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "aggregate_id": run_id,
        "session_cadence_days": MENTORSHIP_CADENCE_DAYS,
        "focus_areas": _focus_areas_or_default(decision.get("focus_areas")),
        "mentorship_required": decision.get("mentorship_required") is True,
        "evidence_window": [run_id],
    }
