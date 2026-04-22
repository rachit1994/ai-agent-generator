from __future__ import annotations

from success_criteria.extended_binary_gates import (
    build_extended_binary_gates,
    validate_extended_binary_gates_dict,
)


def test_build_extended_binary_gates_is_deterministic() -> None:
    parsed = {"checks": [{"name": "a", "passed": True}, {"name": "b", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True, "reliability": 0.91}}]
    skill_nodes = {"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": 0.8}]}
    one = build_extended_binary_gates(
        run_id="rid-ebg", parsed=parsed, events=events, skill_nodes=skill_nodes
    )
    two = build_extended_binary_gates(
        run_id="rid-ebg", parsed=parsed, events=events, skill_nodes=skill_nodes
    )
    assert one == two
    assert validate_extended_binary_gates_dict(one) == []


def test_validate_extended_binary_gates_fail_closed() -> None:
    errs = validate_extended_binary_gates_dict({"schema": "wrong"})
    assert "extended_binary_gates_schema" in errs
    assert "extended_binary_gates_schema_version" in errs


def test_validate_extended_binary_gates_rejects_overall_pass_mismatch() -> None:
    payload = {
        "schema": "sde.extended_binary_gates.v1",
        "schema_version": "1.0",
        "run_id": "rid-ebg",
        "overall_pass": True,
        "gates": {
            "reliability_gate": True,
            "delivery_gate": True,
            "governance_gate": True,
            "learning_gate": False,
        },
    }
    errs = validate_extended_binary_gates_dict(payload)
    assert "extended_binary_gates_overall_pass_mismatch" in errs


def test_extended_binary_gates_treats_truthy_non_boolean_finalize_pass_as_failed() -> None:
    payload = build_extended_binary_gates(
        run_id="rid-ebg-truthy-finalize",
        parsed={"checks": [{"name": "a", "passed": True}]},
        events=[{"stage": "finalize", "score": {"passed": "true", "reliability": 0.95}}],
        skill_nodes={"nodes": [{"score": 0.9}]},
    )
    assert payload["gates"]["delivery_gate"] is False


def test_extended_binary_gates_treats_truthy_non_boolean_check_pass_as_failed() -> None:
    payload = build_extended_binary_gates(
        run_id="rid-ebg-truthy-check",
        parsed={"checks": [{"name": "a", "passed": "true"}]},
        events=[{"stage": "finalize", "score": {"passed": True, "reliability": 0.95}}],
        skill_nodes={"nodes": [{"score": 0.9}]},
    )
    assert payload["gates"]["governance_gate"] is False


def test_validate_extended_binary_gates_rejects_missing_evidence_refs() -> None:
    payload = build_extended_binary_gates(
        run_id="rid-ebg-evidence",
        parsed={"checks": [{"name": "a", "passed": True}]},
        events=[{"stage": "finalize", "score": {"passed": True, "reliability": 0.95}}],
        skill_nodes={"nodes": [{"score": 0.9}]},
    )
    payload["evidence"]["checks_ref"] = ""
    errs = validate_extended_binary_gates_dict(payload)
    assert "extended_binary_gates_evidence_ref:checks_ref" in errs


def test_validate_extended_binary_gates_rejects_non_canonical_evidence_refs() -> None:
    payload = build_extended_binary_gates(
        run_id="rid-ebg-evidence-canonical",
        parsed={"checks": [{"name": "a", "passed": True}]},
        events=[{"stage": "finalize", "score": {"passed": True, "reliability": 0.95}}],
        skill_nodes={"nodes": [{"score": 0.9}]},
    )
    payload["evidence"]["traces_ref"] = "learning/traces.jsonl"
    errs = validate_extended_binary_gates_dict(payload)
    assert "extended_binary_gates_evidence_ref:traces_ref_canonical" in errs


def test_extended_binary_gates_governance_ignores_review_checks_in_denominator() -> None:
    payload = build_extended_binary_gates(
        run_id="rid-ebg-governance-review",
        parsed={
            "checks": [
                {"name": "review", "passed": True},
                {"name": "shape", "passed": True},
            ]
        },
        events=[{"stage": "finalize", "score": {"passed": True, "reliability": 0.95}}],
        skill_nodes={"nodes": [{"score": 0.9}]},
    )
    assert payload["gates"]["governance_gate"] is True


def test_extended_binary_gates_learning_uses_highest_valid_skill_score() -> None:
    payload = build_extended_binary_gates(
        run_id="rid-ebg-learning-nodes",
        parsed={"checks": [{"name": "shape", "passed": True}]},
        events=[{"stage": "finalize", "score": {"passed": True, "reliability": 0.95}}],
        skill_nodes={"nodes": [{"score": "bad"}, {"score": 0.7}, {"score": 0.95}]},
    )
    assert payload["gates"]["learning_gate"] is True
