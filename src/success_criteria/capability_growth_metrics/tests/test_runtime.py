from __future__ import annotations

import math

import pytest

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


def test_build_capability_growth_metrics_clamps_non_finite_inputs() -> None:
    payload = build_capability_growth_metrics(
        run_id="rid-cg",
        parsed={},
        events=[{"stage": "finalize", "score": {"passed": True, "reliability": math.nan}}],
        skill_nodes={"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": math.inf}]},
    )
    assert payload["metrics"]["capability_growth_rate"] == pytest.approx(0.5)
    assert payload["metrics"]["capability_stability_rate"] == pytest.approx(0.0)
    assert payload["metrics"]["growth_confidence"] == pytest.approx(0.15)
    assert validate_capability_growth_metrics_dict(payload) == []


def test_validate_capability_growth_metrics_rejects_non_finite_metric_values() -> None:
    errs = validate_capability_growth_metrics_dict(
        {
            "schema": "sde.capability_growth_metrics.v1",
            "schema_version": "1.0",
            "run_id": "rid-cg",
            "metrics": {
                "capability_growth_rate": math.nan,
                "capability_stability_rate": 0.2,
                "promotion_readiness_delta": 0.0,
                "growth_confidence": math.inf,
            },
        }
    )
    assert "capability_growth_metrics_metric_non_finite:capability_growth_rate" in errs
    assert "capability_growth_metrics_metric_non_finite:growth_confidence" in errs


def test_build_capability_growth_metrics_treats_truthy_non_boolean_pass_as_failed() -> None:
    payload = build_capability_growth_metrics(
        run_id="rid-cg",
        parsed={},
        events=[{"stage": "finalize", "score": {"passed": "true", "reliability": 0.9}}],
        skill_nodes={"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": 0.75}]},
    )
    assert payload["metrics"]["capability_growth_rate"] == pytest.approx(0.375)
    assert payload["metrics"]["promotion_readiness_delta"] == pytest.approx(-0.125)
    assert validate_capability_growth_metrics_dict(payload) == []


def test_validate_capability_growth_metrics_rejects_incoherent_derived_metrics() -> None:
    payload = build_capability_growth_metrics(
        run_id="rid-cg",
        parsed={},
        events=[{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}],
        skill_nodes={"schema_version": "1.0", "nodes": [{"skill_id": "x", "score": 0.75}]},
    )
    payload["metrics"]["promotion_readiness_delta"] = 0.99
    payload["metrics"]["growth_confidence"] = 0.01
    errs = validate_capability_growth_metrics_dict(payload)
    assert "capability_growth_metrics_metric_incoherent:promotion_readiness_delta" in errs
    assert "capability_growth_metrics_metric_incoherent:growth_confidence" in errs


def test_validate_capability_growth_metrics_rejects_missing_evidence() -> None:
    payload = {
        "schema": "sde.capability_growth_metrics.v1",
        "schema_version": "1.0",
        "run_id": "rid-cg",
        "metrics": {
            "capability_growth_rate": 0.5,
            "capability_stability_rate": 0.5,
            "promotion_readiness_delta": 0.0,
            "growth_confidence": 0.5,
        },
    }
    errs = validate_capability_growth_metrics_dict(payload)
    assert "capability_growth_metrics_evidence" in errs


def test_validate_capability_growth_metrics_rejects_invalid_evidence_refs() -> None:
    payload = {
        "schema": "sde.capability_growth_metrics.v1",
        "schema_version": "1.0",
        "run_id": "rid-cg",
        "metrics": {
            "capability_growth_rate": 0.5,
            "capability_stability_rate": 0.5,
            "promotion_readiness_delta": 0.0,
            "growth_confidence": 0.5,
        },
        "evidence": {
            "traces_ref": "",
            "skill_nodes_ref": 123,
        },
    }
    errs = validate_capability_growth_metrics_dict(payload)
    assert "capability_growth_metrics_evidence_ref:traces_ref" in errs
    assert "capability_growth_metrics_evidence_ref:skill_nodes_ref" in errs
