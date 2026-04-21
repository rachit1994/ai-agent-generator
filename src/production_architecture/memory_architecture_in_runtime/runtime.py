"""Deterministic runtime memory-architecture derivation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    MEMORY_ARCHITECTURE_IN_RUNTIME_CONTRACT,
    MEMORY_ARCHITECTURE_IN_RUNTIME_SCHEMA_VERSION,
)


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def build_memory_architecture_in_runtime(
    *,
    run_id: str,
    retrieval_bundle: dict[str, Any],
    quality_metrics: dict[str, Any],
    quarantine_lines: list[str],
) -> dict[str, Any]:
    chunks = retrieval_bundle.get("chunks") if isinstance(retrieval_bundle, dict) else []
    if not isinstance(chunks, list):
        chunks = []
    retrieval_coverage = _clamp01(1.0 if len(chunks) > 0 else 0.0)
    contradiction_rate = quality_metrics.get("contradiction_rate") if isinstance(quality_metrics, dict) else 1.0
    if isinstance(contradiction_rate, bool) or not isinstance(contradiction_rate, (int, float)):
        contradiction_rate = 1.0
    quality_signal = _clamp01(1.0 - float(contradiction_rate))
    quarantine_rate = _clamp01(len(quarantine_lines) / max(1, len(chunks)))
    health_score = _clamp01((0.5 * retrieval_coverage) + (0.4 * quality_signal) + (0.1 * (1.0 - quarantine_rate)))
    status = "missing"
    if health_score >= 0.8:
        status = "healthy"
    elif health_score >= 0.5:
        status = "degraded"
    return {
        "schema": MEMORY_ARCHITECTURE_IN_RUNTIME_CONTRACT,
        "schema_version": MEMORY_ARCHITECTURE_IN_RUNTIME_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "metrics": {
            "retrieval_coverage": retrieval_coverage,
            "quality_signal": quality_signal,
            "quarantine_rate": quarantine_rate,
            "health_score": health_score,
        },
        "evidence": {
            "retrieval_bundle_ref": "memory/retrieval_bundle.json",
            "quality_metrics_ref": "memory/quality_metrics.json",
            "quarantine_ref": "memory/quarantine.jsonl",
            "memory_architecture_ref": "memory/runtime_memory_architecture.json",
        },
    }
