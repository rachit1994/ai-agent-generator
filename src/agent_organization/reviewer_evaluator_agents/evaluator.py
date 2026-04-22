"""Evaluator authority and payload validation."""

from __future__ import annotations

from typing import Any

from .contracts import (
    REVIEW_FINDING_REQUIRED_KEYS,
    REVIEW_FINDING_SEVERITIES,
    REVIEW_STATUSES,
)

REVIEW_SCHEMA = "1.1"
REQUIRED_REVIEW_KEYS = (
    "schema_version",
    "run_id",
    "status",
    "reasons",
    "required_fixes",
    "gate_snapshot",
    "artifact_manifest",
    "review_findings",
    "completed_at",
)


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_review_payload_contract(review: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_REVIEW_KEYS:
        if key not in review:
            errors.append(f"missing_review_key:{key}")
    if review.get("schema_version") != REVIEW_SCHEMA:
        errors.append("invalid_review_schema_version")
    if not _is_non_empty_string(review.get("run_id")):
        errors.append("invalid_review_run_id")
    if str(review.get("status") or "") not in REVIEW_STATUSES:
        errors.append("invalid_review_status")
    for key in ("reasons", "required_fixes"):
        value = review.get(key)
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            errors.append(f"invalid_{key}")
    completed_at = review.get("completed_at")
    if not isinstance(completed_at, str) or not completed_at.strip():
        errors.append("invalid_completed_at")
    findings = review.get("review_findings")
    if not isinstance(findings, list):
        return errors + ["review_findings_not_list"]
    for idx, item in enumerate(findings):
        if not isinstance(item, dict):
            errors.append(f"review_finding_not_object:{idx}")
            continue
        for key in REVIEW_FINDING_REQUIRED_KEYS:
            if key not in item:
                errors.append(f"review_finding_missing_key:{idx}:{key}")
        sev = str(item.get("severity") or "").lower()
        if sev not in REVIEW_FINDING_SEVERITIES:
            errors.append(f"review_finding_invalid_severity:{idx}:{sev}")
        for key in ("code", "message", "evidence_ref"):
            if not _is_non_empty_string(item.get(key)):
                errors.append(f"review_finding_invalid_field:{idx}:{key}")
    return errors


def is_review_pass_evaluator_eligible(review: dict[str, Any]) -> bool:
    # Fail closed: pass-eligibility requires a contract-valid review payload.
    if validate_review_payload_contract(review):
        return False
    if str(review.get("status") or "") != "completed_review_pass":
        return False
    findings = review.get("review_findings")
    if not isinstance(findings, list):
        return False
    for item in findings:
        if not isinstance(item, dict):
            return False
        if str(item.get("severity") or "").lower() == "blocker":
            return False
    return True


def validate_reviewer_evaluator_gate(review: dict[str, Any]) -> list[str]:
    errors = validate_review_payload_contract(review)
    if review.get("status") == "completed_review_pass" and not is_review_pass_evaluator_eligible(review):
        errors.append("review_pass_not_evaluator_eligible")
    return errors
