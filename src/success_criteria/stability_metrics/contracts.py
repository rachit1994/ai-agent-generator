"""Contracts for stability-metrics artifacts."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

STABILITY_METRICS_CONTRACT = "sde.stability_metrics.v1"
STABILITY_METRICS_SCHEMA_VERSION = "1.0"
_FLOAT_TOLERANCE = 1e-4
_CANONICAL_EVIDENCE_REFS = {
    "traces_ref": "traces.jsonl",
    "stability_metrics_ref": "learning/stability_metrics.json",
}


def _validate_execution(execution: Any) -> list[str]:
    if not isinstance(execution, dict):
        return ["stability_metrics_execution"]
    errs: list[str] = []
    int_fields = ("events_processed", "stable_events_processed", "malformed_event_rows")
    for field in int_fields:
        value = execution.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            errs.append(f"stability_metrics_execution_type:{field}")
    if not isinstance(execution.get("reliability_violations"), list):
        errs.append("stability_metrics_execution_type:reliability_violations")
    return errs


def _validate_status_score_semantics(status: Any, metrics: dict[str, Any]) -> list[str]:
    score = metrics.get("stability_score")
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        return []
    numeric_score = float(score)
    if not math.isfinite(numeric_score):
        return []
    if _status_score_mismatch(status, numeric_score):
        return ["stability_metrics_status_score_mismatch"]
    return []


def _validate_metric_arithmetic_semantics(metrics: dict[str, Any]) -> list[str]:
    finalize_pass_rate = metrics.get("finalize_pass_rate")
    reliability_score = metrics.get("reliability_score")
    retry_pressure = metrics.get("retry_pressure")
    stability_score = metrics.get("stability_score")
    if (
        isinstance(finalize_pass_rate, bool)
        or not isinstance(finalize_pass_rate, (int, float))
        or isinstance(reliability_score, bool)
        or not isinstance(reliability_score, (int, float))
        or isinstance(retry_pressure, bool)
        or not isinstance(retry_pressure, (int, float))
        or isinstance(stability_score, bool)
        or not isinstance(stability_score, (int, float))
    ):
        return []
    expected = round(
        (0.55 * float(finalize_pass_rate))
        + (0.35 * float(reliability_score))
        + (0.10 * (1.0 - float(retry_pressure))),
        4,
    )
    if abs(float(stability_score) - expected) > _FLOAT_TOLERANCE:
        return ["stability_metrics_metric_semantics:stability_score"]
    return []


def _status_score_mismatch(status: Any, score: float) -> bool:
    if status == "stable":
        return score < 0.8
    if status == "degraded":
        return score < 0.55 or score >= 0.8
    if status == "unstable":
        return score >= 0.55
    return False


def _validate_core_fields(body: dict[str, Any]) -> tuple[list[str], Any]:
    errs: list[str] = []
    if body.get("schema") != STABILITY_METRICS_CONTRACT:
        errs.append("stability_metrics_schema")
    if body.get("schema_version") != STABILITY_METRICS_SCHEMA_VERSION:
        errs.append("stability_metrics_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("stability_metrics_run_id")
    status = body.get("status")
    if status not in ("stable", "degraded", "unstable"):
        errs.append("stability_metrics_status")
    return errs, status


def _validate_metric_fields(metrics: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    for key in ("finalize_pass_rate", "reliability_score", "retry_pressure", "stability_score"):
        value = metrics.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errs.append(f"stability_metrics_metric_type:{key}")
            continue
        numeric = float(value)
        if not math.isfinite(numeric):
            errs.append(f"stability_metrics_metric_finite:{key}")
            continue
        if numeric < 0.0 or numeric > 1.0:
            errs.append(f"stability_metrics_metric_range:{key}")
    return errs


def _validate_evidence(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return ["stability_metrics_evidence"]
    errs: list[str] = []
    for key, expected in _CANONICAL_EVIDENCE_REFS.items():
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"stability_metrics_evidence_ref:{key}")
            continue
        normalized = value.strip()
        if normalized.startswith("/") or ".." in normalized.split("/") or normalized != expected:
            errs.append(f"stability_metrics_evidence_ref:{key}")
    return errs


def validate_stability_metrics_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["stability_metrics_not_object"]
    errs, status = _validate_core_fields(body)
    errs.extend(_validate_execution(body.get("execution")))
    metrics = body.get("metrics")
    if not isinstance(metrics, dict):
        errs.append("stability_metrics_metrics")
        return errs
    errs.extend(_validate_metric_fields(metrics))
    errs.extend(_validate_evidence(body.get("evidence")))
    if not errs:
        errs.extend(_validate_metric_arithmetic_semantics(metrics))
    if not errs:
        errs.extend(_validate_status_score_semantics(status, metrics))
    return errs


def validate_stability_metrics_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["stability_metrics_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["stability_metrics_json"]
    return validate_stability_metrics_dict(body)
