"""Deterministic online evaluation shadow/canary derivation."""

from __future__ import annotations

from typing import Any

from .online_eval_contracts import OnlineEvalRecord
from .policy_defaults import (
    GATE_ID_ERROR_RATE_DELTA,
    GATE_ID_LATENCY_P95_DELTA_MS,
    GATE_ID_MIN_SAMPLE,
    GATE_ID_QUALITY_DELTA,
    MANDATORY_GATE_IDS,
    MAX_ERROR_RATE_DELTA,
    MAX_LATENCY_P95_DELTA_MS,
    MIN_QUALITY_DELTA,
    MIN_SAMPLE_SIZE,
)

from .contracts import (
    ONLINE_EVALUATION_SHADOW_CANARY_CONTRACT,
    ONLINE_EVALUATION_SHADOW_CANARY_SCHEMA_VERSION,
)

_GATE_REASON_BY_ID = {
    GATE_ID_MIN_SAMPLE: "gate_min_sample_unmet",
    GATE_ID_ERROR_RATE_DELTA: "gate_error_rate_delta_exceeded",
    GATE_ID_LATENCY_P95_DELTA_MS: "gate_latency_p95_delta_exceeded",
    GATE_ID_QUALITY_DELTA: "gate_quality_delta_below_threshold",
}


def _round(value: float) -> float:
    return round(value, 4)


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = pct * (len(ordered) - 1)
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    weight = rank - low
    return ordered[low] + ((ordered[high] - ordered[low]) * weight)


def _rate(passed: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return passed / total


def _gate_order(gate_id: str) -> int:
    return MANDATORY_GATE_IDS.index(gate_id) if gate_id in MANDATORY_GATE_IDS else len(MANDATORY_GATE_IDS)


def build_online_evaluation_shadow_canary(
    *,
    run_id: str,
    online_eval_records: list[OnlineEvalRecord],
    canary_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    sample_size = len(online_eval_records)
    baseline_latencies = [row.baseline_latency_ms for row in online_eval_records]
    candidate_latencies = [row.candidate_latency_ms for row in online_eval_records]
    baseline_successes = sum(1 for row in online_eval_records if row.baseline_outcome)
    candidate_successes = sum(1 for row in online_eval_records if row.candidate_outcome)
    baseline_error_rate = 1.0 - _rate(baseline_successes, sample_size)
    candidate_error_rate = 1.0 - _rate(candidate_successes, sample_size)
    quality_delta = (
        sum(row.candidate_quality - row.baseline_quality for row in online_eval_records) / sample_size
        if sample_size > 0
        else 0.0
    )
    failed_gates: list[str] = []
    min_sample_met = sample_size >= MIN_SAMPLE_SIZE
    if not min_sample_met:
        failed_gates.append(GATE_ID_MIN_SAMPLE)
    error_rate_delta = candidate_error_rate - baseline_error_rate
    if error_rate_delta > MAX_ERROR_RATE_DELTA:
        failed_gates.append(GATE_ID_ERROR_RATE_DELTA)
    latency_p95_delta_ms = _percentile(candidate_latencies, 0.95) - _percentile(baseline_latencies, 0.95)
    if latency_p95_delta_ms > MAX_LATENCY_P95_DELTA_MS:
        failed_gates.append(GATE_ID_LATENCY_P95_DELTA_MS)
    if quality_delta < MIN_QUALITY_DELTA:
        failed_gates.append(GATE_ID_QUALITY_DELTA)
    failed_gates = sorted(failed_gates, key=_gate_order)
    decision_reasons = [_GATE_REASON_BY_ID[gate_id] for gate_id in failed_gates]
    decision = "promote" if not failed_gates else "hold"
    aux_canary_ref = "learning/canary_report.json" if isinstance(canary_report, dict) and canary_report else None
    return {
        "schema": ONLINE_EVALUATION_SHADOW_CANARY_CONTRACT,
        "schema_version": ONLINE_EVALUATION_SHADOW_CANARY_SCHEMA_VERSION,
        "run_id": run_id,
        "decision": {
            "decision": decision,
            "failed_gates": failed_gates,
            "decision_reasons": decision_reasons,
            "min_sample_met": min_sample_met,
        },
        "metrics": {
            "sample_size": sample_size,
            "coverage": _round(_rate(sample_size, sample_size)),
            "baseline_latency_p50_ms": _round(_percentile(baseline_latencies, 0.5)),
            "baseline_latency_p95_ms": _round(_percentile(baseline_latencies, 0.95)),
            "candidate_latency_p50_ms": _round(_percentile(candidate_latencies, 0.5)),
            "candidate_latency_p95_ms": _round(_percentile(candidate_latencies, 0.95)),
            "baseline_error_rate": _round(baseline_error_rate),
            "candidate_error_rate": _round(candidate_error_rate),
            "error_rate_delta": _round(error_rate_delta),
            "latency_p95_delta_ms": _round(latency_p95_delta_ms),
            "quality_delta": _round(quality_delta),
        },
        "evidence": {
            "online_eval_records_ref": "learning/online_eval_records.jsonl",
            "canary_report_ref": aux_canary_ref,
        },
    }
