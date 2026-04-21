"""Deterministic memory-system derivation."""

from __future__ import annotations

import math
from typing import Any

from .contracts import (
    MEMORY_SYSTEM_CONTRACT,
    MEMORY_SYSTEM_EVIDENCE_REFS,
    MEMORY_SYSTEM_HEALTHY_QUALITY_THRESHOLD,
    MEMORY_SYSTEM_SCHEMA_VERSION,
)

_STALE_HOURS_THRESHOLD = 24.0
_STALE_QUALITY_MULTIPLIER = 0.5


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
        out = float(value)
        if math.isnan(out) or math.isinf(out):
            return default
        return out
    return default


def _bounded01_or_default(value: Any, *, default: float) -> float:
    parsed = _to_float(value, default=default)
    if parsed < 0.0 or parsed > 1.0:
        return default
    return parsed


def _non_negative_or_default(value: Any, *, default: float) -> float:
    parsed = _to_float(value, default=default)
    if parsed < 0.0:
        return default
    return parsed


def _quarantine_count(rows: list[str]) -> int:
    count = 0
    for row in rows:
        if isinstance(row, str):
            if row.strip():
                count += 1
            continue
        # Fail closed: malformed quarantine rows still indicate quarantined signal.
        count += 1
    return count


def build_memory_system(
    *,
    run_id: str,
    retrieval_bundle: dict[str, Any],
    quality_metrics: dict[str, Any],
    quarantine_rows: list[str],
) -> dict[str, Any]:
    chunks = retrieval_bundle.get("chunks") if isinstance(retrieval_bundle, dict) else []
    retrieval_chunks = len(chunks) if isinstance(chunks, list) else 0
    contradiction_rate = (
        _bounded01_or_default(quality_metrics.get("contradiction_rate"), default=1.0)
        if isinstance(quality_metrics, dict)
        else 1.0
    )
    staleness_hours = (
        _non_negative_or_default(quality_metrics.get("staleness_p95_hours"), default=999.0)
        if isinstance(quality_metrics, dict)
        else 999.0
    )
    staleness_multiplier = 1.0 if staleness_hours <= _STALE_HOURS_THRESHOLD else _STALE_QUALITY_MULTIPLIER
    quality_score = _clamp01((1.0 - contradiction_rate) * staleness_multiplier)
    if retrieval_chunks == 0:
        quality_score = 0.0
    quarantine_count = _quarantine_count(quarantine_rows)
    status = "missing"
    if (
        retrieval_chunks > 0
        and quality_score >= MEMORY_SYSTEM_HEALTHY_QUALITY_THRESHOLD
        and quarantine_count == 0
    ):
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
            "retrieval_bundle_ref": MEMORY_SYSTEM_EVIDENCE_REFS["retrieval_bundle_ref"],
            "quality_metrics_ref": MEMORY_SYSTEM_EVIDENCE_REFS["quality_metrics_ref"],
            "quarantine_ref": MEMORY_SYSTEM_EVIDENCE_REFS["quarantine_ref"],
            "memory_system_ref": MEMORY_SYSTEM_EVIDENCE_REFS["memory_system_ref"],
        },
    }
