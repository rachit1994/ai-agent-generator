from __future__ import annotations

import pytest

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


def test_build_learning_service_counts_only_strict_true_passed() -> None:
    payload = build_learning_service(
        run_id="rid-learning-service",
        mode="guarded_pipeline",
        reflection_bundle={"reflections": []},
        canary_report={"rows": []},
        events=[
            {"stage": "finalize", "score": {"passed": True}},
            {"stage": "finalize", "score": {"passed": 1}},
            {"stage": "finalize", "score": {"passed": "true"}},
            {"stage": "finalize", "score": {"passed": False}},
        ],
    )
    assert payload["metrics"]["finalize_rows"] == 4
    assert payload["metrics"]["finalize_pass_rate"] == pytest.approx(0.25)


def test_validate_learning_service_rejects_invalid_finalize_pass_rate() -> None:
    payload = build_learning_service(
        run_id="rid-learning-service",
        mode="guarded_pipeline",
        reflection_bundle={"reflections": []},
        canary_report={"rows": []},
        events=[],
    )
    payload["metrics"]["finalize_pass_rate"] = "bad"
    errs = validate_learning_service_dict(payload)
    assert "learning_service_finalize_pass_rate_type" in errs


def test_validate_learning_service_rejects_status_semantics_mismatch() -> None:
    payload = build_learning_service(
        run_id="rid-learning-service",
        mode="guarded_pipeline",
        reflection_bundle={"reflections": [{"id": "r1"}]},
        canary_report={"rows": [{"id": "c1"}]},
        events=[{"stage": "finalize", "score": {"passed": True}}],
    )
    payload["status"] = "insufficient_signal"
    errs = validate_learning_service_dict(payload)
    assert "learning_service_status_semantics:insufficient_signal" in errs


def test_validate_learning_service_rejects_metric_semantics_mismatch() -> None:
    payload = build_learning_service(
        run_id="rid-learning-service",
        mode="guarded_pipeline",
        reflection_bundle={"reflections": [{"id": "r1"}]},
        canary_report={"rows": []},
        events=[{"stage": "finalize", "score": {"passed": True}}],
    )
    payload["metrics"]["health_score"] = 0.0
    errs = validate_learning_service_dict(payload)
    assert "learning_service_metric_semantics:health_score" in errs
