from __future__ import annotations

from success_criteria.hard_release_gates import (
    build_hard_release_gates,
    validate_hard_release_gates_dict,
)


def test_build_hard_release_gates_is_deterministic() -> None:
    parsed = {
        "checks": [{"name": "shape", "passed": True}, {"name": "quality", "passed": True}],
        "hard_stops": [{"id": "HS01", "passed": True}],
    }
    events = [{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}]
    one = build_hard_release_gates(run_id="rid-hard-gates", mode="guarded_pipeline", parsed=parsed, events=events)
    two = build_hard_release_gates(run_id="rid-hard-gates", mode="guarded_pipeline", parsed=parsed, events=events)
    assert one == two
    assert validate_hard_release_gates_dict(one) == []


def test_validate_hard_release_gates_fail_closed() -> None:
    errs = validate_hard_release_gates_dict({"schema": "bad"})
    assert "hard_release_gates_schema" in errs
    assert "hard_release_gates_schema_version" in errs
