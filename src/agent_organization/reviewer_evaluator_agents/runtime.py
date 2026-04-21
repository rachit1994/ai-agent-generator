"""Public runtime facade for reviewer/evaluator agents."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .evaluator import (
    is_review_pass_evaluator_eligible,
    validate_review_payload_contract,
    validate_reviewer_evaluator_gate,
)
from .findings import compose_review_findings


def build_reviewer_evaluator_findings(
    output_dir: Path, manifest: list[dict[str, Any]], status: str, reasons: list[str]
) -> list[dict[str, Any]]:
    return compose_review_findings(output_dir, manifest, status, reasons)


def evaluate_review_contract(review: dict[str, Any]) -> dict[str, Any]:
    errors = validate_review_payload_contract(review)
    eligible = is_review_pass_evaluator_eligible(review)
    return {"errors": errors, "evaluator_eligible": eligible, "strict_ok": (not errors and eligible)}


def validate_reviewer_evaluator_review(review: dict[str, Any]) -> list[str]:
    return validate_reviewer_evaluator_gate(review)
