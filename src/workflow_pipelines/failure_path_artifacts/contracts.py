"""Contracts for deterministic failure-path-artifacts runtime payload."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

FAILURE_PATH_ARTIFACTS_CONTRACT = "sde.failure_path_artifacts.v1"
FAILURE_PATH_ARTIFACTS_SCHEMA_VERSION = "1.0"


def validate_failure_path_artifacts_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["failure_path_artifacts_not_object"]
    errs: list[str] = []
    if body.get("schema") != FAILURE_PATH_ARTIFACTS_CONTRACT:
        errs.append("failure_path_artifacts_schema")
    if body.get("schema_version") != FAILURE_PATH_ARTIFACTS_SCHEMA_VERSION:
        errs.append("failure_path_artifacts_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("failure_path_artifacts_run_id")
    status = body.get("status")
    if status not in ("ok", "failed", "partial_failure"):
        errs.append("failure_path_artifacts_status")
    checks = body.get("checks")
    if not isinstance(checks, dict):
        errs.append("failure_path_artifacts_checks")
    else:
        for key in ("summary_present", "summary_contract_valid", "replay_manifest_present", "replay_manifest_contract_valid"):
            if not isinstance(checks.get(key), bool):
                errs.append(f"failure_path_artifacts_check_type:{key}")
    return errs


def validate_failure_path_artifacts_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["failure_path_artifacts_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["failure_path_artifacts_json"]
    return validate_failure_path_artifacts_dict(body)
