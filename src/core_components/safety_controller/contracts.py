"""Contracts for safety-controller runtime artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SAFETY_CONTROLLER_CONTRACT = "sde.safety_controller.v1"
SAFETY_CONTROLLER_SCHEMA_VERSION = "1.0"


def _validate_execution(execution: Any) -> list[str]:
    if not isinstance(execution, dict):
        return ["safety_controller_execution"]
    errs: list[str] = []
    for key in ("hard_stops_processed", "evaluated_hard_stops", "malformed_hard_stop_rows"):
        value = execution.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            errs.append(f"safety_controller_execution_type:{key}")
    if not isinstance(execution.get("non_boolean_hard_stop_passed_ids"), list):
        errs.append("safety_controller_execution_type:non_boolean_hard_stop_passed_ids")
    return errs


def _validate_metrics(metrics: Any) -> tuple[list[str], tuple[bool, bool, bool] | None]:
    if not isinstance(metrics, dict):
        return (["safety_controller_metrics"], None)
    errs: list[str] = []
    values: list[bool] = []
    for key in ("hard_stop_failures", "validation_ready", "policy_bundle_valid"):
        value = metrics.get(key)
        if not isinstance(value, bool):
            errs.append(f"safety_controller_metric_type:{key}")
            continue
        values.append(value)
    if errs:
        return (errs, None)
    return ([], (values[0], values[1], values[2]))


def validate_safety_controller_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["safety_controller_not_object"]
    errs: list[str] = []
    if body.get("schema") != SAFETY_CONTROLLER_CONTRACT:
        errs.append("safety_controller_schema")
    if body.get("schema_version") != SAFETY_CONTROLLER_SCHEMA_VERSION:
        errs.append("safety_controller_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("safety_controller_run_id")
    status = body.get("status")
    if status not in ("allow", "block"):
        errs.append("safety_controller_status")
    errs.extend(_validate_execution(body.get("execution")))
    metric_errs, metric_values = _validate_metrics(body.get("metrics"))
    errs.extend(metric_errs)
    if metric_values is not None and status in ("allow", "block"):
        hard_stop_failures, validation_ready, policy_bundle_valid = metric_values
        expected_policy_bundle_valid = not hard_stop_failures
        if policy_bundle_valid != expected_policy_bundle_valid:
            errs.append("safety_controller_policy_bundle_valid_mismatch")
        expected_status = "allow" if (validation_ready and policy_bundle_valid) else "block"
        if status != expected_status:
            errs.append("safety_controller_status_metrics_mismatch")
    return errs


def validate_safety_controller_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["safety_controller_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["safety_controller_json"]
    return validate_safety_controller_dict(body)
