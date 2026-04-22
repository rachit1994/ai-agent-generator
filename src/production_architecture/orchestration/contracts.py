"""Contracts for production orchestration artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PRODUCTION_ORCHESTRATION_CONTRACT = "sde.production_orchestration.v1"
PRODUCTION_ORCHESTRATION_SCHEMA_VERSION = "1.0"
_CANONICAL_EVIDENCE_REFS = {
    "lease_table_ref": "coordination/lease_table.json",
    "shard_map_ref": "orchestration/shard_map.json",
    "orchestration_ref": "orchestration/production_orchestration.json",
}


def _validate_execution(execution: Any) -> list[str]:
    if not isinstance(execution, dict):
        return ["production_orchestration_execution"]
    errs: list[str] = []
    for key in (
        "lease_rows_processed",
        "shard_rows_processed",
        "malformed_lease_rows",
        "malformed_shard_rows",
        "inactive_or_missing_lease_ids",
    ):
        value = execution.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            errs.append(f"production_orchestration_execution_type:{key}")
    return errs


def _expected_status(lease_count: int, active_lease_count: int, shard_count: int) -> str:
    if active_lease_count > 0 and shard_count > 0:
        return "healthy"
    if lease_count > 0 or shard_count > 0:
        return "degraded"
    return "missing"


def _validate_status(status: Any) -> tuple[list[str], str | None]:
    if status not in ("healthy", "degraded", "missing"):
        return (["production_orchestration_status"], None)
    return ([], status)


def _validate_metrics(metrics: Any) -> tuple[list[str], tuple[int, int, int] | None]:
    if not isinstance(metrics, dict):
        return (["production_orchestration_metrics"], None)
    errs: list[str] = []
    values: list[int] = []
    for key in ("lease_count", "active_lease_count", "shard_count"):
        value = metrics.get(key)
        if isinstance(value, bool) or not isinstance(value, int):
            errs.append(f"production_orchestration_metric_type:{key}")
            continue
        if value < 0:
            errs.append(f"production_orchestration_metric_range:{key}")
            continue
        values.append(value)
    if errs:
        return (errs, None)
    lease_count, active_lease_count, shard_count = values
    if active_lease_count > lease_count:
        return (["production_orchestration_active_lease_count_range"], None)
    return ([], (lease_count, active_lease_count, shard_count))


def _validate_evidence(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return ["production_orchestration_evidence"]
    errs: list[str] = []
    for key, expected in _CANONICAL_EVIDENCE_REFS.items():
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"production_orchestration_evidence_ref:{key}")
            continue
        normalized = value.strip()
        if normalized != expected:
            errs.append(f"production_orchestration_evidence_ref:{key}")
            continue
        ref_path = Path(normalized)
        if ref_path.is_absolute() or ".." in ref_path.parts:
            errs.append(f"production_orchestration_evidence_ref:{key}")
    return errs


def validate_production_orchestration_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["production_orchestration_not_object"]
    errs: list[str] = []
    if body.get("schema") != PRODUCTION_ORCHESTRATION_CONTRACT:
        errs.append("production_orchestration_schema")
    if body.get("schema_version") != PRODUCTION_ORCHESTRATION_SCHEMA_VERSION:
        errs.append("production_orchestration_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("production_orchestration_run_id")
    errs.extend(_validate_execution(body.get("execution")))
    status_errs, normalized_status = _validate_status(body.get("status"))
    errs.extend(status_errs)
    metric_errs, values = _validate_metrics(body.get("metrics"))
    errs.extend(metric_errs)
    if values is not None and normalized_status is not None:
        lease_count, active_lease_count, shard_count = values
        if normalized_status != _expected_status(lease_count, active_lease_count, shard_count):
            errs.append("production_orchestration_status_metrics_mismatch")
    errs.extend(_validate_evidence(body.get("evidence")))
    return errs


def validate_production_orchestration_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["production_orchestration_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["production_orchestration_json"]
    return validate_production_orchestration_dict(body)
