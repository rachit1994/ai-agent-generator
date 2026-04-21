from __future__ import annotations

from evaluation_framework.online_evaluation_shadow_canary_artifact import (
    build_online_evaluation_shadow_canary,
    validate_online_evaluation_shadow_canary_dict,
)


def test_build_online_evaluation_shadow_canary_is_deterministic() -> None:
    canary = {"schema_version": "1.0", "shadow_metrics": {"latency_p95_ms": 0}, "promote": True}
    events = [{"stage": "finalize", "score": {"passed": True}}]
    one = build_online_evaluation_shadow_canary(
        run_id="rid-online-shadow",
        canary_report=canary,
        events=events,
    )
    two = build_online_evaluation_shadow_canary(
        run_id="rid-online-shadow",
        canary_report=canary,
        events=events,
    )
    assert one == two
    assert validate_online_evaluation_shadow_canary_dict(one) == []


def test_validate_online_evaluation_shadow_canary_fail_closed() -> None:
    errs = validate_online_evaluation_shadow_canary_dict({"schema": "bad"})
    assert "online_evaluation_shadow_canary_schema" in errs
    assert "online_evaluation_shadow_canary_schema_version" in errs
