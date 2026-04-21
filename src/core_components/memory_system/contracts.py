"""Contracts for memory-system artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MEMORY_SYSTEM_CONTRACT = "sde.memory_system.v1"
MEMORY_SYSTEM_SCHEMA_VERSION = "1.0"
MEMORY_SYSTEM_ALLOWED_STATUSES = ("healthy", "degraded", "missing")
MEMORY_SYSTEM_EVIDENCE_REFS = {
    "retrieval_bundle_ref": "memory/retrieval_bundle.json",
    "quality_metrics_ref": "memory/quality_metrics.json",
    "quarantine_ref": "memory/quarantine.jsonl",
    "memory_system_ref": "memory/memory_system.json",
}
MEMORY_SYSTEM_HEALTHY_QUALITY_THRESHOLD = 0.8
_FLOAT_ZERO_TOLERANCE = 1e-9


def _is_valid_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_valid_float(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_core_fields(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    for key in ("schema", "schema_version", "run_id", "status", "metrics", "evidence"):
        if key not in body:
            errs.append(f"memory_system_missing_key:{key}")
    if body.get("schema") != MEMORY_SYSTEM_CONTRACT:
        errs.append("memory_system_schema")
    if body.get("schema_version") != MEMORY_SYSTEM_SCHEMA_VERSION:
        errs.append("memory_system_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("memory_system_run_id")
    status = body.get("status")
    if status not in MEMORY_SYSTEM_ALLOWED_STATUSES:
        errs.append("memory_system_status")
    return errs


def _validate_metric_schema(metrics: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    for key in (
        "retrieval_chunks",
        "quarantine_rows",
        "quality_score",
        "contradiction_rate",
        "staleness_p95_hours",
    ):
        if key not in metrics:
            errs.append(f"memory_system_metric_missing:{key}")
    for key in ("retrieval_chunks", "quarantine_rows"):
        value = metrics.get(key)
        if not _is_valid_int(value):
            errs.append(f"memory_system_metric_type:{key}")
        elif value < 0:
            errs.append(f"memory_system_metric_range:{key}")
    quality_score = metrics.get("quality_score")
    if not _is_valid_float(quality_score):
        errs.append("memory_system_quality_score_type")
    elif float(quality_score) < 0.0 or float(quality_score) > 1.0:
        errs.append("memory_system_quality_score_range")
    contradiction_rate = metrics.get("contradiction_rate")
    if not _is_valid_float(contradiction_rate):
        errs.append("memory_system_contradiction_rate_type")
    elif float(contradiction_rate) < 0.0 or float(contradiction_rate) > 1.0:
        errs.append("memory_system_contradiction_rate_range")
    staleness_p95_hours = metrics.get("staleness_p95_hours")
    if not _is_valid_float(staleness_p95_hours):
        errs.append("memory_system_staleness_p95_hours_type")
    elif float(staleness_p95_hours) < 0.0:
        errs.append("memory_system_staleness_p95_hours_range")
    return errs


def _validate_status_semantics(status: Any, metrics: dict[str, Any]) -> list[str]:
    retrieval_chunks = metrics.get("retrieval_chunks")
    quarantine_rows = metrics.get("quarantine_rows")
    quality_score = metrics.get("quality_score")
    if not (
        _is_valid_int(retrieval_chunks)
        and _is_valid_int(quarantine_rows)
        and _is_valid_float(quality_score)
        and status in MEMORY_SYSTEM_ALLOWED_STATUSES
    ):
        return []
    numeric_quality_score = float(quality_score)
    is_healthy = (
        retrieval_chunks > 0
        and numeric_quality_score >= MEMORY_SYSTEM_HEALTHY_QUALITY_THRESHOLD
        and quarantine_rows == 0
    )
    errs: list[str] = []
    if status == "healthy" and not is_healthy:
        errs.append("memory_system_status_semantics:healthy")
    if status == "missing" and retrieval_chunks != 0:
        errs.append("memory_system_status_semantics:missing")
    if status == "missing" and abs(numeric_quality_score) > _FLOAT_ZERO_TOLERANCE:
        errs.append("memory_system_status_semantics:missing_quality_score")
    if status == "degraded" and (is_healthy or retrieval_chunks == 0):
        errs.append("memory_system_status_semantics:degraded")
    return errs


def _validate_evidence(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return ["memory_system_evidence"]
    errs: list[str] = []
    for key, expected_ref in MEMORY_SYSTEM_EVIDENCE_REFS.items():
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"memory_system_evidence_missing:{key}")
        elif value != expected_ref:
            errs.append(f"memory_system_evidence_ref:{key}")
    return errs


def validate_memory_system_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["memory_system_not_object"]
    errs = _validate_core_fields(body)
    metrics = body.get("metrics")
    if not isinstance(metrics, dict):
        errs.append("memory_system_metrics")
    else:
        errs.extend(_validate_metric_schema(metrics))
        errs.extend(_validate_status_semantics(body.get("status"), metrics))
    errs.extend(_validate_evidence(body.get("evidence")))
    return errs


def validate_memory_system_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["memory_system_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["memory_system_json"]
    return validate_memory_system_dict(body)
