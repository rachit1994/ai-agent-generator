"""Contracts for feature 01 local non-regression gate."""

from __future__ import annotations

from typing import Any

LOCAL_NON_REGRESSION_SCHEMA = "sde.scale.feature_01.local_non_regression.v1"
LOCAL_NON_REGRESSION_SCHEMA_VERSION = "1.0"
_MODES = {"ci", "preflight"}
_STATUSES = {"pass", "fail"}
_CANONICAL_REFS = {
    "baseline_ref": "data/local_non_regression/baseline.json",
    "benchmarks_ref": "data/local_non_regression/benchmarks.json",
    "history_ref": "data/local_non_regression/trend_history.jsonl",
}


def _validate_metric_map(value: Any, key: str) -> list[str]:
    if not isinstance(value, dict):
        return [f"local_non_regression_{key}"]
    errors: list[str] = []
    for name, metric in value.items():
        if not isinstance(name, str) or not name.strip():
            errors.append(f"local_non_regression_{key}_metric_name")
        if isinstance(metric, bool) or not isinstance(metric, (int, float)):
            errors.append(f"local_non_regression_{key}_metric_value")
    return errors


def validate_local_non_regression_report_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["local_non_regression_not_object"]
    errors: list[str] = []
    if body.get("schema") != LOCAL_NON_REGRESSION_SCHEMA:
        errors.append("local_non_regression_schema")
    if body.get("schema_version") != LOCAL_NON_REGRESSION_SCHEMA_VERSION:
        errors.append("local_non_regression_schema_version")
    if body.get("mode") not in _MODES:
        errors.append("local_non_regression_mode")
    if body.get("status") not in _STATUSES:
        errors.append("local_non_regression_status")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errors.append("local_non_regression_run_id")
    errors.extend(_validate_metric_map(body.get("current"), "current"))
    errors.extend(_validate_metric_map(body.get("baseline"), "baseline"))
    refs = body.get("evidence")
    if not isinstance(refs, dict):
        return [*errors, "local_non_regression_evidence"]
    for key, expected in _CANONICAL_REFS.items():
        if refs.get(key) != expected:
            errors.append(f"local_non_regression_evidence_ref:{key}")
    return errors

