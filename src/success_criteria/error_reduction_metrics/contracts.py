"""Contracts for error reduction metrics artifacts."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

ERROR_REDUCTION_METRICS_CONTRACT = "sde.error_reduction_metrics.v1"
ERROR_REDUCTION_METRICS_SCHEMA_VERSION = "1.0"
_FLOAT_TOLERANCE = 1e-9
_REQUIRED_METRICS = (
    "baseline_error_count",
    "candidate_error_count",
    "resolved_error_count",
    "error_reduction_rate",
    "net_error_delta",
)


def _validate_metric_semantics(metrics: Any) -> list[str]:
    if not isinstance(metrics, dict):
        return []
    metric_inputs = _coerce_semantic_inputs(metrics)
    if metric_inputs is None:
        return []
    baseline, candidate, resolved, reduction_rate, net_delta = metric_inputs
    errs: list[str] = []
    expected_resolved = max(0, baseline - candidate)
    errs.extend(_validate_resolved_semantics(resolved, expected_resolved))
    expected_rate = (expected_resolved / baseline) if baseline > 0 else 0.0
    errs.extend(_validate_rate_semantics(float(reduction_rate), expected_rate))
    expected_net_delta = float(candidate - baseline)
    errs.extend(_validate_net_delta_semantics(float(net_delta), expected_net_delta))
    return errs


def _coerce_semantic_inputs(
    metrics: dict[str, Any],
) -> tuple[int, int, int, float, float] | None:
    baseline = metrics.get("baseline_error_count")
    candidate = metrics.get("candidate_error_count")
    resolved = metrics.get("resolved_error_count")
    reduction_rate = metrics.get("error_reduction_rate")
    net_delta = metrics.get("net_error_delta")
    if not _is_non_boolean_int(baseline):
        return None
    if not _is_non_boolean_int(candidate):
        return None
    if not _is_non_boolean_int(resolved):
        return None
    if not _is_non_boolean_number(reduction_rate):
        return None
    if not _is_non_boolean_number(net_delta):
        return None
    return baseline, candidate, resolved, float(reduction_rate), float(net_delta)


def _is_non_boolean_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_non_boolean_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _validate_resolved_semantics(resolved: int, expected_resolved: int) -> list[str]:
    if resolved != expected_resolved:
        return ["error_reduction_metrics_semantics:resolved_error_count"]
    return []


def _validate_rate_semantics(reduction_rate: float, expected_rate: float) -> list[str]:
    if abs(reduction_rate - expected_rate) > _FLOAT_TOLERANCE:
        return ["error_reduction_metrics_semantics:error_reduction_rate"]
    return []


def _validate_net_delta_semantics(net_delta: float, expected_net_delta: float) -> list[str]:
    if abs(net_delta - expected_net_delta) > _FLOAT_TOLERANCE:
        return ["error_reduction_metrics_semantics:net_error_delta"]
    return []


def _validate_metrics(metrics: Any) -> list[str]:
    if not isinstance(metrics, dict):
        return ["error_reduction_metrics_metrics"]
    errs: list[str] = []
    for key in _REQUIRED_METRICS:
        errs.extend(_validate_single_metric(key, metrics.get(key)))
    return errs


def _validate_single_metric(key: str, value: Any) -> list[str]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return [f"error_reduction_metrics_metric_type:{key}"]
    num = float(value)
    if not math.isfinite(num):
        return [f"error_reduction_metrics_metric_finite:{key}"]
    if key.endswith("_count"):
        return _validate_count_metric(key, value)
    if key.endswith("_rate") and (num < 0.0 or num > 1.0):
        return [f"error_reduction_metrics_metric_range:{key}"]
    return []


def _validate_count_metric(key: str, value: Any) -> list[str]:
    errs: list[str] = []
    if not isinstance(value, int):
        return [f"error_reduction_metrics_metric_integral:{key}"]
    if value < 0:
        errs.append(f"error_reduction_metrics_metric_non_negative:{key}")
    return errs


def validate_error_reduction_metrics_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["error_reduction_metrics_not_object"]
    errs: list[str] = []
    if body.get("schema") != ERROR_REDUCTION_METRICS_CONTRACT:
        errs.append("error_reduction_metrics_schema")
    if body.get("schema_version") != ERROR_REDUCTION_METRICS_SCHEMA_VERSION:
        errs.append("error_reduction_metrics_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("error_reduction_metrics_run_id")
    metrics = body.get("metrics")
    errs.extend(_validate_metrics(metrics))
    if not errs:
        errs.extend(_validate_metric_semantics(metrics))
    return errs


def validate_error_reduction_metrics_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["error_reduction_metrics_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["error_reduction_metrics_json"]
    return validate_error_reduction_metrics_dict(body)

