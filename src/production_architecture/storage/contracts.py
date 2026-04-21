"""Contracts for storage architecture artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

STORAGE_ARCHITECTURE_CONTRACT = "sde.storage_architecture.v1"
STORAGE_ARCHITECTURE_SCHEMA_VERSION = "1.0"
STORAGE_BOUNDARY_ID = "storage"
STORAGE_CONTRACT_ERROR_PREFIX = "storage_contract:"


def validate_storage_architecture_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["storage_architecture_not_object"]
    errs: list[str] = []
    if body.get("schema") != STORAGE_ARCHITECTURE_CONTRACT:
        errs.append("storage_architecture_schema")
    if body.get("schema_version") != STORAGE_ARCHITECTURE_SCHEMA_VERSION:
        errs.append("storage_architecture_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("storage_architecture_run_id")
    mode = body.get("mode")
    if not isinstance(mode, str) or not mode.strip():
        errs.append("storage_architecture_mode")
    status = body.get("status")
    if status not in ("consistent", "degraded", "inconsistent"):
        errs.append("storage_architecture_status")
    projections = body.get("projections")
    if not isinstance(projections, dict):
        errs.append("storage_architecture_projections")
        return errs
    cov = projections.get("coverage")
    if isinstance(cov, bool) or not isinstance(cov, (int, float)):
        errs.append("storage_architecture_projections_coverage_type")
    elif float(cov) < 0.0 or float(cov) > 1.0:
        errs.append("storage_architecture_projections_coverage_range")
    required_paths_count = projections.get("required_paths_count")
    present_paths_count = projections.get("present_paths_count")
    if isinstance(required_paths_count, bool) or not isinstance(required_paths_count, int):
        errs.append("storage_architecture_projections_required_paths_count_type")
    elif required_paths_count < 0:
        errs.append("storage_architecture_projections_required_paths_count_range")
    if isinstance(present_paths_count, bool) or not isinstance(present_paths_count, int):
        errs.append("storage_architecture_projections_present_paths_count_type")
    elif present_paths_count < 0:
        errs.append("storage_architecture_projections_present_paths_count_range")
    elif isinstance(required_paths_count, int) and present_paths_count > required_paths_count:
        errs.append("storage_architecture_projections_present_paths_count_exceeds_required")
    vector_memory = body.get("vector_memory")
    if not isinstance(vector_memory, dict):
        errs.append("storage_architecture_vector_memory")
    consistency = body.get("consistency")
    if not isinstance(consistency, dict):
        errs.append("storage_architecture_consistency")
        consistency = {}
    trace_digest_matches = consistency.get("trace_digest_matches_event_payload")
    run_id_alignment_ok = consistency.get("run_id_alignment_ok")
    if not isinstance(trace_digest_matches, bool):
        errs.append("storage_architecture_consistency_trace_digest_matches_event_payload_type")
    if not isinstance(run_id_alignment_ok, bool):
        errs.append("storage_architecture_consistency_run_id_alignment_ok_type")
    if status == "consistent" and (
        trace_digest_matches is not True
        or run_id_alignment_ok is not True
        or not isinstance(cov, (int, float))
        or isinstance(cov, bool)
        or float(cov) < 1.0
    ):
        errs.append("storage_architecture_consistency_status_mismatch")
    if status == "inconsistent" and run_id_alignment_ok is True:
        errs.append("storage_architecture_inconsistent_requires_run_id_mismatch")
    return errs


def validate_storage_architecture_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["storage_architecture_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["storage_architecture_json"]
    return validate_storage_architecture_dict(body)

