from __future__ import annotations

from core_components.self_learning_loop import (
    build_self_learning_loop,
    validate_self_learning_loop_dict,
)


def test_build_self_learning_loop_is_deterministic() -> None:
    payload_one = build_self_learning_loop(
        run_id="rid-self-loop",
        mode="guarded_pipeline",
        events=[{"stage": "finalize", "score": {"passed": True}}],
        practice_engine={"scores": {"readiness_signal": 0.9}},
        transfer_learning_metrics={"scores": {"transfer_efficiency": 0.8}},
        capability_growth_metrics={"scores": {"capability_growth_rate": 0.7}},
        skill_nodes={"nodes": [{"score": 0.86}]},
    )
    payload_two = build_self_learning_loop(
        run_id="rid-self-loop",
        mode="guarded_pipeline",
        events=[{"stage": "finalize", "score": {"passed": True}}],
        practice_engine={"scores": {"readiness_signal": 0.9}},
        transfer_learning_metrics={"scores": {"transfer_efficiency": 0.8}},
        capability_growth_metrics={"scores": {"capability_growth_rate": 0.7}},
        skill_nodes={"nodes": [{"score": 0.86}]},
    )
    assert payload_one == payload_two
    assert validate_self_learning_loop_dict(payload_one) == []


def test_validate_self_learning_loop_fail_closed() -> None:
    errs = validate_self_learning_loop_dict({"schema": "bad"})
    assert "self_learning_loop_schema" in errs
    assert "self_learning_loop_schema_version" in errs
