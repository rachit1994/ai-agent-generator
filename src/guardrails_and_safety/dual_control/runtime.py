"""Deterministic dual-control runtime derivation."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .contracts import DUAL_CONTROL_CONTRACT, DUAL_CONTROL_SCHEMA_VERSION


def _dual_required(doc_review: dict[str, Any]) -> bool:
    block = doc_review.get("dual_control")
    if block is None:
        return False
    if not isinstance(block, dict):
        return True
    required = block.get("required")
    if not isinstance(required, bool):
        return True
    return required


def _ack_valid(ack: dict[str, Any]) -> tuple[bool, bool]:
    if not isinstance(ack, dict):
        return False, False
    if ack.get("schema_version") != "1.0":
        return False, False
    actor_a = ack.get("implementor_actor_id")
    actor_b = ack.get("independent_reviewer_actor_id")
    if not isinstance(actor_a, str) or not isinstance(actor_b, str):
        return False, False
    a = actor_a.strip()
    b = actor_b.strip()
    distinct_actors = bool(a and b and a != b)
    acked_at = ack.get("acknowledged_at")
    acked_at_ok = False
    if isinstance(acked_at, str) and acked_at.strip():
        normalized = acked_at.strip()
        if normalized.endswith("Z"):
            normalized = f"{normalized[:-1]}+00:00"
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            acked_at_ok = False
        else:
            acked_at_ok = parsed.utcoffset() is not None and parsed.utcoffset().total_seconds() == 0
    return distinct_actors and acked_at_ok, distinct_actors


def build_dual_control_runtime(
    *,
    run_id: str,
    doc_review: dict[str, Any],
    dual_control_ack: dict[str, Any],
) -> dict[str, Any]:
    normalized_doc_review = doc_review if isinstance(doc_review, dict) else {}
    normalized_ack = dual_control_ack if isinstance(dual_control_ack, dict) else {}
    doc_review_passed = normalized_doc_review.get("passed") is True
    dual_required = _dual_required(normalized_doc_review)
    ack_present = bool(normalized_ack)
    ack_valid, distinct_actors = _ack_valid(normalized_ack) if ack_present else (False, False)
    status = "validated"
    if dual_required and not ack_present:
        status = "missing_required_ack"
    elif (dual_required or ack_present) and not ack_valid:
        status = "invalid_ack"
    return {
        "schema": DUAL_CONTROL_CONTRACT,
        "schema_version": DUAL_CONTROL_SCHEMA_VERSION,
        "run_id": run_id,
        "status": status,
        "metrics": {
            "doc_review_passed": doc_review_passed,
            "dual_required": dual_required,
            "ack_present": ack_present,
            "ack_valid": ack_valid,
            "distinct_actors": distinct_actors,
        },
        "evidence": {
            "doc_review_ref": "program/doc_review.json",
            "dual_control_ack_ref": "program/dual_control_ack.json",
            "dual_control_runtime_ref": "program/dual_control_runtime.json",
        },
    }
