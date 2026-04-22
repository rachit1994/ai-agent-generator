from __future__ import annotations

import math

import pytest

from success_criteria.stability_metrics import (
    build_stability_metrics,
    validate_stability_metrics_dict,
)


def test_build_stability_metrics_is_deterministic() -> None:
    events = [
        {"stage": "finalize", "score": {"passed": True, "reliability": 0.9}},
        {"stage": "finalize", "score": {"passed": False, "reliability": 0.6}},
        {"stage": "repair"},
    ]
    one = build_stability_metrics(run_id="rid-stability", events=events)
    two = build_stability_metrics(run_id="rid-stability", events=events)
    assert one == two
    assert validate_stability_metrics_dict(one) == []


def test_validate_stability_metrics_fail_closed() -> None:
    errs = validate_stability_metrics_dict({"schema": "bad"})
    assert "stability_metrics_schema" in errs
    assert "stability_metrics_schema_version" in errs


def test_build_stability_metrics_ignores_non_finite_reliability() -> None:
    payload = build_stability_metrics(
        run_id="rid-stability",
        events=[{"stage": "finalize", "score": {"passed": True, "reliability": math.nan}}],
    )
    assert payload["metrics"]["reliability_score"] == pytest.approx(0.0)
    assert payload["metrics"]["stability_score"] == pytest.approx(0.65)
    assert validate_stability_metrics_dict(payload) == []


def test_validate_stability_metrics_rejects_non_finite_metrics() -> None:
    payload = build_stability_metrics(
        run_id="rid-stability",
        events=[{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}],
    )
    payload["metrics"]["stability_score"] = math.nan
    errs = validate_stability_metrics_dict(payload)
    assert "stability_metrics_metric_finite:stability_score" in errs


def test_validate_stability_metrics_rejects_status_score_mismatch() -> None:
    payload = build_stability_metrics(
        run_id="rid-stability",
        events=[{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}],
    )
    payload["status"] = "unstable"
    errs = validate_stability_metrics_dict(payload)
    assert "stability_metrics_status_score_mismatch" in errs


def test_validate_stability_metrics_rejects_stability_score_arithmetic_mismatch() -> None:
    payload = build_stability_metrics(
        run_id="rid-stability",
        events=[{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}],
    )
    payload["metrics"]["stability_score"] = 0.0
    errs = validate_stability_metrics_dict(payload)
    assert "stability_metrics_metric_semantics:stability_score" in errs


def test_build_stability_metrics_non_dict_events_do_not_reduce_retry_pressure() -> None:
    payload = build_stability_metrics(
        run_id="rid-stability",
        events=[
            {"stage": "finalize", "score": {"passed": True, "reliability": 0.9}},
            {"stage": "repair"},
            "malformed-event",
        ],
    )
    assert payload["metrics"]["retry_pressure"] == pytest.approx(0.5)


def test_validate_stability_metrics_rejects_invalid_evidence_refs() -> None:
    payload = build_stability_metrics(
        run_id="rid-stability",
        events=[{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}],
    )
    payload["evidence"]["traces_ref"] = "../traces.jsonl"
    errs = validate_stability_metrics_dict(payload)
    assert "stability_metrics_evidence_ref:traces_ref" in errs


def test_validate_stability_metrics_rejects_invalid_stability_metrics_ref() -> None:
    payload = build_stability_metrics(
        run_id="rid-stability",
        events=[{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}],
    )
    payload["evidence"]["stability_metrics_ref"] = "learning/other.json"
    errs = validate_stability_metrics_dict(payload)
    assert "stability_metrics_evidence_ref:stability_metrics_ref" in errs
