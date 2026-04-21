from __future__ import annotations

from capability_model import build_promotion_package, build_skill_nodes


def test_build_skill_nodes_is_deterministic() -> None:
    parsed = {"checks": [{"name": "a", "passed": True}, {"name": "b", "passed": False}], "refusal": None}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    one = build_skill_nodes(run_id="rid-1", parsed=parsed, events=events)
    two = build_skill_nodes(run_id="rid-1", parsed=parsed, events=events)
    assert one == two
    assert one["schema_version"] == "1.0"
    assert len(one["nodes"]) == 1
    assert one["nodes"][0]["score"] >= 0.0


def test_build_skill_nodes_penalizes_refusal() -> None:
    parsed = {"checks": [{"name": "a", "passed": True}], "refusal": {"code": "unsafe_action_refused"}}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    out = build_skill_nodes(run_id="rid-2", parsed=parsed, events=events)
    assert out["nodes"][0]["score"] < 1.0


def test_build_promotion_package_changes_stage_by_score() -> None:
    low = {"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": 0.2}]}
    high = {"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": 0.95}]}
    low_pkg = build_promotion_package(run_id="r-low", parsed={}, events=[], skill_nodes=low)
    high_pkg = build_promotion_package(run_id="r-high", parsed={}, events=[], skill_nodes=high)
    assert low_pkg["current_stage"] == "junior"
    assert low_pkg["proposed_stage"] == "junior"
    assert high_pkg["proposed_stage"] == "architect"
