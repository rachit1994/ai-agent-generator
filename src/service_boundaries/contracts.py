"""Contracts for service boundaries artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SERVICE_BOUNDARIES_CONTRACT = "sde.service_boundaries.v1"
SERVICE_BOUNDARIES_SCHEMA_VERSION = "1.0"


def _validate_core_fields(body: dict[str, Any]) -> tuple[list[str], Any]:
    errs: list[str] = []
    if body.get("schema") != SERVICE_BOUNDARIES_CONTRACT:
        errs.append("service_boundaries_schema")
    if body.get("schema_version") != SERVICE_BOUNDARIES_SCHEMA_VERSION:
        errs.append("service_boundaries_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("service_boundaries_run_id")
    mode = body.get("mode")
    if not isinstance(mode, str) or not mode.strip():
        errs.append("service_boundaries_mode")
    status = body.get("status")
    if status not in ("bounded", "boundary_violation"):
        errs.append("service_boundaries_status")
    return errs, status


def _validate_violations(violations: Any) -> tuple[list[str], str]:
    errs: list[str] = []
    expected_status = "bounded"
    if not isinstance(violations, list):
        errs.append("service_boundaries_violations")
        return errs, expected_status
    for row in violations:
        if not isinstance(row, dict):
            errs.append("service_boundaries_violation_type")
            continue
        if not isinstance(row.get("service"), str) or not row.get("service", "").strip():
            errs.append("service_boundaries_violation_service")
        if not isinstance(row.get("missing_path"), str) or not row.get("missing_path", "").strip():
            errs.append("service_boundaries_violation_missing_path")
    if violations:
        expected_status = "boundary_violation"
    return errs, expected_status


def _validate_services(services: Any) -> list[str]:
    if not isinstance(services, dict):
        return ["service_boundaries_services"]
    errs: list[str] = []
    for key in ("orchestrator", "event_store", "memory_system", "learning_service"):
        errs.extend(_validate_single_service(key, services.get(key)))
    return errs


def _validate_single_service(key: str, svc: Any) -> list[str]:
    if not isinstance(svc, dict):
        return [f"service_boundaries_service_type:{key}"]
    errs, typed = _validate_service_shape(key, svc)
    if errs:
        return errs
    _, present_count, required_count, coverage = typed
    expected_coverage = (present_count / required_count) if required_count else 0.0
    if abs(coverage - expected_coverage) > 1e-4:
        return [f"service_boundaries_coverage_mismatch:{key}"]
    return []


def _validate_service_shape(key: str, svc: dict[str, Any]) -> tuple[list[str], tuple[list[str], int, int, float]]:
    owned_paths = svc.get("owned_paths")
    present_count = svc.get("present_count")
    required_count = svc.get("required_count")
    coverage = svc.get("coverage")
    if not isinstance(owned_paths, list) or any(not isinstance(path, str) or not path.strip() for path in owned_paths):
        return [f"service_boundaries_owned_paths:{key}"], ([], 0, 0, 0.0)
    if isinstance(present_count, bool) or not isinstance(present_count, int):
        return [f"service_boundaries_present_count_type:{key}"], ([], 0, 0, 0.0)
    if isinstance(required_count, bool) or not isinstance(required_count, int):
        return [f"service_boundaries_required_count_type:{key}"], ([], 0, 0, 0.0)
    if present_count < 0 or required_count < 0 or present_count > required_count:
        return [f"service_boundaries_count_range:{key}"], ([], 0, 0, 0.0)
    if required_count != len(owned_paths):
        return [f"service_boundaries_required_count_mismatch:{key}"], ([], 0, 0, 0.0)
    if isinstance(coverage, bool) or not isinstance(coverage, (int, float)):
        return [f"service_boundaries_coverage_type:{key}"], ([], 0, 0, 0.0)
    numeric_coverage = float(coverage)
    if numeric_coverage < 0.0 or numeric_coverage > 1.0:
        return [f"service_boundaries_coverage_range:{key}"], ([], 0, 0, 0.0)
    return [], (owned_paths, present_count, required_count, numeric_coverage)


def validate_service_boundaries_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["service_boundaries_not_object"]
    errs, status = _validate_core_fields(body)
    violation_errs, expected_status = _validate_violations(body.get("violations"))
    errs.extend(violation_errs)
    errs.extend(_validate_services(body.get("services")))
    if expected_status != status:
        errs.append("service_boundaries_status_semantics")
    return errs


def validate_service_boundaries_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["service_boundaries_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["service_boundaries_json"]
    return validate_service_boundaries_dict(body)

