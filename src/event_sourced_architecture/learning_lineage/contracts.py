"""Contracts for learning-lineage artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

LEARNING_LINEAGE_CONTRACT = "sde.learning_lineage.v1"
LEARNING_LINEAGE_SCHEMA_VERSION = "1.0"
_ALLOWED_MODES = {"baseline", "guarded_pipeline", "phased_pipeline"}
_ALLOWED_STATUS = {"aligned", "partial", "broken"}
_EVIDENCE_REFS = {
    "replay_manifest_ref": "replay_manifest.json",
    "event_store_ref": "event_store/run_events.jsonl",
    "reflection_bundle_ref": "learning/reflection_bundle.json",
    "learning_lineage_ref": "learning/learning_lineage.json",
}


def _expected_status(total_passed: int) -> str:
    if total_passed == 3:
        return "aligned"
    if total_passed >= 2:
        return "partial"
    return "broken"


def _coerced_check_values(checks: dict[str, Any]) -> tuple[bool, bool, bool] | None:
    values = (
        checks.get("manifest_has_chain_root"),
        checks.get("event_store_present"),
        checks.get("reflection_linked"),
    )
    if not all(isinstance(value, bool) for value in values):
        return None
    return values[0], values[1], values[2]


def _validate_status_semantics(body: dict[str, Any]) -> list[str]:
    checks = body.get("checks")
    coverage = body.get("coverage")
    status = body.get("status")
    if (
        not isinstance(checks, dict)
        or not isinstance(coverage, (int, float))
        or isinstance(coverage, bool)
        or not isinstance(status, str)
    ):
        return []
    coerced_checks = _coerced_check_values(checks)
    if coerced_checks is None:
        return []
    total_passed = sum(1 for value in coerced_checks if value is True)
    derived_coverage = total_passed / 3.0
    errs: list[str] = []
    if abs(float(coverage) - derived_coverage) > 1e-9:
        errs.append("learning_lineage_coverage_semantics")
    expected_status = _expected_status(total_passed)
    if status != expected_status:
        errs.append("learning_lineage_status_semantics")
    return errs


def _validate_evidence(body: dict[str, Any]) -> list[str]:
    evidence = body.get("evidence")
    if not isinstance(evidence, dict):
        return ["learning_lineage_evidence"]
    errs: list[str] = []
    for key, expected_ref in _EVIDENCE_REFS.items():
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"learning_lineage_evidence_missing:{key}")
        elif value != expected_ref:
            errs.append(f"learning_lineage_evidence_ref:{key}")
    return errs


def _validate_core_fields(body: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    if body.get("schema") != LEARNING_LINEAGE_CONTRACT:
        errs.append("learning_lineage_schema")
    if body.get("schema_version") != LEARNING_LINEAGE_SCHEMA_VERSION:
        errs.append("learning_lineage_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("learning_lineage_run_id")
    mode = body.get("mode")
    if mode not in _ALLOWED_MODES:
        errs.append("learning_lineage_mode")
    status = body.get("status")
    if status not in _ALLOWED_STATUS:
        errs.append("learning_lineage_status")
    return errs


def _validate_checks(checks: Any) -> list[str]:
    if not isinstance(checks, dict):
        return ["learning_lineage_checks"]
    errs: list[str] = []
    for key in ("manifest_has_chain_root", "event_store_present", "reflection_linked"):
        if not isinstance(checks.get(key), bool):
            errs.append(f"learning_lineage_check_type:{key}")
    return errs


def _validate_coverage(coverage: Any) -> list[str]:
    if isinstance(coverage, bool) or not isinstance(coverage, (int, float)):
        return ["learning_lineage_coverage_type"]
    if float(coverage) < 0.0 or float(coverage) > 1.0:
        return ["learning_lineage_coverage_range"]
    return []


def validate_learning_lineage_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["learning_lineage_not_object"]
    errs = _validate_core_fields(body)
    errs.extend(_validate_checks(body.get("checks")))
    errs.extend(_validate_coverage(body.get("coverage")))
    errs.extend(_validate_status_semantics(body))
    errs.extend(_validate_evidence(body))
    return errs


def validate_learning_lineage_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["learning_lineage_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["learning_lineage_json"]
    return validate_learning_lineage_dict(body)
