from __future__ import annotations

from agent_lifecycle import (
    build_lifecycle_decision,
    build_practice_evaluation_result,
    build_promotion_package,
    build_reflection_bundle,
    execute_lifecycle_runtime,
)


def test_build_lifecycle_decision_is_deterministic() -> None:
    parsed = {
        "checks": [{"name": "a", "passed": True}],
        "transition_events": [
            {
                "event_id": "life-evt-001",
                "from_stage": "senior",
                "to_stage": "senior",
                "reason": "steady_state",
                "approved": True,
            }
        ],
    }
    events = [{"stage": "finalize", "score": {"passed": True}} for _ in range(3)]
    skill_nodes = {"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": 0.72}]}
    one = build_lifecycle_decision(
        run_id="rid", parsed=parsed, events=events, skill_nodes=skill_nodes, prior_stage="senior"
    )
    two = build_lifecycle_decision(
        run_id="rid", parsed=parsed, events=events, skill_nodes=skill_nodes, prior_stage="senior"
    )
    assert one == two
    assert one["current_stage"] == "senior"
    assert one["proposed_stage"] == "senior"
    assert one["execution"]["events_processed"] == 1


def test_build_lifecycle_decision_detects_stagnation() -> None:
    parsed = {"checks": [{"name": "a", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": False}} for _ in range(4)]
    skill_nodes = {"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": 0.6}]}
    out = build_lifecycle_decision(
        run_id="rid2", parsed=parsed, events=events, skill_nodes=skill_nodes, prior_stage="mid"
    )
    assert "stagnation_detected" in out["reasons"]
    eval_result = build_practice_evaluation_result(out)
    assert eval_result["passed"] is False


def test_build_lifecycle_decision_treats_truthy_non_boolean_passed_as_false() -> None:
    parsed = {"checks": [{"name": "a", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": "true"}} for _ in range(4)]
    skill_nodes = {"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": 0.6}]}
    out = build_lifecycle_decision(
        run_id="rid3", parsed=parsed, events=events, skill_nodes=skill_nodes, prior_stage="mid"
    )
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


def test_build_lifecycle_decision_promotes_against_prior_stage() -> None:
    out = build_lifecycle_decision(
        run_id="rid-promote",
        parsed={},
        events=[],
        skill_nodes={"nodes": [{"score": 0.95}]},
        prior_stage="senior",
    )
    assert out["current_stage"] == "senior"
    assert out["proposed_stage"] == "architect"
    assert "promotion_threshold_met" in out["reasons"]


def test_build_lifecycle_decision_demotes_against_prior_stage() -> None:
    out = build_lifecycle_decision(
        run_id="rid-demote",
        parsed={},
        events=[],
        skill_nodes={"nodes": [{"score": 0.4}]},
        prior_stage="senior",
    )
    assert out["current_stage"] == "senior"
    assert out["proposed_stage"] == "mid"
    assert "demotion_floor_breach" in out["reasons"]


def test_build_lifecycle_decision_fail_closed_without_prior_stage() -> None:
    out = build_lifecycle_decision(
        run_id="rid-no-prior",
        parsed={},
        events=[],
        skill_nodes={"nodes": [{"score": 1.0}]},
    )
    assert "missing_or_invalid_prior_stage" in out["reasons"]
    assert "promotion_threshold_met" not in out["reasons"]


def test_execute_lifecycle_runtime_detects_unapproved_stage_change() -> None:
    decision = {
        "current_stage": "mid",
        "proposed_stage": "senior",
    }
    parsed = {
        "transition_events": [
            {
                "event_id": "life-evt-009",
                "from_stage": "mid",
                "to_stage": "senior",
                "reason": "promotion_threshold_met",
                "approved": False,
            }
        ]
    }
    execution = execute_lifecycle_runtime(parsed=parsed, decision=decision)
    assert execution["approval_violations"] == ["life-evt-009"]


def test_build_lifecycle_decision_marks_transition_mismatch() -> None:
    out = build_lifecycle_decision(
        run_id="rid-mismatch",
        parsed={
            "transition_events": [
                {
                    "event_id": "life-evt-010",
                    "from_stage": "junior",
                    "to_stage": "mid",
                    "reason": "promotion_threshold_met",
                    "approved": True,
                }
            ]
        },
        events=[],
        skill_nodes={"nodes": [{"score": 0.2}]},
        prior_stage="senior",
    )
    assert out["execution"]["decision_transition_matches"] is False
