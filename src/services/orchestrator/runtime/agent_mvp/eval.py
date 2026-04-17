from __future__ import annotations

from typing import Iterable


def percentile(values: list[int], p: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    idx = int((len(ordered) - 1) * p)
    return ordered[idx]


def aggregate_metrics(events: Iterable[dict]) -> dict:
    finals = [e for e in events if e.get("stage") == "finalize"]
    total = len(finals) or 1
    pass_count = sum(1 for e in finals if e.get("score", {}).get("passed"))
    validity = sum(1 for e in finals if e.get("score", {}).get("validity", 0) >= 1)
    return {
        "passRate": pass_count / total,
        "reliability": sum(e.get("score", {}).get("reliability", 0) for e in finals) / total,
        "p50Latency": percentile([int(e.get("latency_ms", 0)) for e in finals], 0.5),
        "p95Latency": percentile([int(e.get("latency_ms", 0)) for e in finals], 0.95),
        "avgCost": sum(float(e.get("estimated_cost_usd", 0)) for e in finals) / total,
        "validityRate": validity / total,
        "retryFrequency": sum(int(e.get("retry_count", 0)) for e in finals) / total,
    }


def verdict_for(baseline: dict, guarded: dict) -> str:
    pass_delta = (guarded["passRate"] - baseline["passRate"]) * 100
    latency_delta = (
        0
        if baseline["p50Latency"] == 0
        else ((guarded["p50Latency"] - baseline["p50Latency"]) / baseline["p50Latency"]) * 100
    )
    latency_regressed = latency_delta > 30
    cost_regressed = guarded["avgCost"] > baseline["avgCost"]
    reliability_improved = guarded["reliability"] > baseline["reliability"]

    if pass_delta >= 10 and reliability_improved and not latency_regressed:
        return "supported"
    if pass_delta > 0 and (latency_regressed or cost_regressed):
        return "partially supported"
    if 0 < pass_delta < 10 and not latency_regressed and not cost_regressed and guarded["reliability"] >= baseline["reliability"]:
        return "inconclusive"
    return "rejected"
