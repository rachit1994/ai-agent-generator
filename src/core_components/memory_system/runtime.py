"""Deterministic memory-system derivation."""

from __future__ import annotations

from typing import Any

from .contracts import MEMORY_SYSTEM_CONTRACT, MEMORY_SYSTEM_SCHEMA_VERSION


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def _to_float(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    return default


def build_memory_system(
    *,
    run_id: str,
    retrieval_bundle: dict[str, Any],
    quality_metrics: dict[str, Any],
    quarantine_rows: list[str],
) -> dict[str, Any]:
    chunks = retrieval_bundle.get("chunks") if isinstance(retrieval_bundle, dict) else []
    retrieval_chunks = len(chunks) if isinstance(chunks, list) else 0
    contradiction_rate = _to_float(quality_metrics.get("contradiction_rate")) if isinstance(quality_metrics, dict) else 1.0
    staleness_hours = _to_float(quality_metrics.get("staleness_p95_hours")) if isinstance(quality_metrics, dict) else 999.0
    quality_score = _clamp01((1.0 - contradiction_rate) * (1.0 if staleness_hours <= 24.0 else 0.5))
    quarantine_count = len([line for line in quarantine_rows if isinstance(line, str) and line.strip()])
    status = "missing"
    if retrieval_chunks > 0 and quality_score >= 0.8 and quarantine_count == 0:
        status = "healthy"
    elif retrieval_chunks > 0:
        status = "degraded"
    return {
        "schema": MEMORY_SYSTEM_CONTRACT,
        "schema_version": MEMORY_SYSTEM_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "metrics": {
            "retrieval_chunks": retrieval_chunks,
            "quarantine_rows": quarantine_count,
            "quality_score": quality_score,
            "contradiction_rate": _clamp01(contradiction_rate),
            "staleness_p95_hours": round(staleness_hours, 4),
        },
        "evidence": {
            "retrieval_bundle_ref": "memory/retrieval_bundle.json",
            "quality_metrics_ref": "memory/quality_metrics.json",
            "quarantine_ref": "memory/quarantine.jsonl",
            "memory_system_ref": "memory/memory_system.json",
        },
    }
