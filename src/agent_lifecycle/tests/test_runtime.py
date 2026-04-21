from __future__ import annotations

from agent_lifecycle import (
    build_lifecycle_decision,
    build_practice_evaluation_result,
    build_promotion_package,
    build_reflection_bundle,
)


def test_build_lifecycle_decision_is_deterministic() -> None:
    parsed = {"checks": [{"name": "a", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True}} for _ in range(3)]
    skill_nodes = {"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": 0.72}]}
    one = build_lifecycle_decision(run_id="rid", parsed=parsed, events=events, skill_nodes=skill_nodes)
    two = build_lifecycle_decision(run_id="rid", parsed=parsed, events=events, skill_nodes=skill_nodes)
    assert one == two
    assert one["current_stage"] == "senior"
    assert one["proposed_stage"] == "senior"


def test_build_lifecycle_decision_detects_stagnation() -> None:
    parsed = {"checks": [{"name": "a", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": False}} for _ in range(4)]
    skill_nodes = {"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": 0.6}]}
    out = build_lifecycle_decision(run_id="rid2", parsed=parsed, events=events, skill_nodes=skill_nodes)
    assert "stagnation_detected" in out["reasons"]
    eval_result = build_practice_evaluation_result(out)
    assert eval_result["passed"] is False


def test_build_lifecycle_decision_treats_truthy_non_boolean_passed_as_false() -> None:
    parsed = {"checks": [{"name": "a", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": "true"}} for _ in range(4)]
    skill_nodes = {"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": 0.6}]}
    out = build_lifecycle_decision(run_id="rid3", parsed=parsed, events=events, skill_nodes=skill_nodes)
    assert "stagnation_detected" in out["reasons"]


def test_build_lifecycle_related_payloads_match_contract_shape() -> None:
    decision = {
        "schema_version": "1.0",
        "aggregate_id": "r",
        "score": 0.55,
        "current_stage": "mid",
        "proposed_stage": "senior",
        "lifecycle_state": "active",
        "reasons": ["promotion_threshold_met"],
    }
    reflection = build_reflection_bundle(run_id="r", decision=decision, event_ref="evt-r-traces")
    promotion = build_promotion_package(run_id="r", decision=decision)
    assert reflection["causal_closure_checklist"]["root_cause_evidence"] is True
    assert promotion["schema_version"] == "1.0"
    assert promotion["current_stage"] == "mid"


def test_build_promotion_package_fails_closed_for_non_numeric_score() -> None:
    decision = {
        "schema_version": "1.0",
        "aggregate_id": "r",
        "score": "bad",
        "current_stage": "mid",
        "proposed_stage": "senior",
        "lifecycle_state": "active",
        "reasons": ["steady_state"],
    }
    promotion = build_promotion_package(run_id="r", decision=decision)
    assert promotion["independent_evaluator_signal_ids"] == ["lifecycle-score:0.000"]
