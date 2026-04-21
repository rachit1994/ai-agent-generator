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
