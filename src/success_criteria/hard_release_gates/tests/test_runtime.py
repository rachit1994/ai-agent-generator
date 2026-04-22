from __future__ import annotations

import math

import pytest

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


def test_build_hard_release_gates_fails_closed_on_non_boolean_check_passed() -> None:
    parsed = {
        "checks": [{"name": "shape", "passed": "true"}, {"name": "quality", "passed": True}],
        "hard_stops": [{"id": "HS01", "passed": True}],
    }
    events = [{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}]
    result = build_hard_release_gates(
        run_id="rid-hard-gates", mode="guarded_pipeline", parsed=parsed, events=events
    )
    assert result["scores"]["governance"] == pytest.approx(50.0)
    assert result["gates"]["governance_gate"] is False
    assert result["overall_pass"] is False


def test_build_hard_release_gates_fails_closed_on_non_boolean_finalize_passed() -> None:
    parsed = {
        "checks": [{"name": "shape", "passed": True}, {"name": "quality", "passed": True}],
        "hard_stops": [{"id": "HS01", "passed": True}],
    }
    events = [{"stage": "finalize", "score": {"passed": "true", "reliability": 0.9}}]
    result = build_hard_release_gates(
        run_id="rid-hard-gates", mode="guarded_pipeline", parsed=parsed, events=events
    )
    assert result["scores"]["delivery"] == pytest.approx(0.0)
    assert result["gates"]["delivery_gate"] is False
    assert result["overall_pass"] is False


def test_build_hard_release_gates_fails_closed_on_non_boolean_hard_stop_passed() -> None:
    parsed = {
        "checks": [{"name": "shape", "passed": True}, {"name": "quality", "passed": True}],
        "hard_stops": [{"id": "HS01", "passed": "true"}],
    }
    events = [{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}]
    result = build_hard_release_gates(
        run_id="rid-hard-gates", mode="guarded_pipeline", parsed=parsed, events=events
    )
    assert result["failed_hard_stop_ids"] == ["HS01"]
    assert result["overall_pass"] is False


def test_validate_hard_release_gates_rejects_gate_score_mismatch() -> None:
    parsed = {
        "checks": [{"name": "shape", "passed": True}, {"name": "quality", "passed": True}],
        "hard_stops": [{"id": "HS01", "passed": True}],
    }
    events = [{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}]
    payload = build_hard_release_gates(
        run_id="rid-hard-gates", mode="guarded_pipeline", parsed=parsed, events=events
    )
    payload["gates"]["reliability_gate"] = False
    errs = validate_hard_release_gates_dict(payload)
    assert "hard_release_gates_gate_score_mismatch:reliability" in errs


def test_validate_hard_release_gates_rejects_status_coherence_mismatch() -> None:
    parsed = {
        "checks": [{"name": "shape", "passed": True}, {"name": "quality", "passed": True}],
        "hard_stops": [{"id": "HS01", "passed": True}],
    }
    events = [{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}]
    payload = build_hard_release_gates(
        run_id="rid-hard-gates", mode="guarded_pipeline", parsed=parsed, events=events
    )
    payload["overall_pass"] = False
    payload["validation_ready"] = True
    errs = validate_hard_release_gates_dict(payload)
    assert "hard_release_gates_overall_pass_mismatch" in errs
    assert "hard_release_gates_validation_ready_mismatch" in errs


def test_validate_hard_release_gates_rejects_invalid_evidence() -> None:
    parsed = {
        "checks": [{"name": "shape", "passed": True}, {"name": "quality", "passed": True}],
        "hard_stops": [{"id": "HS01", "passed": True}],
    }
    events = [{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}]
    payload = build_hard_release_gates(
        run_id="rid-hard-gates", mode="guarded_pipeline", parsed=parsed, events=events
    )
    payload["evidence"]["summary_ref"] = "../summary.json"
    payload["evidence"]["traces_ref"] = ""
    errs = validate_hard_release_gates_dict(payload)
    assert "hard_release_gates_evidence_ref:summary_ref" in errs
    assert "hard_release_gates_evidence_ref:traces_ref" in errs


def test_validate_hard_release_gates_rejects_non_finite_scores() -> None:
    parsed = {
        "checks": [{"name": "shape", "passed": True}, {"name": "quality", "passed": True}],
        "hard_stops": [{"id": "HS01", "passed": True}],
    }
    events = [{"stage": "finalize", "score": {"passed": True, "reliability": 0.9}}]
    payload = build_hard_release_gates(
        run_id="rid-hard-gates", mode="guarded_pipeline", parsed=parsed, events=events
    )
    payload["scores"]["reliability"] = math.nan
    errs = validate_hard_release_gates_dict(payload)
    assert "hard_release_gates_score_finite:reliability" in errs
