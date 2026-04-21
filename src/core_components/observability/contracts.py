"""Contracts for core-observability component runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

OBSERVABILITY_COMPONENT_CONTRACT = "sde.observability_component.v1"
OBSERVABILITY_COMPONENT_SCHEMA_VERSION = "1.0"
_ALLOWED_STATUS = {"ready", "degraded"}
_METRIC_KEYS = (
    "has_production_observability",
    "has_run_log",
    "has_traces",
    "has_orchestration_log",
    "all_checks_passed",
)
_EVIDENCE_REFS = {
    "production_observability_ref": "observability/production_observability.json",
    "run_log_ref": "run.log",
    "traces_ref": "traces.jsonl",
    "orchestration_ref": "orchestration.jsonl",
    "component_ref": "observability/component_runtime.json",
}


def _validate_metric_types(metrics: Any) -> tuple[list[str], bool]:
    if not isinstance(metrics, dict):
        return ["observability_component_metrics"], False
    errs: list[str] = []
    for key in _METRIC_KEYS:
        if not isinstance(metrics.get(key), bool):
            errs.append(f"observability_component_metric_type:{key}")
    return errs, not errs


def _validate_metric_consistency(metrics: dict[str, bool], status: Any) -> list[str]:
    errs: list[str] = []
    expected_all_checks_passed = (
        metrics["has_production_observability"]
        and metrics["has_run_log"]
        and metrics["has_traces"]
        and metrics["has_orchestration_log"]
    )
    if metrics["all_checks_passed"] != expected_all_checks_passed:
        errs.append("observability_component_metric_consistency:all_checks_passed")
    if status in _ALLOWED_STATUS:
        expected_status = "ready" if metrics["all_checks_passed"] else "degraded"
        if status != expected_status:
            errs.append("observability_component_status_consistency")
    return errs


def _validate_evidence(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return ["observability_component_evidence"]
    errs: list[str] = []
    for key, expected_ref in _EVIDENCE_REFS.items():
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"observability_component_evidence_ref:{key}")
        elif value != expected_ref:
            errs.append(f"observability_component_evidence_ref_mismatch:{key}")
    return errs


def validate_observability_component_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["observability_component_not_object"]
    errs: list[str] = []
    if body.get("schema") != OBSERVABILITY_COMPONENT_CONTRACT:
        errs.append("observability_component_schema")
    if body.get("schema_version") != OBSERVABILITY_COMPONENT_SCHEMA_VERSION:
        errs.append("observability_component_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("observability_component_run_id")
    status = body.get("status")
    if status not in _ALLOWED_STATUS:
        errs.append("observability_component_status")
    metric_errs, has_required_metric_types = _validate_metric_types(body.get("metrics"))
    errs.extend(metric_errs)
    metrics = body.get("metrics")
    if has_required_metric_types and isinstance(metrics, dict):
        errs.extend(_validate_metric_consistency(metrics, status))
    errs.extend(_validate_evidence(body.get("evidence")))
    return errs


def validate_observability_component_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["observability_component_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["observability_component_json"]
    return validate_observability_component_dict(body)
