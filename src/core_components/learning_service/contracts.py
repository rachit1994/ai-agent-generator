"""Contracts for learning-service artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

LEARNING_SERVICE_CONTRACT = "sde.learning_service.v1"
LEARNING_SERVICE_SCHEMA_VERSION = "1.0"
_FLOAT_TOLERANCE = 1e-4
_CANONICAL_EVIDENCE_REFS = {
    "reflection_bundle_ref": "learning/reflection_bundle.json",
    "canary_report_ref": "learning/canary_report.json",
    "traces_ref": "traces.jsonl",
    "learning_service_ref": "learning/learning_service.json",
}


def _valid_status(status: Any) -> bool:
    return status in ("healthy", "degraded", "insufficient_signal")


def _validate_core_fields(body: dict[str, Any]) -> tuple[list[str], Any]:
    errs: list[str] = []
    if body.get("schema") != LEARNING_SERVICE_CONTRACT:
        errs.append("learning_service_schema")
    if body.get("schema_version") != LEARNING_SERVICE_SCHEMA_VERSION:
        errs.append("learning_service_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("learning_service_run_id")
    mode = body.get("mode")
    if mode not in ("guarded_pipeline", "phased_pipeline", "baseline"):
        errs.append("learning_service_mode")
    status = body.get("status")
    if not _valid_status(status):
        errs.append("learning_service_status")
    return errs, status


def _validate_metric_counts(metrics: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    for key in ("reflection_count", "canary_count", "finalize_rows"):
        value = metrics.get(key)
        if isinstance(value, bool) or not isinstance(value, int):
            errs.append(f"learning_service_metric_type:{key}")
        elif value < 0:
            errs.append(f"learning_service_metric_range:{key}")
    return errs


def _validate_metric_rates(metrics: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    health = metrics.get("health_score")
    if isinstance(health, bool) or not isinstance(health, (int, float)):
        errs.append("learning_service_health_score_type")
    elif float(health) < 0.0 or float(health) > 1.0:
        errs.append("learning_service_health_score_range")
    finalize_pass_rate = metrics.get("finalize_pass_rate")
    if isinstance(finalize_pass_rate, bool) or not isinstance(finalize_pass_rate, (int, float)):
        errs.append("learning_service_finalize_pass_rate_type")
    elif float(finalize_pass_rate) < 0.0 or float(finalize_pass_rate) > 1.0:
        errs.append("learning_service_finalize_pass_rate_range")
    return errs


def _validate_status_semantics(metrics: dict[str, Any], status: Any) -> list[str]:
    reflection_count = metrics.get("reflection_count")
    canary_count = metrics.get("canary_count")
    finalize_rows = metrics.get("finalize_rows")
    health = metrics.get("health_score")
    if not (
        isinstance(reflection_count, int)
        and not isinstance(reflection_count, bool)
        and isinstance(canary_count, int)
        and not isinstance(canary_count, bool)
        and isinstance(finalize_rows, int)
        and not isinstance(finalize_rows, bool)
        and isinstance(health, (int, float))
        and not isinstance(health, bool)
        and _valid_status(status)
    ):
        return []

    errs: list[str] = []
    has_signal = reflection_count > 0 or canary_count > 0 or finalize_rows > 0
    healthy_semantics = reflection_count > 0 and canary_count > 0 and float(health) >= 0.75
    if status == "healthy" and not healthy_semantics:
        errs.append("learning_service_status_semantics:healthy")
    if status == "insufficient_signal" and has_signal:
        errs.append("learning_service_status_semantics:insufficient_signal")
    if status == "degraded" and (not has_signal or healthy_semantics):
        errs.append("learning_service_status_semantics:degraded")
    return errs


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return round(value, 4)


def _validate_metric_semantics(metrics: dict[str, Any]) -> list[str]:
    reflection_count = metrics.get("reflection_count")
    canary_count = metrics.get("canary_count")
    finalize_rows = metrics.get("finalize_rows")
    finalize_pass_rate = metrics.get("finalize_pass_rate")
    health = metrics.get("health_score")
    if not (
        isinstance(reflection_count, int)
        and not isinstance(reflection_count, bool)
        and isinstance(canary_count, int)
        and not isinstance(canary_count, bool)
        and isinstance(finalize_rows, int)
        and not isinstance(finalize_rows, bool)
        and isinstance(finalize_pass_rate, (int, float))
        and not isinstance(finalize_pass_rate, bool)
        and isinstance(health, (int, float))
        and not isinstance(health, bool)
    ):
        return []
    errs: list[str] = []
    if finalize_rows == 0 and abs(float(finalize_pass_rate)) > _FLOAT_TOLERANCE:
        errs.append("learning_service_metric_semantics:finalize_pass_rate")
    signal_density = _clamp01((reflection_count + canary_count) / 10.0)
    expected_health = _clamp01((signal_density * 0.5) + (float(finalize_pass_rate) * 0.5))
    if abs(float(health) - expected_health) > _FLOAT_TOLERANCE:
        errs.append("learning_service_metric_semantics:health_score")
    return errs


def _validate_evidence(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return ["learning_service_evidence"]
    errs: list[str] = []
    for key, expected in _CANONICAL_EVIDENCE_REFS.items():
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"learning_service_evidence_ref:{key}")
            continue
        normalized = value.strip()
        if normalized.startswith("/") or ".." in normalized.split("/") or normalized != expected:
            errs.append(f"learning_service_evidence_ref:{key}")
    return errs


def validate_learning_service_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["learning_service_not_object"]
    errs, status = _validate_core_fields(body)
    metrics = body.get("metrics")
    if not isinstance(metrics, dict):
        errs.append("learning_service_metrics")
    else:
        errs.extend(_validate_metric_counts(metrics))
        errs.extend(_validate_metric_rates(metrics))
        if not errs:
            errs.extend(_validate_metric_semantics(metrics))
        if not errs:
            errs.extend(_validate_status_semantics(metrics, status))
    errs.extend(_validate_evidence(body.get("evidence")))
    return errs


def validate_learning_service_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["learning_service_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["learning_service_json"]
    return validate_learning_service_dict(body)
