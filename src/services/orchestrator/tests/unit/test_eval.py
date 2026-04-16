from agent_mvp.eval import aggregate_metrics, verdict_for


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
    assert metrics["passRate"] == 0.5
    assert metrics["p50Latency"] == 10


def test_verdict_supported() -> None:
    baseline = aggregate_metrics([event("baseline", False, 10), event("baseline", False, 10)])
    guarded = aggregate_metrics([event("guarded_pipeline", True, 12), event("guarded_pipeline", True, 12)])
    assert verdict_for(baseline, guarded) == "supported"
