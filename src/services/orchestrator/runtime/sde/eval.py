from __future__ import annotations

from collections import Counter, defaultdict
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


def root_cause_distribution(events: Iterable[dict]) -> dict[str, int]:
    finals = [e for e in events if e.get("stage") == "finalize"]
    counts: Counter[str] = Counter()
    for event in finals:
        reason = ((event.get("metadata") or {}).get("failure_reason")) or "unknown_failure"
        counts[str(reason)] += 1
    return dict(counts)


def stage_latency_breakdown(events: Iterable[dict]) -> dict[str, int]:
    totals: defaultdict[str, int] = defaultdict(int)
    for event in events:
        stage = str(event.get("stage", "unknown"))
        totals[stage] += int(event.get("latency_ms", 0) or 0)
    return dict(totals)


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


def strict_gate_decision(
    baseline_metrics: dict,
    guarded_metrics: dict,
    *,
    roi_base_case: float,
    pass_threshold_points: float = 15.0,
    reliability_threshold_points: float = 15.0,
    max_latency_overhead_percent: float = 25.0,
) -> dict:
    pass_delta_points = (guarded_metrics["passRate"] - baseline_metrics["passRate"]) * 100
    reliability_delta_points = (guarded_metrics["reliability"] - baseline_metrics["reliability"]) * 100
    baseline_p50 = baseline_metrics.get("p50Latency", 0)
    latency_delta_percent = 0.0 if baseline_p50 == 0 else ((guarded_metrics["p50Latency"] - baseline_p50) / baseline_p50) * 100
    checks = {
        "passRateDelta": pass_delta_points >= pass_threshold_points,
        "reliabilityDelta": reliability_delta_points >= reliability_threshold_points,
        "latencyOverhead": latency_delta_percent <= max_latency_overhead_percent,
        "incrementalRoiBaseCase": roi_base_case > 0,
    }
    if all(checks.values()):
        decision = "continue_and_scale"
    elif checks["passRateDelta"] or checks["reliabilityDelta"]:
        decision = "continue_constrained"
    else:
        decision = "stop"
    return {
        "decision": decision,
        "checks": checks,
        "metrics": {
            "passRateDeltaPoints": pass_delta_points,
            "reliabilityDeltaPoints": reliability_delta_points,
            "medianLatencyDeltaPercent": latency_delta_percent,
            "incrementalRoiBaseCase": roi_base_case,
        },
        "thresholds": {
            "passRateDeltaPoints": pass_threshold_points,
            "reliabilityDeltaPoints": reliability_threshold_points,
            "maxLatencyOverheadPercent": max_latency_overhead_percent,
            "incrementalRoiBaseCase": 0.0,
        },
    }
