"""Contracts for deterministic failure-path-artifacts runtime payload."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

FAILURE_PATH_ARTIFACTS_CONTRACT = "sde.failure_path_artifacts.v1"
FAILURE_PATH_ARTIFACTS_SCHEMA_VERSION = "1.0"
_CANONICAL_EVIDENCE_REFS = {
    "summary_ref": "summary.json",
    "replay_manifest_ref": "replay_manifest.json",
    "failure_path_artifacts_ref": "replay/failure_path_artifacts.json",
}


def _validate_checks(checks: Any) -> tuple[list[str], dict[str, bool] | None]:
    if not isinstance(checks, dict):
        return (["failure_path_artifacts_checks"], None)
    errs: list[str] = []
    values: dict[str, bool] = {}
    for key in (
        "summary_present",
        "summary_contract_valid",
        "replay_manifest_present",
        "replay_manifest_contract_valid",
    ):
        value = checks.get(key)
        if not isinstance(value, bool):
            errs.append(f"failure_path_artifacts_check_type:{key}")
            continue
        values[key] = value
    if errs:
        return (errs, None)
    return ([], values)


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
    check_errs, values = _validate_checks(body.get("checks"))
    errs.extend(check_errs)
    errs.extend(_validate_evidence(body.get("evidence")))
    if status == "ok" and values is not None:
        if values["summary_contract_valid"] is not True or values["replay_manifest_contract_valid"] is not True:
            errs.append("failure_path_artifacts_status_ok_requires_valid_contracts")
    return errs


def _validate_evidence(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return ["failure_path_artifacts_evidence"]
    errs: list[str] = []
    for key, expected in _CANONICAL_EVIDENCE_REFS.items():
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"failure_path_artifacts_evidence_ref:{key}")
            continue
        normalized = value.strip()
        if normalized != expected:
            errs.append(f"failure_path_artifacts_evidence_ref:{key}")
            continue
        ref_path = Path(normalized)
        if ref_path.is_absolute() or ".." in ref_path.parts:
            errs.append(f"failure_path_artifacts_evidence_ref:{key}")
    return errs


def validate_failure_path_artifacts_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["failure_path_artifacts_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["failure_path_artifacts_json"]
    return validate_failure_path_artifacts_dict(body)
