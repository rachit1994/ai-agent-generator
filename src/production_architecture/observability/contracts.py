"""Contracts for production observability artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PRODUCTION_OBSERVABILITY_CONTRACT = "sde.production_observability.v1"
PRODUCTION_OBSERVABILITY_SCHEMA_VERSION = "1.0"
PRODUCTION_OBSERVABILITY_EVIDENCE_REFS = {
    "traces_ref": "traces.jsonl",
    "orchestration_ref": "orchestration.jsonl",
    "run_log_ref": "run.log",
    "observability_ref": "observability/production_observability.json",
}


def _validate_execution(execution: Any) -> list[str]:
    if not isinstance(execution, dict):
        return ["production_observability_execution"]
    errs: list[str] = []
    for key in (
        "signals_processed",
        "trace_rows_observed",
        "orchestration_rows_observed",
        "run_log_lines_observed",
    ):
        value = execution.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            errs.append(f"production_observability_execution_type:{key}")
    if not isinstance(execution.get("missing_signal_sources"), list):
        errs.append("production_observability_execution_type:missing_signal_sources")
    return errs


def _validate_metric_count(metrics: dict[str, Any], key: str) -> tuple[str | None, int | None]:
    value = metrics.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        return (f"production_observability_metric_type:{key}", None)
    if value < 0:
        return (f"production_observability_metric_range:{key}", None)
    return (None, value)


def _expected_status(trace_rows: int, orchestration_rows: int, run_log_lines: int) -> str:
    has_core = trace_rows > 0 and orchestration_rows > 0
    has_log = run_log_lines > 0
    if has_core and has_log:
        return "healthy"
    if has_core or has_log:
        return "degraded"
    return "missing"


def _validate_metrics(metrics: Any) -> tuple[list[str], tuple[int, int, int] | None]:
    if not isinstance(metrics, dict):
        return (["production_observability_metrics"], None)
    errs: list[str] = []
    trace_err, trace_rows = _validate_metric_count(metrics, "trace_rows")
    orchestration_err, orchestration_rows = _validate_metric_count(metrics, "orchestration_rows")
    run_log_err, run_log_lines = _validate_metric_count(metrics, "run_log_lines")
    for err in (trace_err, orchestration_err, run_log_err):
        if err is not None:
            errs.append(err)
    if errs:
        return (errs, None)
    return ([], (trace_rows or 0, orchestration_rows or 0, run_log_lines or 0))


def _validate_evidence(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return ["production_observability_evidence"]
    errs: list[str] = []
    for key, expected_ref in PRODUCTION_OBSERVABILITY_EVIDENCE_REFS.items():
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"production_observability_evidence_ref:{key}")
        elif value != expected_ref:
            errs.append(f"production_observability_evidence_ref_mismatch:{key}")
    return errs


def validate_production_observability_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["production_observability_not_object"]
    errs: list[str] = []
    if body.get("schema") != PRODUCTION_OBSERVABILITY_CONTRACT:
        errs.append("production_observability_schema")
    if body.get("schema_version") != PRODUCTION_OBSERVABILITY_SCHEMA_VERSION:
        errs.append("production_observability_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("production_observability_run_id")
    mode = body.get("mode")
    if mode not in ("guarded_pipeline", "phased_pipeline", "baseline"):
        errs.append("production_observability_mode")
    status = body.get("status")
    if status not in ("healthy", "degraded", "missing"):
        errs.append("production_observability_status")
    errs.extend(_validate_execution(body.get("execution")))
    metric_errs, counts = _validate_metrics(body.get("metrics"))
    errs.extend(metric_errs)
    errs.extend(_validate_evidence(body.get("evidence")))
    if counts is not None and status in ("healthy", "degraded", "missing"):
        trace_rows, orchestration_rows, run_log_lines = counts
        expected_status = _expected_status(trace_rows, orchestration_rows, run_log_lines)
        if status != expected_status:
            errs.append("production_observability_status_metrics_mismatch")
    return errs


def validate_production_observability_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["production_observability_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["production_observability_json"]
    return validate_production_observability_dict(body)
