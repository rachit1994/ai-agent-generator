from __future__ import annotations

import math

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


def test_build_skill_nodes_fails_closed_for_non_boolean_check_status() -> None:
    parsed = {
        "checks": [
            {"name": "string-false", "passed": "false"},
            {"name": "numeric-true", "passed": 1},
            {"name": "real-bool-false", "passed": False},
        ],
        "refusal": None,
    }
    events = [{"stage": "finalize", "score": {"passed": False}}]
    out = build_skill_nodes(run_id="rid-bad-checks", parsed=parsed, events=events)
    assert math.isclose(out["nodes"][0]["score"], 0.0)
    assert math.isclose(out["nodes"][0]["confidence"], 0.0)


def test_build_promotion_package_fails_closed_for_non_numeric_node_score() -> None:
    malformed = {"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": "bad"}]}
    pkg = build_promotion_package(run_id="r-bad", parsed={}, events=[], skill_nodes=malformed)
    assert pkg["current_stage"] == "junior"
    assert pkg["proposed_stage"] == "junior"


def test_build_skill_nodes_treats_truthy_non_boolean_finalize_pass_as_failed() -> None:
    parsed = {"checks": [{"name": "ok", "passed": True}], "refusal": None}
    events = [{"stage": "finalize", "score": {"passed": "true"}}]
    out = build_skill_nodes(run_id="rid-truthy-finalize", parsed=parsed, events=events)
    assert math.isclose(out["nodes"][0]["score"], 0.7)
    assert math.isclose(out["nodes"][0]["confidence"], 0.5)
