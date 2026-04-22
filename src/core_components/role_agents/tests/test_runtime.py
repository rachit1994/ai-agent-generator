from __future__ import annotations

import pytest

from core_components.role_agents import (
    build_role_agents,
    execute_role_agents_runtime,
    validate_role_agents_dict,
)


def test_build_role_agents_is_deterministic() -> None:
    payload_one = build_role_agents(
        run_id="rid-role-agents",
        parsed={"checks": [{"name": "shape", "passed": True}]},
        events=[{"event_id": "evt-1", "stage": "finalize", "score": {"passed": True}}],
        skill_nodes={"nodes": [{"score": 0.8}]},
    )
    payload_two = build_role_agents(
        run_id="rid-role-agents",
        parsed={"checks": [{"name": "shape", "passed": True}]},
        events=[{"event_id": "evt-1", "stage": "finalize", "score": {"passed": True}}],
        skill_nodes={"nodes": [{"score": 0.8}]},
    )
    assert payload_one == payload_two
    assert validate_role_agents_dict(payload_one) == []
    assert payload_one["execution"]["finalize_events_processed"] == 1


def test_validate_role_agents_fail_closed() -> None:
    errs = validate_role_agents_dict({"schema": "bad"})
    assert "role_agents_schema" in errs
    assert "role_agents_schema_version" in errs


def test_build_role_agents_fails_closed_on_truthy_non_boolean_passed() -> None:
    payload = build_role_agents(
        run_id="rid-role-agents",
        parsed={"checks": [{"name": "shape", "passed": "yes"}]},
        events=[{"event_id": "evt-2", "stage": "finalize", "score": {"passed": "true"}}],
        skill_nodes={"nodes": [{"score": 0.5}]},
    )
    assert payload["role_scores"]["planner"] == pytest.approx(0.0)
    assert payload["role_scores"]["implementor"] == pytest.approx(0.0)


def test_validate_role_agents_rejects_status_spread_mismatch() -> None:
    payload = {
        "schema": "sde.role_agents.v1",
        "schema_version": "1.0",
        "run_id": "rid-role-agents",
        "status": "drifted",
        "execution": {
            "checks_processed": 1,
            "finalize_events_processed": 1,
            "malformed_event_rows": 0,
            "strict_boolean_violations": [],
        },
        "role_scores": {"planner": 0.5, "implementor": 0.5, "verifier": 0.5},
        "evidence": {
            "summary_ref": "summary.json",
            "traces_ref": "traces.jsonl",
            "skill_nodes_ref": "capability/skill_nodes.json",
            "role_agents_ref": "capability/role_agents.json",
        },
    }
    errs = validate_role_agents_dict(payload)
    assert "role_agents_status_semantics:drifted" in errs


def test_role_agents_governance_excludes_review_checks_from_denominator() -> None:
    payload = build_role_agents(
        run_id="rid-role-agents-review",
        parsed={
            "checks": [
                {"name": "review", "passed": True},
                {"name": "shape", "passed": True},
            ]
        },
        events=[{"event_id": "evt-1", "stage": "finalize", "score": {"passed": True}}],
        skill_nodes={"nodes": [{"score": 0.8}]},
    )
    assert payload["role_scores"]["planner"] == pytest.approx(1.0)


def test_role_agents_verifier_uses_highest_valid_skill_node_score() -> None:
    payload = build_role_agents(
        run_id="rid-role-agents-skill-nodes",
        parsed={"checks": [{"name": "shape", "passed": True}]},
        events=[{"event_id": "evt-1", "stage": "finalize", "score": {"passed": True}}],
        skill_nodes={"nodes": [{"score": "bad"}, {"score": 0.4}, {"score": 0.9}]},
    )
    assert payload["role_scores"]["verifier"] == pytest.approx(0.9)


def test_execute_role_agents_runtime_detects_malformed_rows() -> None:
    execution = execute_role_agents_runtime(
        parsed={"checks": [{"name": "shape", "passed": True}]},
        events=[
            {"event_id": "evt-1", "stage": "finalize", "score": {"passed": True}},
            {"event_id": "evt-2", "stage": "finalize", "score": {"passed": "true"}},
            "bad-row",
        ],
    )
    assert execution["checks_processed"] == 1
    assert execution["finalize_events_processed"] == 2
    assert execution["malformed_event_rows"] == 1
    assert execution["strict_boolean_violations"] == ["evt-2"]
