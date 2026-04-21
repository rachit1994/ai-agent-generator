"""Deterministic online evaluation shadow/canary derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    ONLINE_EVALUATION_SHADOW_CANARY_CONTRACT,
    ONLINE_EVALUATION_SHADOW_CANARY_SCHEMA_VERSION,
)


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def _finalize_pass_rate(events: list[dict[str, Any]]) -> float:
    finals = [row for row in events if isinstance(row, dict) and row.get("stage") == "finalize"]
    if not finals:
        return 0.0
    passed = 0
    for row in finals:
        score = row.get("score")
        if isinstance(score, dict) and bool(score.get("passed")):
            passed += 1
    return _clamp01(passed / len(finals))


def build_online_evaluation_shadow_canary(
    *,
    run_id: str,
    canary_report: dict[str, Any],
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    shadow_metrics = canary_report.get("shadow_metrics") if isinstance(canary_report, dict) else {}
    if not isinstance(shadow_metrics, dict):
        shadow_metrics = {}
    latency = shadow_metrics.get("latency_p95_ms")
    latency_p95 = float(latency) if isinstance(latency, (int, float)) and not isinstance(latency, bool) else 0.0
    promote = bool(canary_report.get("promote")) if isinstance(canary_report, dict) else False
    finalize_rate = _finalize_pass_rate(events)
    decision = "promote" if promote and finalize_rate >= 0.8 else "hold"
    return {
        "schema": ONLINE_EVALUATION_SHADOW_CANARY_CONTRACT,
        "schema_version": ONLINE_EVALUATION_SHADOW_CANARY_SCHEMA_VERSION,
        "run_id": run_id,
        "decision": decision,
        "metrics": {
            "latency_p95_ms": round(max(0.0, latency_p95), 2),
            "finalize_pass_rate": finalize_rate,
            "promote_flag": promote,
        },
        "evidence": {
            "canary_report_ref": "learning/canary_report.json",
            "shadow_eval_ref": "learning/online_evaluation_shadow_canary.json",
            "traces_ref": "traces.jsonl",
        },
    }
