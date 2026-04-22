from __future__ import annotations

import math

import pytest

from success_criteria.error_reduction_metrics import (
    build_error_reduction_metrics,
    execute_error_reduction_runtime,
    validate_error_reduction_metrics_dict,
)


def test_build_error_reduction_metrics_is_deterministic() -> None:
    parsed = {"checks": [{"name": "a", "passed": False}, {"name": "b", "passed": True}]}
    events = [{"event_id": "evt-1", "stage": "finalize", "score": {"passed": True}}]
    one = build_error_reduction_metrics(run_id="rid-erm", parsed=parsed, events=events, skill_nodes=None)
    two = build_error_reduction_metrics(run_id="rid-erm", parsed=parsed, events=events, skill_nodes=None)
    assert one == two
    assert validate_error_reduction_metrics_dict(one) == []
    assert one["execution"]["events_processed"] == 1


def test_validate_error_reduction_metrics_fail_closed() -> None:
    errs = validate_error_reduction_metrics_dict({"schema": "bad"})
    assert "error_reduction_metrics_schema" in errs
    assert "error_reduction_metrics_schema_version" in errs


def test_validate_error_reduction_metrics_rejects_non_finite_numbers() -> None:
    payload = {
        "schema": "sde.error_reduction_metrics.v1",
        "schema_version": "1.0",
        "run_id": "rid-non-finite",
        "metrics": {
            "baseline_error_count": 2,
            "candidate_error_count": 1,
            "resolved_error_count": 1,
            "error_reduction_rate": math.nan,
            "net_error_delta": math.inf,
        },
    }
    errs = validate_error_reduction_metrics_dict(payload)
    assert "error_reduction_metrics_metric_finite:error_reduction_rate" in errs
    assert "error_reduction_metrics_metric_finite:net_error_delta" in errs


def test_validate_error_reduction_metrics_rejects_non_integral_or_negative_counts() -> None:
    payload = {
        "schema": "sde.error_reduction_metrics.v1",
        "schema_version": "1.0",
        "run_id": "rid-counts",
        "metrics": {
            "baseline_error_count": 2.5,
            "candidate_error_count": -1,
            "resolved_error_count": 0,
            "error_reduction_rate": 0.0,
            "net_error_delta": -2.0,
        },
    }
    errs = validate_error_reduction_metrics_dict(payload)
    assert "error_reduction_metrics_metric_integral:baseline_error_count" in errs
    assert "error_reduction_metrics_metric_non_negative:candidate_error_count" in errs


def test_build_error_reduction_metrics_treats_truthy_non_boolean_check_pass_as_failed() -> None:
    payload = build_error_reduction_metrics(
        run_id="rid-check-truthy",
        parsed={"checks": [{"name": "a", "passed": "true"}]},
        events=[{"event_id": "evt-1", "stage": "finalize", "score": {"passed": True}}],
        skill_nodes=None,
    )
    assert payload["metrics"]["baseline_error_count"] == 1


def test_build_error_reduction_metrics_treats_truthy_non_boolean_finalize_pass_as_failed() -> None:
    payload = build_error_reduction_metrics(
        run_id="rid-finalize-truthy",
        parsed={"checks": [{"name": "a", "passed": False}]},
        events=[{"event_id": "evt-2", "stage": "finalize", "score": {"passed": "true"}}],
        skill_nodes=None,
    )
    assert payload["metrics"]["candidate_error_count"] == 1


def test_validate_error_reduction_metrics_rejects_count_arithmetic_mismatch() -> None:
    payload = {
        "schema": "sde.error_reduction_metrics.v1",
        "schema_version": "1.0",
        "run_id": "rid-arithmetic-mismatch",
        "metrics": {
            "baseline_error_count": 4,
            "candidate_error_count": 1,
            "resolved_error_count": 2,
            "error_reduction_rate": 0.5,
            "net_error_delta": 0.0,
        },
        "execution": {
            "events_processed": 1,
            "finalize_events_processed": 1,
            "malformed_event_rows": 0,
            "strict_boolean_violations": [],
        },
        "evidence": {"traces_ref": "traces.jsonl", "summary_ref": "summary.json"},
    }
    errs = validate_error_reduction_metrics_dict(payload)
    assert "error_reduction_metrics_semantics:resolved_error_count" in errs
    assert "error_reduction_metrics_semantics:error_reduction_rate" in errs
    assert "error_reduction_metrics_semantics:net_error_delta" in errs


def test_build_error_reduction_metrics_no_finalize_events_fail_closed_to_no_improvement() -> None:
    payload = build_error_reduction_metrics(
        run_id="rid-no-finalize",
        parsed={"checks": [{"name": "a", "passed": False}]},
        events=[],
        skill_nodes=None,
    )
    assert payload["metrics"]["baseline_error_count"] == 1
    assert payload["metrics"]["candidate_error_count"] == 1
    assert payload["metrics"]["resolved_error_count"] == 0
    assert payload["metrics"]["error_reduction_rate"] == pytest.approx(0.0)


def test_execute_error_reduction_runtime_detects_malformed_rows() -> None:
    execution = execute_error_reduction_runtime(
        events=[
            {"event_id": "evt-1", "stage": "finalize", "score": {"passed": True}},
            {"stage": "finalize", "score": {"passed": True}},
            {"event_id": "evt-3", "stage": "repair"},
        ]
    )
    assert execution["events_processed"] == 3
    assert execution["finalize_events_processed"] == 1
    assert execution["malformed_event_rows"] == 2


def test_build_error_reduction_metrics_records_boolean_violations() -> None:
    payload = build_error_reduction_metrics(
        run_id="rid-violations",
        parsed={"checks": [{"name": "a", "passed": False}]},
        events=[{"event_id": "evt-bad", "stage": "finalize", "score": {"passed": "yes"}}],
        skill_nodes=None,
    )
    assert payload["execution"]["strict_boolean_violations"] == ["evt-bad"]


def test_validate_error_reduction_metrics_accepts_runtime_rounded_rate() -> None:
    payload = {
        "schema": "sde.error_reduction_metrics.v1",
        "schema_version": "1.0",
        "run_id": "rid-rounded-rate",
        "metrics": {
            "baseline_error_count": 3,
            "candidate_error_count": 2,
            "resolved_error_count": 1,
            "error_reduction_rate": 0.3333,
            "net_error_delta": -1.0,
        },
        "execution": {
            "events_processed": 1,
            "finalize_events_processed": 1,
            "malformed_event_rows": 0,
            "strict_boolean_violations": [],
        },
        "evidence": {"traces_ref": "traces.jsonl", "summary_ref": "summary.json"},
    }
    assert validate_error_reduction_metrics_dict(payload) == []


def test_validate_error_reduction_metrics_rejects_missing_evidence_refs() -> None:
    payload = {
        "schema": "sde.error_reduction_metrics.v1",
        "schema_version": "1.0",
        "run_id": "rid-evidence",
        "metrics": {
            "baseline_error_count": 2,
            "candidate_error_count": 1,
            "resolved_error_count": 1,
            "error_reduction_rate": 0.5,
            "net_error_delta": -1.0,
        },
        "evidence": {"traces_ref": "../traces.jsonl", "summary_ref": ""},
    }
    errs = validate_error_reduction_metrics_dict(payload)
    assert "error_reduction_metrics_evidence_ref:traces_ref" in errs
    assert "error_reduction_metrics_evidence_ref:summary_ref" in errs

