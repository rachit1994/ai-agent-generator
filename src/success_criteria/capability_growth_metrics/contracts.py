"""Contracts for capability growth metrics artifacts."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

CAPABILITY_GROWTH_METRICS_CONTRACT = "sde.capability_growth_metrics.v1"
CAPABILITY_GROWTH_METRICS_SCHEMA_VERSION = "1.0"
_METRIC_KEYS = (
    "capability_growth_rate",
    "capability_stability_rate",
    "promotion_readiness_delta",
    "growth_confidence",
)


def _validate_execution(execution: Any) -> list[str]:
    if not isinstance(execution, dict):
        return ["capability_growth_metrics_execution"]
    errs: list[str] = []
    int_fields = (
        "events_processed",
        "growth_events_processed",
        "malformed_event_rows",
        "skill_node_count",
    )
    for field in int_fields:
        value = execution.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            errs.append(f"capability_growth_metrics_execution_type:{field}")
    if not isinstance(execution.get("reliability_violations"), list):
        errs.append("capability_growth_metrics_execution_type:reliability_violations")
    return errs


def _metric_range_error(key: str, num: float) -> str | None:
    if key == "promotion_readiness_delta":
        if num < -1.0 or num > 1.0:
            return f"capability_growth_metrics_metric_range:{key}"
        return None
    if num < 0.0 or num > 1.0:
        return f"capability_growth_metrics_metric_range:{key}"
    return None


def _validate_metric_values(metrics: Any) -> tuple[list[str], dict[str, float] | None]:
    if not isinstance(metrics, dict):
        return (["capability_growth_metrics_metrics"], None)
    errs: list[str] = []
    numeric: dict[str, float] = {}
    for key in _METRIC_KEYS:
        value = metrics.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errs.append(f"capability_growth_metrics_metric_type:{key}")
            continue
        num = float(value)
        if not math.isfinite(num):
            errs.append(f"capability_growth_metrics_metric_non_finite:{key}")
            continue
        range_err = _metric_range_error(key, num)
        if range_err is not None:
            errs.append(range_err)
            continue
        numeric[key] = round(num, 4)
    return (errs, numeric if not errs else None)


def _validate_evidence_refs(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return ["capability_growth_metrics_evidence"]
    errs: list[str] = []
    for key in ("traces_ref", "skill_nodes_ref"):
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"capability_growth_metrics_evidence_ref:{key}")
    return errs


def _validate_metric_coherence(metrics: dict[str, float]) -> list[str]:
    capability_growth_rate = metrics["capability_growth_rate"]
    capability_stability_rate = metrics["capability_stability_rate"]
    promotion_readiness_delta = metrics["promotion_readiness_delta"]
    growth_confidence = metrics["growth_confidence"]
    expected_delta = round(capability_growth_rate - 0.5, 4)
    expected_confidence = round(
        (0.7 * capability_stability_rate) + (0.3 * capability_growth_rate),
        4,
    )
    errs: list[str] = []
    if promotion_readiness_delta != expected_delta:
        errs.append("capability_growth_metrics_metric_incoherent:promotion_readiness_delta")
    if growth_confidence != expected_confidence:
        errs.append("capability_growth_metrics_metric_incoherent:growth_confidence")
    return errs


def validate_capability_growth_metrics_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["capability_growth_metrics_not_object"]
    errs: list[str] = []
    if body.get("schema") != CAPABILITY_GROWTH_METRICS_CONTRACT:
        errs.append("capability_growth_metrics_schema")
    if body.get("schema_version") != CAPABILITY_GROWTH_METRICS_SCHEMA_VERSION:
        errs.append("capability_growth_metrics_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("capability_growth_metrics_run_id")
    errs.extend(_validate_execution(body.get("execution")))
    metric_errs, numeric_metrics = _validate_metric_values(body.get("metrics"))
    errs.extend(metric_errs)
    errs.extend(_validate_evidence_refs(body.get("evidence")))
    if not errs and numeric_metrics is not None:
        errs.extend(_validate_metric_coherence(numeric_metrics))
    return errs


def validate_capability_growth_metrics_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["capability_growth_metrics_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["capability_growth_metrics_json"]
    return validate_capability_growth_metrics_dict(body)

