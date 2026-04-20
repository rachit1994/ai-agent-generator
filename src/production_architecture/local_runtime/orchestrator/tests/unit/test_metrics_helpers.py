from __future__ import annotations

import pytest

from guardrails_and_safety.risk_budgets_permission_matrix.risk_budgets.metrics_helpers import (
    metrics_from_events,
    reliability_gate,
)


def test_metrics_from_events_fails_closed_for_malformed_numeric_fields() -> None:
    events = [
        {
            "stage": "finalize",
            "latency_ms": "n/a",
            "estimated_cost_usd": "bad",
            "retry_count": True,
            "score": {"passed": True, "reliability": "oops", "validity": "bad"},
        },
        {
            "stage": "finalize",
            "latency_ms": "42",
            "estimated_cost_usd": "1.5",
            "retry_count": "2",
            "score": {"passed": False, "reliability": "0.9", "validity": "1"},
        },
    ]
    metrics = metrics_from_events(events)
    assert metrics["passRate"] == pytest.approx(0.5)
    assert metrics["reliability"] == pytest.approx(0.45)
    assert metrics["p50Latency"] == 0
    assert metrics["p95Latency"] == 0
    assert metrics["avgCost"] == pytest.approx(0.75)
    assert metrics["validityRate"] == pytest.approx(0.5)
    assert metrics["retryFrequency"] == 1


def test_metrics_from_events_empty_finalize_slice_returns_zero_profile() -> None:
    metrics = metrics_from_events([{"stage": "draft", "latency_ms": 100}])
    assert metrics["passRate"] == 0
    assert metrics["reliability"] == 0
    assert metrics["p50Latency"] == 0
    assert metrics["p95Latency"] == 0
    assert metrics["avgCost"] == 0
    assert metrics["validityRate"] == 0
    assert metrics["retryFrequency"] == 0
    assert reliability_gate(metrics) is False
