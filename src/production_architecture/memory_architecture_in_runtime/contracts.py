"""Contracts for runtime memory-architecture artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MEMORY_ARCHITECTURE_IN_RUNTIME_CONTRACT = "sde.memory_architecture_in_runtime.v1"
MEMORY_ARCHITECTURE_IN_RUNTIME_SCHEMA_VERSION = "1.0"
_EXPECTED_EVIDENCE_REFS = {
    "retrieval_bundle_ref": "memory/retrieval_bundle.json",
    "quality_metrics_ref": "memory/quality_metrics.json",
    "quarantine_ref": "memory/quarantine.jsonl",
    "memory_architecture_ref": "memory/runtime_memory_architecture.json",
}


def _append_execution_errors(execution: Any, errs: list[str]) -> None:
    if not isinstance(execution, dict):
        errs.append("memory_architecture_in_runtime_execution")
        return
    for key in (
        "chunks_processed",
        "quarantine_rows_processed",
        "malformed_chunk_rows",
        "malformed_quarantine_rows",
    ):
        value = execution.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            errs.append(f"memory_architecture_in_runtime_execution_type:{key}")
    if not isinstance(execution.get("missing_quality_fields"), list):
        errs.append("memory_architecture_in_runtime_execution_type:missing_quality_fields")


def _valid_status(status: Any) -> bool:
    return status in ("healthy", "degraded", "missing")


def _validate_core_fields(body: dict[str, Any]) -> tuple[list[str], Any]:
    errs: list[str] = []
    if body.get("schema") != MEMORY_ARCHITECTURE_IN_RUNTIME_CONTRACT:
        errs.append("memory_architecture_in_runtime_schema")
    if body.get("schema_version") != MEMORY_ARCHITECTURE_IN_RUNTIME_SCHEMA_VERSION:
        errs.append("memory_architecture_in_runtime_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("memory_architecture_in_runtime_run_id")
    status = body.get("status")
    if not _valid_status(status):
        errs.append("memory_architecture_in_runtime_status")
    return errs, status


def _append_metric_errors(metrics: dict[str, Any], errs: list[str]) -> None:
    for key in ("retrieval_coverage", "quality_signal", "quarantine_rate", "health_score"):
        value = metrics.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errs.append(f"memory_architecture_in_runtime_metric_type:{key}")
            continue
        numeric = float(value)
        if numeric < 0.0 or numeric > 1.0:
            errs.append(f"memory_architecture_in_runtime_metric_range:{key}")


def _append_evidence_errors(evidence: dict[str, Any], errs: list[str]) -> None:
    for key, expected in _EXPECTED_EVIDENCE_REFS.items():
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"memory_architecture_in_runtime_evidence_type:{key}")
            continue
        if value != expected:
            errs.append(f"memory_architecture_in_runtime_evidence_ref:{key}")


def _append_status_semantics_errors(metrics: dict[str, Any], status: Any, errs: list[str]) -> None:
    health_score = metrics.get("health_score")
    if isinstance(health_score, bool) or not isinstance(health_score, (int, float)) or not _valid_status(status):
        return
    score = float(health_score)
    if status == "healthy" and score < 0.8:
        errs.append("memory_architecture_in_runtime_status_semantics:healthy")
    if status == "degraded" and (score < 0.5 or score >= 0.8):
        errs.append("memory_architecture_in_runtime_status_semantics:degraded")
    if status == "missing" and score >= 0.5:
        errs.append("memory_architecture_in_runtime_status_semantics:missing")


def validate_memory_architecture_in_runtime_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["memory_architecture_in_runtime_not_object"]
    errs, status = _validate_core_fields(body)
    _append_execution_errors(body.get("execution"), errs)
    metrics = body.get("metrics")
    if not isinstance(metrics, dict):
        errs.append("memory_architecture_in_runtime_metrics")
    else:
        _append_metric_errors(metrics, errs)
        if not errs:
            _append_status_semantics_errors(metrics, status, errs)
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        errs.append("memory_architecture_in_runtime_evidence")
    else:
        _append_evidence_errors(evidence, errs)
    return errs


def validate_memory_architecture_in_runtime_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["memory_architecture_in_runtime_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["memory_architecture_in_runtime_json"]
    return validate_memory_architecture_in_runtime_dict(body)
