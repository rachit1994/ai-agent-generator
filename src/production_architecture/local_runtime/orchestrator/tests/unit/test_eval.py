import pytest

from evaluation_framework.offline_evaluation.sde_eval.eval import (
    aggregate_metrics,
    root_cause_distribution,
    stage_latency_breakdown,
    strict_gate_decision,
    verdict_for,
)


def event(mode: str, passed: bool, latency: int) -> dict:
    return {
        "mode": mode,
        "stage": "finalize",
        "latency_ms": latency,
        "estimated_cost_usd": 0,
        "retry_count": 0,
        "score": {"passed": passed, "reliability": 1 if passed else 0, "validity": 1},
    }


def test_aggregate_metrics() -> None:
    metrics = aggregate_metrics([event("baseline", True, 10), event("baseline", False, 30)])
    assert metrics["passRate"] == pytest.approx(0.5)
    assert metrics["p50Latency"] == 10


def test_verdict_supported() -> None:
    baseline = aggregate_metrics([event("baseline", False, 10), event("baseline", False, 10)])
    guarded = aggregate_metrics([event("guarded_pipeline", True, 12), event("guarded_pipeline", True, 12)])
    assert verdict_for(baseline, guarded) == "supported"


def test_verdict_inconclusive_small_positive_improvement_no_regressions() -> None:
    baseline_events = [event("baseline", True, 10) for _ in range(8)] + [event("baseline", False, 10) for _ in range(12)]
    guarded_events = [event("guarded_pipeline", True, 10) for _ in range(9)] + [
        event("guarded_pipeline", False, 10) for _ in range(11)
    ]
    baseline = aggregate_metrics(baseline_events)
    guarded = aggregate_metrics(guarded_events)
    assert verdict_for(baseline, guarded) == "inconclusive"


def test_root_cause_distribution_reads_finalize_metadata() -> None:
    events = [
        {"stage": "finalize", "metadata": {"failure_reason": "quality_check_fail"}},
        {"stage": "finalize", "metadata": {"failure_reason": "quality_check_fail"}},
        {"stage": "finalize", "metadata": {"failure_reason": "pipeline_timeout"}},
    ]
    assert root_cause_distribution(events) == {"quality_check_fail": 2, "pipeline_timeout": 1}


def test_strict_gate_decision_stop_when_thresholds_fail() -> None:
    baseline = {"passRate": 0.2, "reliability": 0.2, "p50Latency": 100}
    guarded = {"passRate": 0.25, "reliability": 0.25, "p50Latency": 180}
    decision = strict_gate_decision(baseline, guarded, roi_base_case=-1.0)
    assert decision["decision"] == "stop"
    assert decision["checks"]["incrementalRoiBaseCase"] is False


def test_aggregate_metrics_fail_closed_on_malformed_events() -> None:
    metrics = aggregate_metrics(
        [
            "bad_event",
            {"stage": "finalize", "score": [], "latency_ms": "N/A", "estimated_cost_usd": {}, "retry_count": []},
        ]
    )
    assert metrics["passRate"] == 0
    assert metrics["validityRate"] == 0
    assert metrics["reliability"] == 0
    assert metrics["p50Latency"] == 0
    assert metrics["avgCost"] == 0
    assert metrics["retryFrequency"] == 0


def test_root_cause_distribution_uses_unknown_failure_for_malformed_metadata() -> None:
    events = [
        {"stage": "finalize", "metadata": ["bad"]},
        {"stage": "finalize", "metadata": None},
        {"stage": "planning", "metadata": {"failure_reason": "ignored"}},
    ]
    assert root_cause_distribution(events) == {"unknown_failure": 2}


def test_root_cause_distribution_rejects_non_string_failure_reason() -> None:
    events = [
        {"stage": "finalize", "metadata": {"failure_reason": True}},
        {"stage": "finalize", "metadata": {"failure_reason": 404}},
        {"stage": "finalize", "metadata": {"failure_reason": "  "}},
    ]
    assert root_cause_distribution(events) == {"unknown_failure": 3}


def test_stage_latency_breakdown_ignores_malformed_rows() -> None:
    breakdown = stage_latency_breakdown([{"stage": "planning", "latency_ms": 10}, {"stage": "finalize", "latency_ms": "oops"}, 3])
    assert breakdown["planning"] == 10
    assert breakdown["finalize"] == 0
    assert breakdown["unknown"] == 0


def test_verdict_for_fails_closed_on_missing_or_malformed_metrics() -> None:
    assert verdict_for({"passRate": "bad"}, {"avgCost": "bad"}) == "rejected"


def test_strict_gate_decision_fails_closed_on_malformed_or_missing_fields() -> None:
    decision = strict_gate_decision({"passRate": True}, {"reliability": "bad"}, roi_base_case=0)
    assert decision["decision"] == "stop"
    assert decision["checks"]["passRateDelta"] is False
    assert decision["checks"]["reliabilityDelta"] is False


def test_strict_gate_decision_fails_closed_on_malformed_threshold_arguments() -> None:
    baseline = {"passRate": 0.2, "reliability": 0.2, "p50Latency": 100}
    guarded = {"passRate": 0.5, "reliability": 0.5, "p50Latency": 120}
    decision = strict_gate_decision(
        baseline,
        guarded,
        roi_base_case=float("nan"),
        pass_threshold_points=float("nan"),
        reliability_threshold_points=float("nan"),
        max_latency_overhead_percent=float("nan"),
    )
    assert decision["checks"]["incrementalRoiBaseCase"] is False
    assert decision["thresholds"]["passRateDeltaPoints"] == pytest.approx(15.0)
    assert decision["thresholds"]["reliabilityDeltaPoints"] == pytest.approx(15.0)
    assert decision["thresholds"]["maxLatencyOverheadPercent"] == pytest.approx(25.0)
    assert decision["decision"] == "continue_constrained"
