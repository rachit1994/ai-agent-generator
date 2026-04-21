from __future__ import annotations

import math

import pytest

from human_professional_evolution_model import (
    build_evolution_decision,
    build_canary_report,
    build_mentorship_plan,
    build_practice_evaluation_result,
    build_promotion_package,
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
    assert abs(out["performance_score"] - 0.0) < 1e-9
    assert out["mentorship_required"] is True


def test_build_evolution_decision_fails_closed_for_non_finite_skill_score() -> None:
    out = build_evolution_decision(
        run_id="rid-nan",
        parsed={},
        events=[],
        skill_nodes={"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": math.nan}]},
    )
    assert abs(out["performance_score"] - 0.0) < 1e-9
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


def test_build_evolution_decision_treats_truthy_non_boolean_finalize_passed_as_false() -> None:
    out = build_evolution_decision(
        run_id="rid-truthy",
        parsed={},
        events=[{"stage": "finalize", "score": {"passed": "true"}}],
        skill_nodes={"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": 0.8}]},
    )
    assert out["performance_score"] == pytest.approx(0.56)


def test_related_artifacts_fail_closed_for_non_numeric_performance_score() -> None:
    malformed = {"performance_score": "bad-score"}
    promotion = build_promotion_package(run_id="rid-bad-perf", decision=malformed)
    evaluation = build_practice_evaluation_result(decision=malformed)
    canary = build_canary_report(decision=malformed)
    assert promotion["current_stage"] == "junior"
    assert promotion["proposed_stage"] == "junior"
    assert evaluation["passed"] is False
    assert canary["promote"] is False


def test_build_mentorship_plan_fail_closed_for_malformed_focus_areas_and_flag() -> None:
    plan = build_mentorship_plan(
        run_id="rid-bad-mentorship",
        decision={"focus_areas": "delivery.structured_output", "mentorship_required": "true"},
    )
    assert plan["focus_areas"] == ["delivery.structured_output"]
    assert plan["mentorship_required"] is False


def test_build_reflection_bundle_treats_truthy_non_boolean_mentorship_required_as_none() -> None:
    bundle = build_reflection_bundle(
        run_id="rid-reflection-truthy",
        decision={"growth_trend": "steady", "mentorship_required": "true"},
        event_ref="evt-reflection",
    )
    assert bundle["proposed_intervention"] == "none"
