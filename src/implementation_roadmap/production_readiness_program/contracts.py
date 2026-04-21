"""Contracts for production readiness program artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PRODUCTION_READINESS_PROGRAM_CONTRACT = "sde.production_readiness_program.v1"
PRODUCTION_READINESS_PROGRAM_SCHEMA_VERSION = "1.0"
_ALLOWED_MODES = {"baseline", "guarded_pipeline", "phased_pipeline"}
_REQUIRED_CHECK_KEYS = (
    "run_manifest_valid",
    "review_gate_passed",
    "hard_stops_passed",
    "balanced_gates_ready",
    "required_artifacts_present",
    "policy_bundle_valid",
)


def _validate_checks_and_status(checks: Any, status: Any) -> list[str]:
    if not isinstance(checks, dict):
        return ["production_readiness_program_checks"]
    errs: list[str] = []
    for key in _REQUIRED_CHECK_KEYS:
        value = checks.get(key)
        if not isinstance(value, bool):
            errs.append(f"production_readiness_program_check_type:{key}")
    if status in ("ready", "not_ready") and not errs:
        checks_all_passed = all(checks[key] for key in _REQUIRED_CHECK_KEYS)
        expected_status = "ready" if checks_all_passed else "not_ready"
        if status != expected_status:
            errs.append("production_readiness_program_status_checks_mismatch")
        required_artifacts_present = checks["required_artifacts_present"]
        policy_bundle_valid = checks["policy_bundle_valid"]
        if required_artifacts_present != policy_bundle_valid:
            errs.append("production_readiness_program_policy_bundle_mismatch")
    return errs


def validate_production_readiness_program_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["production_readiness_program_not_object"]
    errs: list[str] = []
    if body.get("schema") != PRODUCTION_READINESS_PROGRAM_CONTRACT:
        errs.append("production_readiness_program_schema")
    if body.get("schema_version") != PRODUCTION_READINESS_PROGRAM_SCHEMA_VERSION:
        errs.append("production_readiness_program_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("production_readiness_program_run_id")
    mode = body.get("mode")
    if mode not in _ALLOWED_MODES:
        errs.append("production_readiness_program_mode")
    status = body.get("status")
    if status not in ("ready", "not_ready"):
        errs.append("production_readiness_program_status")
    errs.extend(_validate_checks_and_status(body.get("checks"), status))
    return errs


def validate_production_readiness_program_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["production_readiness_program_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["production_readiness_program_json"]
    return validate_production_readiness_program_dict(body)

