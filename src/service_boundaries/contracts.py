"""Contracts for service boundaries artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SERVICE_BOUNDARIES_CONTRACT = "sde.service_boundaries.v1"
SERVICE_BOUNDARIES_SCHEMA_VERSION = "1.0"


def validate_service_boundaries_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["service_boundaries_not_object"]
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
    services = body.get("services")
    if not isinstance(services, dict):
        errs.append("service_boundaries_services")
        return errs
    for key in ("orchestrator", "event_store", "memory_system", "learning_service"):
        svc = services.get(key)
        if not isinstance(svc, dict):
            errs.append(f"service_boundaries_service_type:{key}")
            continue
        cov = svc.get("coverage")
        if isinstance(cov, bool) or not isinstance(cov, (int, float)):
            errs.append(f"service_boundaries_coverage_type:{key}")
            continue
        if float(cov) < 0.0 or float(cov) > 1.0:
            errs.append(f"service_boundaries_coverage_range:{key}")
    return errs


def validate_service_boundaries_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["service_boundaries_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["service_boundaries_json"]
    return validate_service_boundaries_dict(body)

