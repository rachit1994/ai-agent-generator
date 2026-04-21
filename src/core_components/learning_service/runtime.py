"""Deterministic learning-service derivation."""

from __future__ import annotations

from typing import Any

from .contracts import LEARNING_SERVICE_CONTRACT, LEARNING_SERVICE_SCHEMA_VERSION


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def build_learning_service(
    *,
    run_id: str,
    mode: str,
    reflection_bundle: dict[str, Any],
    canary_report: dict[str, Any],
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    reflections = reflection_bundle.get("reflections") if isinstance(reflection_bundle, dict) else []
    reflection_count = len(reflections) if isinstance(reflections, list) else 0
    canary_items = canary_report.get("rows") if isinstance(canary_report, dict) else []
    canary_count = len(canary_items) if isinstance(canary_items, list) else 0
    finalize_rows = [
        row
        for row in events
        if isinstance(row, dict) and row.get("stage") == "finalize"
    ]
    finalize_pass_rate = _clamp01(
        sum(
            1
            for row in finalize_rows
            if isinstance(row.get("score"), dict) and row.get("score", {}).get("passed") is True
        )
        / max(1, len(finalize_rows))
    )
    signal_density = _clamp01((reflection_count + canary_count) / 10.0)
    health_score = _clamp01((signal_density * 0.5) + (finalize_pass_rate * 0.5))
    status = "insufficient_signal"
    if reflection_count > 0 and canary_count > 0 and health_score >= 0.75:
        status = "healthy"
    elif reflection_count > 0 or canary_count > 0 or len(finalize_rows) > 0:
        status = "degraded"
    return {
        "schema": LEARNING_SERVICE_CONTRACT,
        "schema_version": LEARNING_SERVICE_SCHEMA_VERSION,
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "metrics": {
            "reflection_count": reflection_count,
            "canary_count": canary_count,
            "finalize_rows": len(finalize_rows),
            "finalize_pass_rate": finalize_pass_rate,
            "health_score": health_score,
        },
        "evidence": {
            "reflection_bundle_ref": "learning/reflection_bundle.json",
            "canary_report_ref": "learning/canary_report.json",
            "traces_ref": "traces.jsonl",
            "learning_service_ref": "learning/learning_service.json",
        },
    }
