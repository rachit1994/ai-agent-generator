from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Iterable


def _as_dict(value: object) -> dict:
    if isinstance(value, dict):
        return value
    return {}


def _to_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value: object, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(parsed):
        return default
    return parsed


def percentile(values: list[int], p: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    idx = int((len(ordered) - 1) * p)
    return ordered[idx]


def aggregate_metrics(events: Iterable[dict]) -> dict:
    finals = []
    for event in events:
        row = _as_dict(event)
        if row.get("stage") == "finalize":
            finals.append(row)
    total = len(finals) or 1
    pass_count = 0
    validity = 0
    reliability_sum = 0.0
    latencies: list[int] = []
    avg_cost_sum = 0.0
    retry_sum = 0
    for event in finals:
        score = _as_dict(event.get("score"))
        if bool(score.get("passed")):
            pass_count += 1
        if _to_float(score.get("validity")) >= 1:
            validity += 1
        reliability_sum += _to_float(score.get("reliability"))
        latencies.append(_to_int(event.get("latency_ms")))
        avg_cost_sum += _to_float(event.get("estimated_cost_usd"))
        retry_sum += _to_int(event.get("retry_count"))
    return {
        "passRate": pass_count / total,
        "reliability": reliability_sum / total,
        "p50Latency": percentile(latencies, 0.5),
        "p95Latency": percentile(latencies, 0.95),
        "avgCost": avg_cost_sum / total,
        "validityRate": validity / total,
        "retryFrequency": retry_sum / total,
    }


def root_cause_distribution(events: Iterable[dict]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for event in events:
        row = _as_dict(event)
        if row.get("stage") != "finalize":
            continue
        metadata = _as_dict(row.get("metadata"))
        raw_reason = metadata.get("failure_reason")
        if isinstance(raw_reason, str) and raw_reason.strip():
            counts[raw_reason.strip()] += 1
        else:
            counts["unknown_failure"] += 1
    return dict(counts)


def stage_latency_breakdown(events: Iterable[dict]) -> dict[str, int]:
    totals: defaultdict[str, int] = defaultdict(int)
    for event in events:
        row = _as_dict(event)
        stage = str(row.get("stage", "unknown"))
        totals[stage] += _to_int(row.get("latency_ms"))
    return dict(totals)


def verdict_for(baseline: dict, guarded: dict) -> str:
    baseline_pass_rate = _to_float(baseline.get("passRate"))
    guarded_pass_rate = _to_float(guarded.get("passRate"))
    baseline_p50 = _to_int(baseline.get("p50Latency"))
    guarded_p50 = _to_int(guarded.get("p50Latency"))
    baseline_cost = _to_float(baseline.get("avgCost"))
    guarded_cost = _to_float(guarded.get("avgCost"))
    baseline_reliability = _to_float(baseline.get("reliability"))
    guarded_reliability = _to_float(guarded.get("reliability"))
    pass_delta = (guarded_pass_rate - baseline_pass_rate) * 100
    latency_delta = (
        0
        if baseline_p50 == 0
        else ((guarded_p50 - baseline_p50) / baseline_p50) * 100
    )
    latency_regressed = latency_delta > 30
    cost_regressed = guarded_cost > baseline_cost
    reliability_improved = guarded_reliability > baseline_reliability

    if pass_delta >= 10 and reliability_improved and not latency_regressed:
        return "supported"
    if pass_delta > 0 and (latency_regressed or cost_regressed):
        return "partially supported"
    if 0 < pass_delta < 10 and not latency_regressed and not cost_regressed and guarded_reliability >= baseline_reliability:
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
    baseline_pass_rate = _to_float(baseline_metrics.get("passRate"))
    guarded_pass_rate = _to_float(guarded_metrics.get("passRate"))
    baseline_reliability = _to_float(baseline_metrics.get("reliability"))
    guarded_reliability = _to_float(guarded_metrics.get("reliability"))
    baseline_p50 = _to_float(baseline_metrics.get("p50Latency"))
    guarded_p50 = _to_float(guarded_metrics.get("p50Latency"))
    min_pass_delta = _to_float(pass_threshold_points, 15.0)
    min_reliability_delta = _to_float(reliability_threshold_points, 15.0)
    max_latency_overhead = _to_float(max_latency_overhead_percent, 25.0)
    roi = _to_float(roi_base_case)
    pass_delta_points = (guarded_pass_rate - baseline_pass_rate) * 100
    reliability_delta_points = (guarded_reliability - baseline_reliability) * 100
    latency_delta_percent = 0.0 if baseline_p50 == 0 else ((guarded_p50 - baseline_p50) / baseline_p50) * 100
    checks = {
        "passRateDelta": pass_delta_points >= min_pass_delta,
        "reliabilityDelta": reliability_delta_points >= min_reliability_delta,
        "latencyOverhead": latency_delta_percent <= max_latency_overhead,
        "incrementalRoiBaseCase": roi > 0,
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
            "incrementalRoiBaseCase": roi,
        },
        "thresholds": {
            "passRateDeltaPoints": min_pass_delta,
            "reliabilityDeltaPoints": min_reliability_delta,
            "maxLatencyOverheadPercent": max_latency_overhead,
            "incrementalRoiBaseCase": 0.0,
        },
    }
