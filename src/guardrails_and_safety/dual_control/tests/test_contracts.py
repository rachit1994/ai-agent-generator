from __future__ import annotations

from guardrails_and_safety.dual_control.contracts import (
    DUAL_CONTROL_CONTRACT,
    DUAL_CONTROL_SCHEMA_VERSION,
    validate_dual_control_dict,
)


def _valid_payload() -> dict[str, object]:
    return {
        "schema": DUAL_CONTROL_CONTRACT,
        "schema_version": DUAL_CONTROL_SCHEMA_VERSION,
        "run_id": "rid-contract",
        "status": "validated",
        "metrics": {
            "doc_review_passed": True,
            "dual_required": False,
            "ack_present": True,
            "ack_valid": True,
            "distinct_actors": True,
        },
        "evidence": {
            "doc_review_ref": "program/doc_review.json",
            "dual_control_ack_ref": "program/dual_control_ack.json",
            "dual_control_runtime_ref": "program/dual_control_runtime.json",
        },
    }


def test_contract_rejects_validated_with_invalid_ack_metric() -> None:
    payload = _valid_payload()
    payload["metrics"] = {**payload["metrics"], "ack_valid": False}
    errs = validate_dual_control_dict(payload)
    assert "dual_control_semantics" in errs


def test_contract_rejects_missing_required_ack_with_ack_present() -> None:
    payload = _valid_payload()
    payload["status"] = "missing_required_ack"
    payload["metrics"] = {
        **payload["metrics"],
        "dual_required": True,
        "ack_present": True,
        "ack_valid": False,
    }
    errs = validate_dual_control_dict(payload)
    assert "dual_control_semantics" in errs


def test_contract_rejects_invalid_ack_without_ack_or_requirement() -> None:
    payload = _valid_payload()
    payload["status"] = "invalid_ack"
    payload["metrics"] = {
        **payload["metrics"],
        "dual_required": False,
        "ack_present": False,
        "ack_valid": False,
    }
    errs = validate_dual_control_dict(payload)
    assert "dual_control_semantics" in errs


def test_contract_rejects_missing_or_blank_evidence_refs() -> None:
    payload = _valid_payload()
    payload["evidence"] = {
        "doc_review_ref": "",
        "dual_control_runtime_ref": "program/dual_control_runtime.json",
    }
    errs = validate_dual_control_dict(payload)
    assert "dual_control_evidence_ref:doc_review_ref" in errs
    assert "dual_control_evidence_ref:dual_control_ack_ref" in errs
