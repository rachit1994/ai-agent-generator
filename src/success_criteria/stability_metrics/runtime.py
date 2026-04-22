"""Deterministic stability-metrics derivation."""

from __future__ import annotations

import math
from typing import Any

from .contracts import STABILITY_METRICS_CONTRACT, STABILITY_METRICS_SCHEMA_VERSION


def _clamp01(value: float) -> float:
    if not math.isfinite(value):
        return 0.0
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def _finalize_pass_rate(finals: list[dict[str, Any]]) -> float:
    if not finals:
        return 0.0
    passed = sum(
        1 for row in finals
        if isinstance(row.get("score"), dict) and bool(row.get("score", {}).get("passed"))
    )
    return _clamp01(passed / len(finals))


def _collect_reliability_and_retries(events: list[dict[str, Any]]) -> tuple[list[float], int]:
    reliability_values: list[float] = []
    retries = 0
    for row in events:
        score = row.get("score")
        if isinstance(score, dict):
            reliability = score.get("reliability")
            if isinstance(reliability, (int, float)) and not isinstance(reliability, bool):
                numeric_reliability = float(reliability)
                if math.isfinite(numeric_reliability):
                    reliability_values.append(numeric_reliability)
        if row.get("stage") in {"repair", "executor_fix", "verifier_fix"}:
            retries += 1
    return reliability_values, retries


def _valid_stability_event(event: Any) -> bool:
    if not isinstance(event, dict):
        return False
    required = ("event_id", "stage")
    if not all(key in event for key in required):
        return False
    return isinstance(event["stage"], str) and bool(event["stage"].strip())


def execute_stability_runtime(*, events: list[dict[str, Any]]) -> dict[str, Any]:
    stable_events = [event for event in events if _valid_stability_event(event)]
    malformed_event_rows = len(events) - len(stable_events)
    reliability_violations: list[str] = []
    for event in stable_events:
        score = event.get("score")
        if not isinstance(score, dict):
            continue
        reliability = score.get("reliability")
        if reliability is None:
            continue
        if isinstance(reliability, bool) or not isinstance(reliability, (int, float)):
            reliability_violations.append(str(event["event_id"]))
            continue
        numeric_reliability = float(reliability)
        if not math.isfinite(numeric_reliability) or numeric_reliability < 0.0 or numeric_reliability > 1.0:
            reliability_violations.append(str(event["event_id"]))
    return {
        "events_processed": len(events),
        "stable_events_processed": len(stable_events),
        "malformed_event_rows": malformed_event_rows,
        "reliability_violations": reliability_violations,
    }


def build_stability_metrics(
    *,
    run_id: str,
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    execution = execute_stability_runtime(events=events)
    valid_events = [row for row in events if isinstance(row, dict)]
    finals = [row for row in valid_events if row.get("stage") == "finalize"]
    pass_rate = _finalize_pass_rate(finals)
    reliability_values, retries = _collect_reliability_and_retries(valid_events)
    reliability_score = _clamp01(
        (sum(reliability_values) / len(reliability_values)) if reliability_values else 0.0
    )
    retry_pressure = _clamp01(retries / max(1, len(valid_events)))
    stability_score = _clamp01((0.55 * pass_rate) + (0.35 * reliability_score) + (0.10 * (1.0 - retry_pressure)))
    status = "unstable"
    if stability_score >= 0.8:
        status = "stable"
    elif stability_score >= 0.55:
        status = "degraded"
    return {
        "schema": STABILITY_METRICS_CONTRACT,
        "schema_version": STABILITY_METRICS_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "execution": execution,
        "metrics": {
            "finalize_pass_rate": pass_rate,
            "reliability_score": reliability_score,
            "retry_pressure": retry_pressure,
            "stability_score": stability_score,
        },
        "evidence": {
            "traces_ref": "traces.jsonl",
            "stability_metrics_ref": "learning/stability_metrics.json",
        },
    }
