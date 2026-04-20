"""Metrics derived from trace events for gates."""

from __future__ import annotations

from typing import Any


def _percentile(values: list[int], p: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    idx = int((len(ordered) - 1) * p)
    return ordered[idx]


def metrics_from_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    finals = [event for event in events if event.get("stage") == "finalize"]
    total = len(finals) or 1
    pass_count = sum(1 for event in finals if event.get("score", {}).get("passed"))
    validity = sum(1 for event in finals if event.get("score", {}).get("validity", 0) >= 1)
    return {
        "passRate": pass_count / total,
        "reliability": sum(event.get("score", {}).get("reliability", 0) for event in finals) / total,
        "p50Latency": _percentile([int(event.get("latency_ms", 0)) for event in finals], 0.5),
        "p95Latency": _percentile([int(event.get("latency_ms", 0)) for event in finals], 0.95),
        "avgCost": sum(float(event.get("estimated_cost_usd", 0)) for event in finals) / total,
        "validityRate": validity / total,
        "retryFrequency": sum(int(event.get("retry_count", 0)) for event in finals) / total,
    }


def reliability_gate(metrics: dict[str, Any]) -> bool:
    return float(metrics.get("reliability", 0)) >= 0.85
