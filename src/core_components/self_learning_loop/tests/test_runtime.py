from __future__ import annotations

import pytest

from core_components.self_learning_loop import (
    MANDATORY_GATE_IDS,
    build_self_learning_loop,
    validate_self_learning_loop_dict,
)


def test_build_self_learning_loop_is_deterministic() -> None:
    payload_one = build_self_learning_loop(
        run_id="rid-self-loop",
        mode="guarded_pipeline",
        events=[{"stage": "finalize", "score": {"passed": True}} for _ in range(6)],
        practice_engine={"scores": {"readiness_signal": 0.9}},
        transfer_learning_metrics={"scores": {"transfer_efficiency": 0.8}},
        capability_growth_metrics={"scores": {"capability_growth_rate": 0.7}},
        skill_nodes={"nodes": [{"score": 0.86}]},
    )
    payload_two = build_self_learning_loop(
        run_id="rid-self-loop",
        mode="guarded_pipeline",
        events=[{"stage": "finalize", "score": {"passed": True}} for _ in range(6)],
        practice_engine={"scores": {"readiness_signal": 0.9}},
        transfer_learning_metrics={"scores": {"transfer_efficiency": 0.8}},
        capability_growth_metrics={"scores": {"capability_growth_rate": 0.7}},
        skill_nodes={"nodes": [{"score": 0.86}]},
    )
    assert payload_one == payload_two
    assert validate_self_learning_loop_dict(payload_one) == []
    assert payload_one["decision"]["decision"] == "promote"
    assert payload_one["decision"]["failed_gates"] == []


def test_validate_self_learning_loop_fail_closed() -> None:
    errs = validate_self_learning_loop_dict({"schema": "bad"})
    assert "self_learning_loop_schema" in errs
    assert "self_learning_loop_schema_version" in errs


def test_self_learning_loop_hold_when_insufficient_examples() -> None:
    payload = build_self_learning_loop(
        run_id="rid-self-loop",
        mode="guarded_pipeline",
        events=[{"stage": "finalize", "score": {"passed": True}}],
        practice_engine={"scores": {"readiness_signal": 0.9}},
        transfer_learning_metrics={"scores": {"transfer_efficiency": 0.9}},
        capability_growth_metrics={"scores": {"capability_growth_rate": 0.9}},
        skill_nodes={"nodes": [{"score": 0.9}]},
    )
    assert payload["decision"]["decision"] == "hold"
    assert payload["decision"]["failed_gates"] == ["min_examples"]


def test_self_learning_loop_reject_when_regression_and_contradiction_fail() -> None:
    payload = build_self_learning_loop(
        run_id="rid-self-loop",
        mode="guarded_pipeline",
        events=[{"stage": "finalize", "score": {"passed": True}} for _ in range(6)],
        practice_engine={"scores": {"readiness_signal": 0.1}},
        transfer_learning_metrics={"scores": {"transfer_efficiency": 0.7}},
        capability_growth_metrics={"scores": {"capability_growth_rate": 0.7}},
        skill_nodes={"nodes": [{"score": 0.95}]},
    )
    assert payload["decision"]["decision"] == "reject"
    assert payload["decision"]["failed_gates"] == ["regression_rate", "contradiction_rate"]
    assert set(MANDATORY_GATE_IDS)


def test_self_learning_failed_gate_and_reason_order_is_deterministic() -> None:
    payload = build_self_learning_loop(
        run_id="rid-self-loop",
        mode="guarded_pipeline",
        events=[{"stage": "finalize", "score": {"passed": True}} for _ in range(3)],
        practice_engine={"scores": {"readiness_signal": 0.2}},
        transfer_learning_metrics={"scores": {"transfer_efficiency": 0.1}},
        capability_growth_metrics={"scores": {"capability_growth_rate": 0.1}},
        skill_nodes={"nodes": [{"score": 0.9}]},
    )
    assert payload["decision"]["decision"] == "reject"
    assert payload["decision"]["failed_gates"] == [
        "min_examples",
        "regression_rate",
        "novelty_score",
        "contradiction_rate",
    ]
    assert payload["decision"]["decision_reasons"] == [
        "self_learning_loop_contract:gate_min_examples_unmet",
        "self_learning_loop_contract:gate_regression_rate_exceeded",
        "self_learning_loop_contract:gate_novelty_score_below_threshold",
        "self_learning_loop_contract:gate_contradiction_rate_exceeded",
    ]


