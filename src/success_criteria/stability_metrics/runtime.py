"""Deterministic stability-metrics derivation."""

from __future__ import annotations

from typing import Any

from .contracts import STABILITY_METRICS_CONTRACT, STABILITY_METRICS_SCHEMA_VERSION


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def build_stability_metrics(
    *,
    run_id: str,
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    finals = [row for row in events if isinstance(row, dict) and row.get("stage") == "finalize"]
    if finals:
        pass_rate = _clamp01(
            sum(
                1 for row in finals
                if isinstance(row.get("score"), dict) and bool(row.get("score", {}).get("passed"))
            )
            / len(finals)
        )
    else:
        pass_rate = 0.0
    reliability_values: list[float] = []
    retries = 0
    for row in events:
        if not isinstance(row, dict):
            continue
        score = row.get("score")
        if isinstance(score, dict):
            reliability = score.get("reliability")
            if isinstance(reliability, (int, float)) and not isinstance(reliability, bool):
                reliability_values.append(float(reliability))
        if row.get("stage") in {"repair", "executor_fix", "verifier_fix"}:
            retries += 1
    reliability_score = _clamp01(
        (sum(reliability_values) / len(reliability_values)) if reliability_values else 0.0
    )
    retry_pressure = _clamp01(retries / max(1, len(events)))
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
