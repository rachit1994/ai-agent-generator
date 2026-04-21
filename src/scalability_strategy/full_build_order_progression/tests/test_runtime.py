from __future__ import annotations

from scalability_strategy.full_build_order_progression import (
    build_full_build_order_progression,
    validate_full_build_order_progression_dict,
)


def test_build_full_build_order_progression_is_deterministic() -> None:
    events = [
        {"type": "stage_event", "stage": "planner_doc"},
        {"type": "stage_event", "stage": "planner_prompt"},
        {"type": "stage_event", "stage": "executor"},
        {"type": "stage_event", "stage": "finalize"},
    ]
    one = build_full_build_order_progression(run_id="rid-fbop", mode="guarded_pipeline", orchestration_events=events)
    two = build_full_build_order_progression(run_id="rid-fbop", mode="guarded_pipeline", orchestration_events=events)
    assert one == two
    assert validate_full_build_order_progression_dict(one) == []


def test_validate_full_build_order_progression_fail_closed() -> None:
    errs = validate_full_build_order_progression_dict({"schema": "bad"})
    assert "full_build_order_progression_schema" in errs
    assert "full_build_order_progression_schema_version" in errs

