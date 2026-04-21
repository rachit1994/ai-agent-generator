from __future__ import annotations

from workflow_pipelines.strategy_overlay import (
    build_strategy_overlay_runtime,
    validate_strategy_overlay_runtime_dict,
)


def test_build_strategy_overlay_runtime_is_deterministic() -> None:
    proposal = {
        "schema_version": "1.0",
        "actor_id": "strategy-agent-harness",
        "requires_promotion_package": True,
        "applied_autonomy": False,
        "proposal_ref": "lifecycle/promotion_package.json",
    }
    events = [{"stage": "finalize", "score": {"passed": True}}]
    one = build_strategy_overlay_runtime(
        run_id="rid-strategy-overlay", mode="guarded_pipeline", proposal=proposal, events=events
    )
    two = build_strategy_overlay_runtime(
        run_id="rid-strategy-overlay", mode="guarded_pipeline", proposal=proposal, events=events
    )
    assert one == two
    assert validate_strategy_overlay_runtime_dict(one) == []


def test_validate_strategy_overlay_runtime_fail_closed() -> None:
    errs = validate_strategy_overlay_runtime_dict({"schema": "bad"})
    assert "strategy_overlay_runtime_schema" in errs
    assert "strategy_overlay_runtime_schema_version" in errs
