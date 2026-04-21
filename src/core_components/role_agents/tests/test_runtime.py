from __future__ import annotations

from core_components.role_agents import build_role_agents, validate_role_agents_dict


def test_build_role_agents_is_deterministic() -> None:
    payload_one = build_role_agents(
        run_id="rid-role-agents",
        parsed={"checks": [{"name": "shape", "passed": True}]},
        events=[{"stage": "finalize", "score": {"passed": True}}],
        skill_nodes={"nodes": [{"score": 0.8}]},
    )
    payload_two = build_role_agents(
        run_id="rid-role-agents",
        parsed={"checks": [{"name": "shape", "passed": True}]},
        events=[{"stage": "finalize", "score": {"passed": True}}],
        skill_nodes={"nodes": [{"score": 0.8}]},
    )
    assert payload_one == payload_two
    assert validate_role_agents_dict(payload_one) == []


def test_validate_role_agents_fail_closed() -> None:
    errs = validate_role_agents_dict({"schema": "bad"})
    assert "role_agents_schema" in errs
    assert "role_agents_schema_version" in errs
