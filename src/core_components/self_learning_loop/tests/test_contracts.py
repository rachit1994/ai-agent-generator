from __future__ import annotations

from core_components.self_learning_loop import validate_self_learning_loop_dict


def _valid_payload() -> dict[str, object]:
    return {
        "schema": "sde.self_learning_loop.v1",
        "schema_version": "1.0",
        "run_id": "rid-1",
        "mode": "guarded_pipeline",
        "signals": {
            "finalize_pass_rate": 0.95,
            "capability_score": 0.9,
            "transfer_efficiency": 0.9,
            "growth_signal": 0.9,
            "practice_readiness": 0.9,
        },
        "decision": {
            "decision": "promote",
            "failed_gates": [],
            "decision_reasons": ["self_learning_loop_contract:all_gates_passed"],
            "next_action": "open_promotion_review",
            "primary_reason": "self_learning_loop_contract:all_gates_passed",
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


def test_validate_unknown_gate_is_rejected() -> None:
    payload = _valid_payload()
    payload["decision"] = {
        "decision": "hold",
        "failed_gates": ["not-real"],
        "decision_reasons": ["self_learning_loop_contract:gate_unknown"],
        "next_action": "run_practice_cycle",
        "primary_reason": "self_learning_loop_contract:gate_unknown",
    }
    errs = validate_self_learning_loop_dict(payload)
    assert "self_learning_loop_unknown_gate_id" in errs


def test_promote_with_failed_gates_is_rejected() -> None:
    payload = _valid_payload()
    payload["decision"] = {
        "decision": "promote",
        "failed_gates": ["min_examples"],
        "decision_reasons": ["self_learning_loop_contract:gate_min_examples_unmet"],
        "next_action": "open_promotion_review",
        "primary_reason": "self_learning_loop_contract:gate_min_examples_unmet",
    }
    errs = validate_self_learning_loop_dict(payload)
    assert "self_learning_loop_promote_failed_gates" in errs


def test_missing_candidates_reference_is_rejected() -> None:
    payload = _valid_payload()
    payload["evidence"] = {
        "traces_ref": "traces.jsonl",
        "skill_nodes_ref": "capability/skill_nodes.json",
        "practice_engine_ref": "practice/practice_engine.json",
        "transfer_learning_metrics_ref": "learning/transfer_learning_metrics.json",
        "capability_growth_metrics_ref": "learning/capability_growth_metrics.json",
        "self_learning_loop_ref": "learning/self_learning_loop.json",
    }
    errs = validate_self_learning_loop_dict(payload)
    assert "self_learning_loop_evidence_self_learning_candidates_ref" in errs


def test_failed_gates_must_be_canonical_and_unique() -> None:
    payload = _valid_payload()
    payload["decision"] = {
        "decision": "reject",
        "failed_gates": ["regression_rate", "min_examples", "regression_rate"],
        "decision_reasons": [
            "self_learning_loop_contract:gate_regression_rate_exceeded",
            "self_learning_loop_contract:gate_min_examples_unmet",
        ],
        "next_action": "halt_and_repair",
        "primary_reason": "self_learning_loop_contract:gate_regression_rate_exceeded",
    }
    errs = validate_self_learning_loop_dict(payload)
    assert "self_learning_loop_duplicate_failed_gates" in errs


def test_decision_reasons_must_be_unique() -> None:
    payload = _valid_payload()
    payload["decision"] = {
        "decision": "hold",
        "failed_gates": ["min_examples"],
        "decision_reasons": [
            "self_learning_loop_contract:gate_min_examples_unmet",
            "self_learning_loop_contract:gate_min_examples_unmet",
        ],
        "next_action": "run_practice_cycle",
        "primary_reason": "self_learning_loop_contract:gate_min_examples_unmet",
    }
    errs = validate_self_learning_loop_dict(payload)
    assert "self_learning_loop_duplicate_decision_reasons" in errs


def test_failed_gates_must_follow_policy_order() -> None:
    payload = _valid_payload()
    payload["decision"] = {
        "decision": "reject",
        "failed_gates": ["novelty_score", "min_examples"],
        "decision_reasons": [
            "self_learning_loop_contract:gate_novelty_score_below_threshold",
            "self_learning_loop_contract:gate_min_examples_unmet",
        ],
        "next_action": "halt_and_repair",
        "primary_reason": "self_learning_loop_contract:gate_novelty_score_below_threshold",
    }
    errs = validate_self_learning_loop_dict(payload)
    assert "self_learning_loop_failed_gates_order" in errs
