from __future__ import annotations

from human_professional_evolution_model import (
    build_evolution_decision,
    build_mentorship_plan,
    build_practice_evaluation_result,
    build_reflection_bundle,
)


def test_build_evolution_decision_is_deterministic() -> None:
    parsed = {"checks": [{"name": "a", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    skill_nodes = {"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": 0.8}]}
    one = build_evolution_decision(run_id="rid-h", parsed=parsed, events=events, skill_nodes=skill_nodes)
    two = build_evolution_decision(run_id="rid-h", parsed=parsed, events=events, skill_nodes=skill_nodes)
    assert one == two
    assert one["schema_version"] == "1.0"


def test_build_evolution_decision_fails_closed_for_malformed_inputs() -> None:
    out = build_evolution_decision(run_id="rid-x", parsed={}, events=[], skill_nodes=None)
    assert out["performance_score"] == 0.0
    assert out["mentorship_required"] is True


def test_build_related_human_artifacts_have_expected_shape() -> None:
    decision = {
        "schema_version": "1.0",
        "aggregate_id": "rid-y",
        "performance_score": 0.6,
        "growth_trend": "steady",
        "mentorship_required": True,
        "focus_areas": ["delivery.structured_output"],
    }
    mentorship = build_mentorship_plan(run_id="rid-y", decision=decision)
    reflection = build_reflection_bundle(run_id="rid-y", decision=decision, event_ref="evt-rid-y-traces")
    evaluation = build_practice_evaluation_result(decision=decision)
    assert mentorship["session_cadence_days"] == 14
    assert reflection["causal_closure_checklist"]["intervention_mapped"] is True
    assert isinstance(evaluation["passed"], bool)
