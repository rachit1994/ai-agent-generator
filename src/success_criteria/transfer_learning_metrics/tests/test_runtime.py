from __future__ import annotations

from success_criteria.transfer_learning_metrics import (
    build_transfer_learning_metrics,
    validate_transfer_learning_metrics_dict,
)


def test_build_transfer_learning_metrics_is_deterministic() -> None:
    parsed = {"checks": [{"name": "a", "passed": True}]}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    skill_nodes = {"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": 0.8}]}
    one = build_transfer_learning_metrics(run_id="rid-t", parsed=parsed, events=events, skill_nodes=skill_nodes)
    two = build_transfer_learning_metrics(run_id="rid-t", parsed=parsed, events=events, skill_nodes=skill_nodes)
    assert one == two
    assert validate_transfer_learning_metrics_dict(one) == []


def test_transfer_learning_metrics_fail_closed_when_malformed() -> None:
    errs = validate_transfer_learning_metrics_dict({"schema": "x"})
    assert "transfer_learning_metrics_schema" in errs
    assert "transfer_learning_metrics_schema_version" in errs