def test_self_learning_loop_treats_truthy_non_boolean_finalize_passed_as_false() -> None:
    payload = build_self_learning_loop(
        run_id="rid-self-loop",
        mode="guarded_pipeline",
        events=[{"stage": "finalize", "score": {"passed": "true"}} for _ in range(6)],
        practice_engine={"scores": {"readiness_signal": 0.9}},
        transfer_learning_metrics={"scores": {"transfer_efficiency": 0.9}},
        capability_growth_metrics={"scores": {"capability_growth_rate": 0.9}},
        skill_nodes={"nodes": [{"score": 0.9}]},
    )
    assert payload["signals"]["finalize_pass_rate"] == pytest.approx(0.0)
    assert "verifier_pass_rate" in payload["decision"]["failed_gates"]


def test_validate_self_learning_loop_rejects_loop_state_mismatch() -> None:
    payload = build_self_learning_loop(
        run_id="rid-self-loop",
        mode="guarded_pipeline",
        events=[{"stage": "finalize", "score": {"passed": True}} for _ in range(6)],
        practice_engine={"scores": {"readiness_signal": 0.9}},
        transfer_learning_metrics={"scores": {"transfer_efficiency": 0.9}},
        capability_growth_metrics={"scores": {"capability_growth_rate": 0.9}},
        skill_nodes={"nodes": [{"score": 0.9}]},
    )
    payload["decision"]["loop_state"] = "hold"
    errs = validate_self_learning_loop_dict(payload)
    assert "self_learning_loop_loop_state_mismatch" in errs


def test_validate_self_learning_loop_rejects_primary_reason_mismatch() -> None:
    payload = build_self_learning_loop(
        run_id="rid-self-loop",
        mode="guarded_pipeline",
        events=[{"stage": "finalize", "score": {"passed": True}} for _ in range(6)],
        practice_engine={"scores": {"readiness_signal": 0.2}},
        transfer_learning_metrics={"scores": {"transfer_efficiency": 0.7}},
        capability_growth_metrics={"scores": {"capability_growth_rate": 0.7}},
        skill_nodes={"nodes": [{"score": 0.95}]},
    )
    payload["decision"]["primary_reason"] = "self_learning_loop_contract:all_gates_passed"
    errs = validate_self_learning_loop_dict(payload)
    assert "self_learning_loop_primary_reason_mismatch" in errs


def test_validate_self_learning_loop_rejects_next_action_mismatch() -> None:
    payload = build_self_learning_loop(
        run_id="rid-self-loop",
        mode="guarded_pipeline",
        events=[{"stage": "finalize", "score": {"passed": True}} for _ in range(6)],
        practice_engine={"scores": {"readiness_signal": 0.9}},
        transfer_learning_metrics={"scores": {"transfer_efficiency": 0.9}},
        capability_growth_metrics={"scores": {"capability_growth_rate": 0.9}},
        skill_nodes={"nodes": [{"score": 0.9}]},
    )
    payload["decision"]["next_action"] = "halt_and_repair"
    errs = validate_self_learning_loop_dict(payload)
    assert "self_learning_loop_next_action_mismatch" in errs


def test_self_learning_loop_uses_highest_valid_skill_node_score() -> None:
    payload = build_self_learning_loop(
        run_id="rid-self-loop-skill-nodes",
        mode="guarded_pipeline",
        events=[{"stage": "finalize", "score": {"passed": True}} for _ in range(6)],
        practice_engine={"scores": {"readiness_signal": 0.9}},
        transfer_learning_metrics={"scores": {"transfer_efficiency": 0.9}},
        capability_growth_metrics={"scores": {"capability_growth_rate": 0.9}},
        skill_nodes={"nodes": [{"score": "bad"}, {"score": 0.3}, {"score": 0.95}]},
    )
    assert payload["signals"]["capability_score"] == pytest.approx(0.95)


def test_validate_self_learning_loop_rejects_noncanonical_self_loop_evidence_ref() -> None:
    payload = build_self_learning_loop(
        run_id="rid-self-loop-evidence",
        mode="guarded_pipeline",
        events=[{"stage": "finalize", "score": {"passed": True}} for _ in range(6)],
        practice_engine={"scores": {"readiness_signal": 0.9}},
        transfer_learning_metrics={"scores": {"transfer_efficiency": 0.9}},
        capability_growth_metrics={"scores": {"capability_growth_rate": 0.9}},
        skill_nodes={"nodes": [{"score": 0.9}]},
    )
    payload["evidence"]["self_learning_loop_ref"] = "learning/other_self_learning_loop.json"
    errs = validate_self_learning_loop_dict(payload)
    assert "self_learning_loop_evidence_self_learning_loop_ref" in errs
