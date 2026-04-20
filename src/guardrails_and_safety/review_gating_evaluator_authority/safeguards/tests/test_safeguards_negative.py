"""Negative-path tests for safeguards leaf module."""

from __future__ import annotations

import pytest

from guardrails_and_safety.review_gating_evaluator_authority.safeguards.safeguards import (
    classify_output_failure,
    validate_structured_output,
    validate_task_payload,
    validate_task_text,
)


def test_validate_task_text_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="invalid_input_empty_task"):
        validate_task_text("   ")


def test_validate_task_payload_rejects_missing_required_keys() -> None:
    with pytest.raises(ValueError, match="invalid_task_payload"):
        validate_task_payload({"taskId": "t1", "difficulty": "simple"})


def test_validate_task_payload_rejects_unknown_difficulty() -> None:
    payload = {
        "taskId": "t1",
        "prompt": "build",
        "expectedChecks": [],
        "difficulty": "hard",
    }
    with pytest.raises(ValueError, match="invalid_task_payload"):
        validate_task_payload(payload)


def test_validate_structured_output_falls_back_for_non_json_text() -> None:
    parsed = validate_structured_output("non-json response")
    assert parsed["answer"] == "non-json response"
    assert parsed["checks"][0]["name"] == "json_schema"
    assert parsed["refusal"] is None


def test_classify_output_failure_contract_parse_error_on_schema_failure() -> None:
    label = classify_output_failure(
        {"answer": "x", "checks": [{"name": "json_schema", "passed": False}], "refusal": None}
    )
    assert label == "contract_parse_error"
