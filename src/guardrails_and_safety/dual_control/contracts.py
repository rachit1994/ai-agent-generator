"""Contracts for dual-control runtime evidence artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DUAL_CONTROL_CONTRACT = "sde.dual_control.v1"
DUAL_CONTROL_SCHEMA_VERSION = "1.0"
DUAL_CONTROL_ALLOWED_STATUS = (
    "validated",
    "missing_required_ack",
    "invalid_ack",
)
DUAL_CONTROL_REQUIRED_METRICS = (
    "doc_review_passed",
    "dual_required",
    "ack_present",
    "ack_valid",
    "distinct_actors",
)
DUAL_CONTROL_REQUIRED_EVIDENCE_REFS = (
    "doc_review_ref",
    "dual_control_ack_ref",
    "dual_control_runtime_ref",
)
DUAL_CONTROL_CANONICAL_EVIDENCE_REFS = {
    "doc_review_ref": "program/doc_review.json",
    "dual_control_ack_ref": "program/dual_control_ack.json",
    "dual_control_runtime_ref": "program/dual_control_runtime.json",
}


def _validate_semantics(status: str, metrics: dict[str, Any]) -> list[str]:
    errs: list[str] = []
    ack_valid = metrics.get("ack_valid") is True
    dual_required = metrics.get("dual_required") is True
    ack_present = metrics.get("ack_present") is True
    distinct_actors = metrics.get("distinct_actors") is True
    validated_without_ack_allowed = (not dual_required) and (not ack_present)
    validated_with_ack_allowed = ack_valid and distinct_actors
    if status == "validated" and not (validated_without_ack_allowed or validated_with_ack_allowed):
        errs.append("dual_control_semantics")
    if status == "missing_required_ack" and not (dual_required and not ack_present):
        errs.append("dual_control_semantics")
    if status == "invalid_ack" and not (ack_present and not ack_valid):
        errs.append("dual_control_semantics")
    return errs


def _validate_metrics(metrics: Any) -> tuple[list[str], dict[str, Any] | None]:
    if not isinstance(metrics, dict):
        return ["dual_control_metrics"], None
    errs: list[str] = []
    for key in DUAL_CONTROL_REQUIRED_METRICS:
        if not isinstance(metrics.get(key), bool):
            errs.append(f"dual_control_metric_type:{key}")
    return errs, metrics


def _validate_evidence(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return ["dual_control_evidence"]
    errs: list[str] = []
    for key in DUAL_CONTROL_REQUIRED_EVIDENCE_REFS:
        value = evidence.get(key)
        if not isinstance(value, str) or not value.strip():
            errs.append(f"dual_control_evidence_ref:{key}")
            continue
        normalized = value.strip()
        expected = DUAL_CONTROL_CANONICAL_EVIDENCE_REFS[key]
        if normalized.startswith("/") or ".." in normalized.split("/") or normalized != expected:
            errs.append(f"dual_control_evidence_ref:{key}")
    return errs


def validate_dual_control_dict(body: Any) -> list[str]:
    if not isinstance(body, dict):
        return ["dual_control_not_object"]
    errs: list[str] = []
    if body.get("schema") != DUAL_CONTROL_CONTRACT:
        errs.append("dual_control_schema")
    if body.get("schema_version") != DUAL_CONTROL_SCHEMA_VERSION:
        errs.append("dual_control_schema_version")
    run_id = body.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        errs.append("dual_control_run_id")
    status = body.get("status")
    if status not in DUAL_CONTROL_ALLOWED_STATUS:
        errs.append("dual_control_status")
    metric_errs, metric_dict = _validate_metrics(body.get("metrics"))
    errs.extend(metric_errs)
    evidence = body.get("evidence")
    errs.extend(_validate_evidence(evidence))
    if isinstance(status, str) and metric_dict is not None and isinstance(evidence, dict):
        errs.extend(_validate_semantics(status, metric_dict))
    return errs


def validate_dual_control_path(path: Path) -> list[str]:
    if not path.is_file():
        return ["dual_control_file_missing"]
    try:
        body = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["dual_control_json"]
    return validate_dual_control_dict(body)
