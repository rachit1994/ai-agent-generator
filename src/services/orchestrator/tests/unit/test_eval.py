import pytest

from sde.eval import aggregate_metrics, root_cause_distribution, strict_gate_decision, verdict_for


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
