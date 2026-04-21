from __future__ import annotations

from success_criteria.capability_growth_metrics import (
    build_capability_growth_metrics,
    validate_capability_growth_metrics_dict,
)


def test_build_capability_growth_metrics_is_deterministic() -> None:
    parsed = {"checks": [{"name": "a", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}]
    skill_nodes = {"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": 0.75}]}
    one = build_capability_growth_metrics(
        run_id="rid-cg", parsed=parsed, events=events, skill_nodes=skill_nodes
    )
    two = build_capability_growth_metrics(
        run_id="rid-cg", parsed=parsed, events=events, skill_nodes=skill_nodes
    )
    assert one == two
    assert validate_capability_growth_metrics_dict(one) == []


def test_validate_capability_growth_metrics_fail_closed() -> None:
    errs = validate_capability_growth_metrics_dict({"schema": "wrong"})
    assert "capability_growth_metrics_schema" in errs
    assert "capability_growth_metrics_schema_version" in errs
