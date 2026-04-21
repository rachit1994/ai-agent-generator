from __future__ import annotations

from core_components.learning_service import (
    build_learning_service,
    validate_learning_service_dict,
)


def test_build_learning_service_is_deterministic() -> None:
    events = [{"stage": "finalize", "score": {"passed": True}}]
    one = build_learning_service(
        run_id="rid-learning-service",
        mode="guarded_pipeline",
        reflection_bundle={"reflections": [{"id": "r1"}]},
        canary_report={"rows": [{"id": "c1"}]},
        events=events,
    )
    two = build_learning_service(
        run_id="rid-learning-service",
        mode="guarded_pipeline",
        reflection_bundle={"reflections": [{"id": "r1"}]},
        canary_report={"rows": [{"id": "c1"}]},
        events=events,
    )
    assert one == two
    assert validate_learning_service_dict(one) == []


def test_validate_learning_service_fail_closed() -> None:
    errs = validate_learning_service_dict({"schema": "bad"})
    assert "learning_service_schema" in errs
    assert "learning_service_schema_version" in errs
