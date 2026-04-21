from __future__ import annotations

from scalability_strategy import build_scalability_strategy, validate_scalability_strategy_dict


def test_build_scalability_strategy_is_deterministic() -> None:
    parsed = {"checks": [{"name": "a", "passed": True}, {"name": "b", "passed": True}]}
    events = [{"stage": "finalize", "retry_count": 0, "score": {"passed": True}}]
    cto = {"balanced_gates": {"validation_ready": True}, "hard_stops": [{"id": "HS01", "passed": True}]}
    one = build_scalability_strategy(
        run_id="run-scalability",
        mode="guarded_pipeline",
        parsed=parsed,
        events=events,
        cto=cto,
    )
    two = build_scalability_strategy(
        run_id="run-scalability",
        mode="guarded_pipeline",
        parsed=parsed,
        events=events,
        cto=cto,
    )
    assert one == two
    assert validate_scalability_strategy_dict(one) == []


def test_validate_scalability_strategy_fail_closed() -> None:
    errs = validate_scalability_strategy_dict({"schema": "bad"})
    assert "scalability_strategy_schema" in errs
    assert "scalability_strategy_schema_version" in errs

